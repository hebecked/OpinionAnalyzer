#!/usr/bin/env bash

# Setting credentials to run system
source set-credentials.sh

# Shutting down system if active
./shut-down.sh

# Building project and executing system
docker-compose up -d --build --force-recreate
