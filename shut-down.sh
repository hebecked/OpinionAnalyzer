#!/usr/bin/env bash

echo "Shutting down containers & cleaning up: "
docker exec -u postgres postgres pg_ctl stop
docker rm -f postgres dbs-configurator grafana analyzer scraper pgadmin node-exporter prometheus cadvisor alertmanager
docker volume rm opinionanalyzer_grafana_storage
screen -X -S loggingSession quit
screen -wipe
