#!/usr/bin/bash

python3 -m srv.runner.runner --runner-id="$1" --db-client=POSTGRESQL
