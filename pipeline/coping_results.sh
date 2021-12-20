#!/bin/bash
source ./pipeline/error_check.sh
export _S3_FILE_URI="$1"
export _FILE_ID="$2"
export _JOB_ID="$3"
export _S3_OUTPUT_DIR="$4"
export _INPUT_DIR="/mnt/input/${_JOB_ID}"
export _OUTPUT_DIR="/mnt/output/${_JOB_ID}"

printf "SCRIPT - Begin - Coping results to S3 bucket for pipeline %s\n" "${_JOB_ID}"

printf "STEP 1 - Begin - Restoring the pipeline context\n"
source ./pipeline/get_context.sh
error_check 'ERROR happened during restoring the pipeline context\n'
printf "STEP 1 - End\n"

printf "STEP 2 - Begin - Copying result files to the S3 bucket\n"
aws s3 cp "${_OUTPUT_DIR}" "s3://${AWS_S3_BUCKET_NAME}/output/${_S3_OUTPUT_DIR}" --recursive --sse > /dev/null
error_check "ERROR happened during copying results to the S3 bucket\n"
printf "STEP 2 - End\n"

printf "STEP 3 - Begin - Cleaning the context of the pipeline\n"
source ./pipeline/clean_context.sh
error_check "ERROR happened during clenaning the context of the pipeline\n"
printf "STEP 3 - End\n"

printf "SCRIPT - End\n"