#!/usr/bin/env bash
# Don't run if you don't want your files to die
rm server/database.db
python server/server.py &
sleep 1
python client/client.py localhost:9050
