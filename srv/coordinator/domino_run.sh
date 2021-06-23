#!/usr/bin/bash

export POSTGRES_HOST="34.252.72.157"
export POSTGRES_DB="reclada_dev_1"
export POSTGRES_USER="rumyantsev"
export POSTGRES_PASSWORD="LjgPsdert8we8"
export POSTGRES_NOTIFY_CHANNEL="test"

python3 -m srv.coordinator.coordinator -platform DOMINO -database POSTGRESQL -messenger POSTGRESQL