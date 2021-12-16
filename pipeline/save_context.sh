#!/bin/bash
# This script saving the pipeline context that is going to be used in the pipeline.
# It will copy all files from /mnt/output and from /mnt/input folders to the S3 bucket
aws s3 cp "${_OUTPUT_DIR}" "s3://${AWS_S3_BUCKET_NAME}/output/${_S3_OUTPUT_DIR}/context/output" --recursive --sse
aws s3 cp "${_INPUT_DIR}" "s3://${AWS_S3_BUCKET_NAME}/output/${_S3_OUTPUT_DIR}/context/input" --recursive --sse

# if we have a parameter then we need to create a json file to start processing of the next step in the pipeline
if [[ -n $1 ]]
then
  touch "$1.json"
  aws s3 cp "$1.json" "s3://${AWS_S3_BUCKET_NAME}/inbox/pipelines/${_JOB_ID}"
fi