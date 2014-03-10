#!/usr/bin/python
# -*- coding: utf-8 -*-

from subprocess import *
from urllib.request import urlopen
from lxml import etree
import socket
import re
import pygeoip
from peewee import *
from datetime import datetime, timedelta
import configparser

iniFile = "vietcong.ini"
udpTimeout = 4

################################################################################
## DATA RETRIEVAL:

geoip = pygeoip.GeoIP("/usr/share/GeoIP/GeoIP.dat")

def getGameSpyList():
	source = urlopen(
		"http://gstadmin.gamespy.net/masterserver/?gamename=vietcong")
	tree = etree.parse(source, parser = etree.HTMLParser())
	rows = tree.xpath("/html/body/form/table/tr")[1:]

	servers = []
	for row in rows:
		servers.append(Server(ip = row[0].text, infoport = int(row[1].text)))
	
	return servers


def callAluigi():
	with Popen(["./gslist", "-n", "vietcong"], stdout = PIPE, stderr = PIPE,
		cwd = "/home/ondra/skola/vietcong/service/") as proc:
		output = proc.stdout.read().decode("ascii")
		arr = [line.split() for line in output.split("\n") if line.strip()]
		print(list(map(lambda row: {"ip": row[0], "infoport": row[1]}, arr)))
	

def saveGameSpyServers(servers):
	for server in servers:
		if not Server.select().where(Server.ip == server.ip,
				Server.port == server.port).exists():
			server.save()


def getServerInfo(server):
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.settimeout(udpTimeout)
	udp.connect((server.ip, server.infoport))
	udp.send("\\status\\players\\".encode("latin1"))
	data = udp.recv(4096).decode("latin1")
	arr = re.split("\\\\", data)[1:-4]
	return dict(zip(arr[::2], arr[1::2]))


def mergeServerInfo(server, serverInfo):
	server.online = True
	server.offlineSince = None

	server.port = int(serverInfo["hostport"])
	server.password = "password" in serverInfo
	server.dedic = "dedic" in serverInfo
	server.vietnam = "vietnam" in serverInfo
	
	server.country = geoip.country_code_by_addr(server.ip)
	server.countryname = geoip.country_name_by_addr(server.ip)
	
	server.name = serverInfo["hostname"]
	server.mode = serverInfo["gametype"]
	server.mapname = serverInfo["mapname"]
	server.version = (lambda v: v[0] + "." + v[1:])(serverInfo["uver"])
	server.maxplayers = serverInfo["maxplayers"]
	if "hbver" in serverInfo:
		server.hradba = serverInfo["hbver"]
	
	players = []
	for i in range(int(serverInfo["numplayers"])):
		try:
			player = Player(
				name = serverInfo["player_" + str(i)],
				ping = int(serverInfo["ping_" + str(i)]),
				frags = int(serverInfo["frags_" + str(i)]))
			players.append(player)
		except KeyError:
			break
	server.players = players
	server.numplayers = len(players)
	
	server.save()


def getAll():
	servers = getGameSpyList()
	servers2 = []
	for server in servers:
		try:
			mergeServerInfo(server, getServerInfo(server))
			servers2.append(server)
		except Exception:
			pass
	return servers2


################################################################################
## LOCAL DATABASE:

config = configparser.ConfigParser()
config.read(iniFile)
db = MySQLDatabase("vietcong", **config["db"])
db.connect()

class BaseModel(Model):
	class Meta:
		database = db

class Server(BaseModel):
	ip = CharField()
	infoport = IntegerField()
	port = IntegerField()
	
	name = CharField()
	mapname = CharField()
	mode = CharField()
	country = CharField(null = True)
	countryname = CharField(null = True)
	
	version = CharField()
	hradba = CharField(null = True)
	numplayers = IntegerField()
	maxplayers = IntegerField()
	
	password = BooleanField(null = True)
	dedic = BooleanField(null = True)
	vietnam = BooleanField(null = True)
	
	online = BooleanField(default = True)
	onlineSince = DateTimeField(default = datetime.now)
	offlineSince = DateTimeField(null = True)


class Player(BaseModel):
	name = CharField()
	ping = IntegerField()
	frags = IntegerField()
	
	server = ForeignKeyField(Server, related_name = "players",
		on_update = "cascade", on_delete = "cascade")
	
	online = BooleanField(default = True)
	onlineSince = DateTimeField(default = datetime.now)

Server.create_table(True)
Player.create_table(True)


# FIXME: nepřevádět do modelu, již v něm je
def saveServers(servers):
	db.set_autocommit(False)
	Server.update(online = False).execute()
	Player.update(online = False).execute()
	
	for server in servers:
		try:
			serverDb = Server.get((Server.ip == server["ip"]) &
				(Server.port == server["port"]))
			serverDb.online = True
			serverDb.offlineSince = None
			serverDb.mapname = server["mapname"]
			serverDb.mode = server["mode"]
			serverDb.numplayers = server["numplayers"]
			serverDb.maxplayers = server["maxplayers"]
			serverDb.password = server["password"]
			serverDb.vietnam = server["vietnam"]
		except Server.DoesNotExist:
			serverDb = Server(**server)
		serverDb.save()
		if "players" in server:
			for player in server["players"]:
				try:
					playerDb = Player.get((Player.server == serverDb) &
						(Player.name == player["name"]) &
						(Player.online == False))
					playerDb.online = True
					playerDb.frags = player["frags"]
					playerDb.ping = player["ping"]
				except Player.DoesNotExist:
					playerDb = Player(server = serverDb, **player)
				playerDb.save()
	
	Server.update(offlineSince = datetime.now()).where((Server.online == False) &
		(Server.offlineSince >> None)).execute()
	Server.delete().where(datetime.now() - Server.offlineSince >
		timedelta(hours = 1)).execute()
	Player.delete().where(Player.online == False).execute()
	db.commit()


################################################################################
## RUN:

if __name__ == "__main__":
	servers = getAll()
	saveServers(servers)
