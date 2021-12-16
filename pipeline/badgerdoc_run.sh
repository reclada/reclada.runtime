#!/bin/bash
soure ./error_check.sh

export _S3_FILE_URI="$1"
export _FILE_ID="$2"
export _JOB_ID="$3"
export _S3_OUTPUT_DIR="$4"
export _INPUT_DIR="/mnt/input/${_JOB_ID}"
export _OUTPUT_DIR="/mnt/output/${_JOB_ID}"
export PYTHONPATH="${PYTHONPATH}:${BADGERDOC_REPO_PATH}"
export PYTHONPATH="${PYTHONPATH}:${SCINLP_REPO_PATH}/lite:${SCINLP_REPO_PATH}"

printf "SCRIPT - Begin - Running badgerdoc to process the document %s for pipeline %s\n" _S3_FILE_URI _JOB_ID

printf "STEP 1 - Begin - Parsing DB_URI environment variable\n"
S3_FILE_NAME=`python3 -c "print('$_S3_FILE_URI'.split('/')[-1])"`
printf "STEP 1 - End\n"

printf "STEP 2 - Begin - Restore the pipeline context\n"
source ./get_context.sh
error_check 'ERROR happened during restoring the pipeline context\n'

printf "STEP 3 - Begin - Running badgerdoc \n"
python3 -m table_extractor.run run "${_INPUT_DIR}/${S3_FILE_NAME}" "${_OUTPUT_DIR}" --verbose true --paddle_on true
error_check 'ERROR happened during running badgerdoc\n'
printf "STEP 3 - End\n"

printf "STEP 4 - Begin - Saving the pipeline context\n"
source ./save_context.sh 3
error_check 'ERROR happened during saving the pipeline context\n'
printf "STEP 4 - End\n"

printf "SCRIPT - End\n"