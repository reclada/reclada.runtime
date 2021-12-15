#!/bin/bash
source ./error_check.sh

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

printf "STEP 1 - Begin - Creating context for the pipeline\n"
source ./create_context.sh
error_check 'ERROR happened during creating context.\n'
printf "STEP 1 - End\n"