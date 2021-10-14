#!/bin/bash

unset DOMINO_TOKEN_FILE
cd "$1"
python3 -m srv.runner.runner --runner-id="$2" --db-client=POSTGRESQL
