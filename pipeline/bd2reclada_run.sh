#!/bin/bash
source ./pipeline/error_check.sh

export _S3_FILE_URI="$1"
export _FILE_ID="$2"
export _JOB_ID="$3"
export _S3_OUTPUT_DIR="$4"
export _INPUT_DIR="/mnt/input/${_JOB_ID}"
export _OUTPUT_DIR="/mnt/output/${_JOB_ID}"
export PYTHONPATH="${PYTHONPATH}:${BADGERDOC_REPO_PATH}"
export PYTHONPATH="${PYTHONPATH}:${SCINLP_REPO_PATH}/lite:${SCINLP_REPO_PATH}"

printf "SCRIPT - Beging - Running bd2reclada utility for pipeline %s\n" "${_JOB_ID}"

printf "STEP 1 - Begin - Restoring the pipeline context\n"
CURRENT_DIR="${PWD}"
source ./pipeline/get_context.sh
error_check 'ERROR happened during restoring the pipeline context\n'
printf "STEP 1 - End\n"

printf "STEP 2 - Begin - Parsing S3 file name\n"
S3_FILE_NAME=`python3 -c "print('$_S3_FILE_URI'.split('/')[-1])"`
printf "STEP 2 - End\n"

printf "STEP 3 - Begin - Starting bd2reclada\n"
cd ${SCINLP_REPO_PATH}/src/srv/bd2reclada
sudo python3 setup.py install
python3 -m bd2reclada "${_OUTPUT_DIR}/${S3_FILE_NAME}/document.json" "${_OUTPUT_DIR}/output.csv" "${_FILE_ID}"
error_check "ERROR happened during running bd2reclada\n"
printf "STEP 3 - End\n"

printf "STEP 4 - Begin - Saving the pipeline context\n"
cd ${CURRENT_DIR}
source ./pipeline/save_context.sh 4
error_check 'ERROR happened during saving the pipeline context\n'
printf "STEP 4 - End\n"
