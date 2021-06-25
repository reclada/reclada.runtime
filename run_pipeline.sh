#!/bin/bash

_S3_FILE_URI="$1"
_JOB_ID="$2"
_INPUT_DIR="/mnt/input/${_JOB_ID}"
_OUTPUT_DIR="/mnt/output/${_JOB_ID}"
_BUCKET_NAME="dev-reclada-bucket"

DB_URI_QUOTED=`python3 -c "import urllib.parse; print(urllib.parse.quote('$DB_URI'))"`


aws s3 cp ${_S3_FILE_URI} ${_INPUT_DIR}/input.pdf

python3 -m table_extractor.run run ${_INPUT_DIR}/input.pdf ${_OUTPUT_DIR} --verbose true --paddle_on true

python3 -m bd2reclada ${_OUTPUT_DIR}/input.pdf/document.json ${_OUTPUT_DIR}/output.csv

# psql ${DB_URI_QUOTED} -c "\COPY reclada.staging FROM '${_OUTPUT_DIR}/output.csv' WITH CSV QUOTE ''''"
cat ${_OUTPUT_DIR}/output.csv | psql ${DB_URI_QUOTED} -c "\COPY reclada.staging FROM STDIN WITH CSV QUOTE ''''"

aws s3 cp ${_OUTPUT_DIR} s3://${_BUCKET_NAME}/output/${_JOB_ID} --recursive
