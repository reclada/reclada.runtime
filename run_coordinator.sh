#!/bin/bash

cd "$1"
python3 -m srv.coordinator.coordinator -platform DOMINO -database POSTGRESQL -messenger POSTGRESQL -verbose
