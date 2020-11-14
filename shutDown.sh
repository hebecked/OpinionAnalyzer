#!/usr/bin/env bash

echo "Shutting down containers & cleaning up: "
docker exec -u postgres postgres pg_ctl stop
docker rm -f postgres
screen -X -S loggingSession quit
screen -wipe
