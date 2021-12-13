#!/bin/bash

function error_check(){
  if [ $? -ne 0 ]
  then
    printf "$1"
    if [[ -n $2 ]]
    then
      # if an error occurred and there was the second parameter of this function
      # then we need to copy the results of the pipeline processing to S3 bucket and stop the pipeline
      aws s3 cp "${_OUTPUT_DIR}" "s3://${AWS_S3_BUCKET_NAME}/output/${_S3_OUTPUT_DIR}" --recursive --sse
    else
      exit 1
    fi
  fi
}


export _S3_FILE_URI="$1"
_FILE_ID="$2"
_JOB_ID="$3"
export _S3_OUTPUT_DIR="$4"
_CUSTOM_TASK="$5"
_PREPROCESS_TASK="$6"
_POSTPROCESS_TASK="$7"
_INPUT_DIR="/mnt/input/${_JOB_ID}"
export _OUTPUT_DIR="/mnt/output/${_JOB_ID}"

export PYTHONPATH="${PYTHONPATH}:${BADGERDOC_REPO_PATH}"
export PYTHONPATH="${PYTHONPATH}:${SCINLP_REPO_PATH}/lite:${SCINLP_REPO_PATH}"

printf "STEP 1 - Begin - Parsing DB_URI environment variable\n"
DB_URI_QUOTED=`python3 -c "import urllib.parse; parsed = urllib.parse.urlparse('$DB_URI'); print('$DB_URI'.replace(parsed.password, urllib.parse.quote(parsed.password)))"`
S3_FILE_NAME=`python3 -c "print('$_S3_FILE_URI'.split('/')[-1])"`
printf "STEP 1 - End\n"

printf "STEP 2 - Begin - Copying files from S3 bucket to local drive\n"
aws s3 cp "${_S3_FILE_URI}" "${_INPUT_DIR}/${S3_FILE_NAME}"
error_check 'ERROR happened during copying files form S3 bucket\n'
printf "STEP 2 - End \n"

if [[ -n $_PREPROCESS_TASK && $_PREPROCESS_TASK != "0" ]]
then
  printf "STEP 3 - Begin - Running a preprocess custom command\n"
  source "$_PREPROCESS_TASK"
  error_check "ERROR happened during preprocessing custom command\n" "copy"
  printf "STEP 3 - End\n"
else
  printf "Preprocessing command is not set. Step 3 is skipped\n"
fi

printf "STEP 4 - Begin - Running badgerdoc \n"
python3 -m table_extractor.run run "${_INPUT_DIR}/${S3_FILE_NAME}" "${_OUTPUT_DIR}" --verbose true --paddle_on true
error_check "ERROR happened during running badgerdoc\n"
printf "STEP 4 - End\n"

printf "STEP 5 - Begin - Copying the results of badgerdoc's work to the S3 bucket\n"
aws s3 cp "${_OUTPUT_DIR}" "s3://${AWS_S3_BUCKET_NAME}/output/${_S3_OUTPUT_DIR}" --recursive --sse
error_check "ERROR happened during copying results to the S3 bucket\n"
printf "STEP 5 - End\n"

printf "STEP 6 - Begin - Starting bd2reclada\n"
python3 -m bd2reclada "${_OUTPUT_DIR}/${S3_FILE_NAME}/document.json" "${_OUTPUT_DIR}/output.csv" "${_FILE_ID}"
error_check "ERROR happened during running bd2reclada\n"
printf "STEP 6 - End\n"

printf "STEP 7 - Begin - Loading data to DB\n"
cat "${_OUTPUT_DIR}/output.csv" | psql ${DB_URI_QUOTED} -c "\COPY reclada.staging FROM STDIN WITH CSV QUOTE ''''"
error_check "ERROR happened during loading data to DB\n"
printf "STEP 7 - End\n"

printf "STEP 8 - Begin - SciNLP processing\n"
python3 -m lite "${_OUTPUT_DIR}/output.csv" "${_OUTPUT_DIR}/nlp_output.csv" "${DB_URI_QUOTED}"
error_check "ERROR happened during SciNLP processing\n" "copy"
printf "STEP 8 - End\n"

printf "STEP 9 - Begin - Loading data to DB\n"
cat "${_OUTPUT_DIR}/nlp_output.csv" | psql ${DB_URI_QUOTED} -c "\COPY reclada.staging FROM STDIN WITH CSV QUOTE ''''"
error_check "ERROR happened during loading data to DB\n"
printf "STEP 9 - End\n"

# On some platform such as DOMINO we need to add an extra step in the pipeline.
# The extra step supplied as 5th parameter and if it exists then
# we need to run it. If it doesn't then we skip this step
if [ -n "$_CUSTOM_TASK" ]
then
  printf "STEP 10 - Begin - Custom task\n"
  source "$_CUSTOM_TASK"
  error_check "ERROR happened during processing custom task\n" "copy"
  printf "STEP 10 - End\n"
fi

if [[ -n $_POSTPROCESS_TASK && $_POSTPROCESS_TASK != "0" ]]
then
  printf "STEP 11 - Begin - Running postprocess custom command\n"
  source "$_POSTPROCESS_TASK"
  error_check "ERROR happened during postprocessing custom command\n" "copy"
  printf "STEP 11 - End\n"
else
  printf "Postprocessing command is not set. Step 11 is skipped\n"
fi

printf "STEP 12 - Begin - Copying result files to the S3 bucket\n"
aws s3 cp "${_OUTPUT_DIR}" "s3://${AWS_S3_BUCKET_NAME}/output/${_S3_OUTPUT_DIR}" --recursive --sse
error_check "ERROR happened during copying results to the S3 bucket\n"
printf "STEP 12 - End\n"
