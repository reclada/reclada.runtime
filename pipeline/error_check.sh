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