#!/bin/bash
source ./pipeline/error_check.sh

export _S3_FILE_URI="$1"
export _FILE_ID="$2"
export _JOB_ID="$3"
export _S3_OUTPUT_DIR="$4"
export _INPUT_DIR="/mnt/input/${_JOB_ID}"
export _OUTPUT_DIR="/mnt/output/${_JOB_ID}"

printf "SCRIPT - Begin - Running the custom task for pipeline %s\n" "${_JOB_ID}"

printf "STEP 1 - Begin - Restoring the pipeline context\n"
source ./pipeline/get_context.sh
error_check 'ERROR happened during restoring the pipeline context\n'
printf "STEP 1 - End\n"

printf "STEP 2 - Begin - Parsing DB_URI environment variable\n"
DB_URI_QUOTED=`python3 -c "import urllib.parse; parsed = urllib.parse.urlparse('$DB_URI'); print('$DB_URI'.replace(parsed.password, urllib.parse.quote(parsed.password)))"`
S3_FILE_NAME=`python3 -c "print('$_S3_FILE_URI'.split('/')[-1])"`
printf "STEP 2 - End\n"

printf "STEP 3 - Begin - Custom task processing\n"
#source "${CUSTOM_REPO_PATH}/custom_task.sh"
error_check 'ERROR happened during processing the custom task\n'
printf "STEP 3 - End\n"

printf "STEP 4 - Begin - Saving the pipeline context\n"
source ./pipeline/save_context.sh 8
error_check 'ERROR happened during saving the pipeline context\n'
printf "STEP 4 - End\n"

printf "SCRIPT - End\n"