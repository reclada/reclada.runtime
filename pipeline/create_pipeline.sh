#!/bin/bash
source ./error_check.sh

export _S3_FILE_URI="$1"
export _FILE_ID="$2"
export _JOB_ID="$3"
export _S3_OUTPUT_DIR="$4"
export _INPUT_DIR="/mnt/input/${_JOB_ID}"
export _OUTPUT_DIR="/mnt/output/${_JOB_ID}"

printf "SCRIPT - BEGIN - Creating the pipeline context for pipeline %s has been started\n" _JOB_ID
printf "STEP 1 - Begin - Creating context for the pipeline\n"
source ./create_context.sh
error_check 'ERROR happened during creating context\n'
printf "STEP 1 - End\n"
printf "SCRIPT - END\n"