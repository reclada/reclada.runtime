#!/bin/bash
source ./error_check.sh
export _S3_FILE_URI="$1"
export _FILE_ID="$2"
export _JOB_ID="$3"
export _S3_OUTPUT_DIR="$4"
export _INPUT_DIR="/mnt/input/${_JOB_ID}"
export _OUTPUT_DIR="/mnt/output/${_JOB_ID}"
export PYTHONPATH="${PYTHONPATH}:${BADGERDOC_REPO_PATH}"
export PYTHONPATH="${PYTHONPATH}:${SCINLP_REPO_PATH}/lite:${SCINLP_REPO_PATH}"

printf "STEP 1 - Begin - Restoring the pipeline context\n"
source ./get_context.sh
error_check 'ERROR happened during restoring the pipeline context\n'
printf "STEP 1 - End\n"

printf "STEP 2 - Begin - Parsing DB_URI environment variable\n"
DB_URI_QUOTED=`python3 -c "import urllib.parse; parsed = urllib.parse.urlparse('$DB_URI'); print('$DB_URI'.replace(parsed.password, urllib.parse.quote(parsed.password)))"`
printf "STEP 2 - End\n"

printf "STEP 3 - Begin - Loading data to DB\n"
cat "${_OUTPUT_DIR}/output.csv" | psql ${DB_URI_QUOTED} -c "\COPY reclada.staging FROM STDIN WITH CSV QUOTE ''''"
error_check 'ERROR happened during loading data to DB\n'
printf "STEP 3 - End\n"

printf "STEP 4 - Begin - Saving the pipeline context\n"
source ./save_context.sh 5
error_check 'ERROR happened during saving the pipeline context\n'
printf "STEP 4 - End\n"