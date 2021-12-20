#!/bin/bash
# This script restore the pipeline context from the S3 bucket.
# It copies the input and output dir from S3 bucket to the local drive

# cleaning the pipeline context
if [[ -d "${_OUTPUT_DIR}" ]]
then
  rm -rf "${_OUTPUT_DIR}"
fi

if [[ -d "${_INPUT_DIR}" ]]
then
  rm -rf "${_INPUT_DIR}"
fi

# creating folders
mkdir "${_OUTPUT_DIR}"
mkdir "${_INPUT_DIR}"

# coping the context to the specified folders
aws s3 cp "s3://${AWS_S3_BUCKET_NAME}/output/${_JOB_ID}/context/output/" "${_OUTPUT_DIR}/" --recursive --sse > /dev/null
aws s3 cp "s3://${AWS_S3_BUCKET_NAME}/output/${_JOB_ID}/context/input/" "${_INPUT_DIR}/" --recursive --sse > /dev/null
