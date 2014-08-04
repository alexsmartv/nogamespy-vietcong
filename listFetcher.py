# Copyright (C) 2014 Ondřej Garncarz 
# License: AGPLv3+

from urllib.request import urlopen
from lxml import etree
from subprocess import *

from model import *
import serverFetcher


def getGameSpyList():
	source = urlopen(
		"http://gstadmin.gamespy.net/masterserver/?gamename=vietcong")
	tree = etree.parse(source, parser = etree.HTMLParser())
	rows = tree.xpath("/html/body/form/table/tr")[1:]

	servers = []
	for row in rows:
		servers.append(Server(ip = row[0].text, infoport = int(row[1].text)))
	
	return servers


def getQtrackerList():
	source = urlopen("http://www.qtracker.com/server_list_details.php?game=vietcong")
	lines = source.readlines()
	arr = [str(line, encoding = "utf8").split(":")
		for line in lines if line.strip()]
	return list(map(lambda row: Server(
		ip = row[0],
		infoport = int(row[1])), arr))


def callAluigi():
	with Popen(["./gslist", "-n", "vietcong"], stdout = PIPE, stderr = PIPE) \
			as proc:
		output = proc.stdout.read().decode("ascii")
		arr = [line.split() for line in output.split("\n") if line.strip()]
		return list(map(lambda row: Server(
			ip = row[0],
			infoport = int(row[1])), arr))
	

def fetchNewServers(servers):
	for server in servers:
		if not Server.select().where(Server.ip == server.ip,
				Server.infoport == server.infoport).exists():
			serverFetcher.fetchServer(server)

