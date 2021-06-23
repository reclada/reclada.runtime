#!/usr/bin/bash

cd /repos/badgerdoc_badgerdoc
python3 -m badgerdoc_badgerdoc.table_extractor.run run "$1" "$2"
python3 -m bd2reclada "$2"/document.json "$2"/output.csv
psql target-db \
    -U <admin user> \
    -p <port> \
    -h <DB instance name> \
    -c "\copy source-table from '"$2"/output.csv' with DELIMITER ','"
aws s3 cp "$2" s3://mybucket/output/"$3" --recursive
