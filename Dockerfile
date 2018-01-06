from python:3-slim

run apt-get update && apt-get install -y \
    geoip-database \
    # helpful when developing:
    tree ncdu \
  && rm -rf /var/lib/apt/lists/*

run mkdir /app
workdir /app

copy requirements.txt .
run pip install --no-cache-dir -r requirements.txt

copy . .
# run ./setup.py build  # if `build` dir not copied from the last step, but then `slim` base image can't be used

volume /app/volume
run ln -s /app/volume/settings_local.py nogamespy/settings_local.py

env PYTHONPATH build/lib.linux-x86_64-3.6

expose 27900/udp 28900

## trying to use non-root user:
# run chown -R nobody .
# user nobody
## unfortunately volume still belongs to root then and thus db.sqlite is read-only
