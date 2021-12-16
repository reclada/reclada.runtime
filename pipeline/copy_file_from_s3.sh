#!/bin/bash
source ./error_check.sh
export _S3_FILE_URI="$1"
export _FILE_ID="$2"
export _JOB_ID="$3"
export _S3_OUTPUT_DIR="$4"
export _INPUT_DIR="/mnt/input/${_JOB_ID}"
export _OUTPUT_DIR="/mnt/output/${_JOB_ID}"

printf "SCRIPT - Begin - Coping a file %s from S3 bucket for pipeline %s\n" _S3_FILE_URI _JOB_ID

printf "STEP 1 - Begin - Parsing DB_URI environment variable\n"
S3_FILE_NAME=`python3 -c "print('$_S3_FILE_URI'.split('/')[-1])"`
printf "STEP 1 - End\n"

printf "STEP 2 - Begin - Copying files from S3 bucket to local drive\n"
aws s3 cp "${_S3_FILE_URI}" "${_INPUT_DIR}/${S3_FILE_NAME}"
error_check 'ERROR happened during copying files form S3 bucket\n'
printf "STEP 2 - End \n"

printf "STEP 3 - Begin - Saving context\n"
source save_context.sh 2
error_check 'ERROR happened during saving context\n'
printf "STEP 3 - End\n"

printf "SCRIPT - End\n"