#!/usr/bin/env bash

echo "Shutting down containers & cleaning up: "
docker exec -u postgres postgres pg_ctl stop
docker rm -f postgres dbs-configurator grafana analyzer
screen -X -S loggingSession quit
screen -wipe
