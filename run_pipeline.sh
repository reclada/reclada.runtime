#!/bin/bash

function error_check(){
  if [ $? -ne 0 ]
  then
    printf "$1"
    exit 1
  fi
}


export _S3_FILE_URI="$1"
_FILE_ID="$2"
_JOB_ID="$3"
export _S3_OUTPUT_DIR="$4"
_CUSTOM_TASK="$5"
_INPUT_DIR="/mnt/input/${_JOB_ID}"
export _OUTPUT_DIR="/mnt/output/${_JOB_ID}"

export PYTHONPATH="${PYTHONPATH}:${BADGERDOC_REPO_PATH}"
export PYTHONPATH="${PYTHONPATH}:${SCINLP_REPO_PATH}"

printf "STEP 0 - Begin - Installing bd2reclada\n"
pip install 'git+https://github.com/reclada/SciNLP.git#egg=bd2reclada&subdirectory=src/srv/bd2reclada'
printf "STEP 0 - End\n"

printf "STEP 1 - Begin - Parsing DB_URI environment variable\n"
DB_URI_QUOTED=`python3 -c "import urllib.parse; parsed = urllib.parse.urlparse('$DB_URI'); print('$DB_URI'.replace(parsed.password, urllib.parse.quote(parsed.password)))"`
S3_FILE_NAME=`python3 -c "print('$_S3_FILE_URI'.split('/')[-1])"`
printf "STEP 1 - End\n"

printf "STEP 2 - Begin - Copying files from S3 bucket to local drive\n"
aws s3 cp "${_S3_FILE_URI}" "${_INPUT_DIR}/${S3_FILE_NAME}"
error_check 'ERROR happened during copying files form S3 bucket\n'
printf "STEP 2 - End \n"

printf "STEP 3 - Begin - Running badgerdoc \n"
python3 -m table_extractor.run run "${_INPUT_DIR}/${S3_FILE_NAME}" "${_OUTPUT_DIR}" --verbose true --paddle_on true
error_check "ERROR happened during running badgerdoc\n"
printf "STEP 3 - End\n"

printf "STEP 4 - Begin - Copying the results of badgerdoc's work to the S3 bucket\n"
aws s3 cp "${_OUTPUT_DIR}" "s3://${AWS_S3_BUCKET_NAME}/output/${_S3_OUTPUT_DIR}" --recursive --sse
error_check "ERROR happened during copying results to the S3 bucket\n"
printf "STEP 4 - End\n"

printf "STEP 5 - Begin - Starting bd2reclada\n"
python3 -m bd2reclada "${_OUTPUT_DIR}/${S3_FILE_NAME}/document.json" "${_OUTPUT_DIR}/output.csv" "${_FILE_ID}"
error_check "ERROR happened during running bd2reclada\n"
printf "STEP 5 - End\n"

printf "STEP 6 - Begin - Loading data to DB\n"
cat "${_OUTPUT_DIR}/output.csv" | psql ${DB_URI_QUOTED} -c "\COPY reclada.staging FROM STDIN WITH CSV QUOTE ''''"
error_check "ERROR happened during loading data to DB\n"
printf "STEP 6 - End\n"

printf "STEP 7 - Begin - SciNLP processing\n"
python3 -m lite "${_OUTPUT_DIR}/output.csv" "${_OUTPUT_DIR}/nlp_output.csv"
error_check "ERROR happened during SciNLP processing\n"
printf "STEP 7 - End\n"

printf "STEP 8 - Begin - Loading data to DB\n"
cat "${_OUTPUT_DIR}/nlp_output.csv" | psql ${DB_URI_QUOTED} -c "\COPY reclada.staging FROM STDIN WITH CSV QUOTE ''''"
error_check "ERROR happened during loading data to DB\n"
printf "STEP 8 - End\n"

printf "STEP 9 - Begin - Copying result files to the S3 bucket\n"
aws s3 cp "${_OUTPUT_DIR}" "s3://${AWS_S3_BUCKET_NAME}/output/${_S3_OUTPUT_DIR}" --recursive --sse
error_check "ERROR happened during copying results to the S3 bucket\n"
printf "STEP 9 - End\n"

# On some platform such as DOMINO we need to add an extra step in the pipeline.
# The extra step supplied as 5th parameter and if it exists then
# we need to run it. If it doesn't then we skip this step
if [ -n "$_CUSTOM_TASK" ]
then
  printf "STEP 10 - Begin - Custom task\n"
  source "$_CUSTOM_TASK"
  error_check "ERROR happened during processing custom task\n"
  printf "STEP 10 - End\n"
fi