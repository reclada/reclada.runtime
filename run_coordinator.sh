#!/bin/bash

unset DOMINO_TOKEN_FILE
cd "$1"
python3 -m srv.coordinator.coordinator -platform DOMINO -database POSTGRESQL -messenger POSTGRESQL -verbose
