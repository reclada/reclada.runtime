#!/bin/bash

_S3_FILE_URI="$1"
_JOB_ID="$2"
_INPUT_DIR="/mnt/input/${_JOB_ID}"
_OUTPUT_DIR="/mnt/output/${_JOB_ID}"

# DB_URI_QUOTED=`python3 -c "import urllib.parse; print(urllib.parse.quote('$DB_URI'))"`
# DB_URI_QUOTED=`python3 -c "import urllib.parse; print('$DB_URI'.replace(urllib.parse.urlparse('$DB_URI').password, urllib.parse.quote(urllib.parse.urlparse('$DB_URI').password)))"`
DB_URI_QUOTED=`python3 -c "import urllib.parse; parsed = urllib.parse.urlparse('$DB_URI'); print('$DB_URI'.replace(parsed.password, urllib.parse.quote(parsed.password)))"`


aws s3 cp ${_S3_FILE_URI} ${_INPUT_DIR}/input.pdf

python3 -m table_extractor.run run ${_INPUT_DIR}/input.pdf ${_OUTPUT_DIR} --verbose true --paddle_on true

python3 -m bd2reclada ${_OUTPUT_DIR}/input.pdf/document.json ${_OUTPUT_DIR}/output.csv

# psql ${DB_URI_QUOTED} -c "\COPY reclada.staging FROM '${_OUTPUT_DIR}/output.csv' WITH CSV QUOTE ''''"
cat ${_OUTPUT_DIR}/output.csv | psql ${DB_URI_QUOTED} -c "\COPY reclada.staging FROM STDIN WITH CSV QUOTE ''''"

aws s3 cp ${_OUTPUT_DIR} s3://${AWS_S3_BUCKET_NAME}/output/${_JOB_ID} --recursive
