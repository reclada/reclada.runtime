#!/bin/bash
# This script delete all files in the specified s3 bucket
# If there is no parameter with the bucket name then AWS_S3_BUCKET_NAME environment variable is used as the bucket name.

# Here we need to check if aws cli is installed
aws --version 2> /dev/null
if [ $? -ne 0 ]
  then
    printf "The aws client needs to be installed.\n"
fi

# The bucket name is supposed to be specified as the second parameter or
# in the environment variable AWS_S3_BUCKET_NAME and we need to check if it is specified.
# The bucket name should be specified in URI form for example s3://dev1-reclada-bucket or
# in the form of the plain name for example dev1-reclada-bucket
if [ -n "$1" ]
  then
    S3_BUCKET="$1"
    if [ "${S3_BUCKET:0:5}" != "s3://" ]
      then
        S3_BUCKET="s3://${S3_BUCKET}"
    fi
  elif [ -n "${AWS_S3_BUCKET_NAME}" ]
    then
      if [ "${AWS_S3_BUCKET_NAME:0:5}" == "s3://" ]
      then
        S3_BUCKET="${AWS_S3_BUCKET_NAME}"
      else
        S3_BUCKET="s3://${AWS_S3_BUCKET_NAME}"
      fi
  else
      printf "The S3 bucket name is not specified.\n"
      exit 0
fi

printf "The s3 bucket name %s \n" $S3_BUCKET

# Here we check the last character of the bucket name
# if it is "/" then consider deleting a folder otherwise
# deleting a file. Also we check if the bucket name has only the name of the bucket
# without prefixes or file names.
if [ "${S3_BUCKET: - 1}" == "/" ]
  then
    # Here we delete all files in the specified folder.
    # As folder in AWS is just a prefix associated with the S3 object sometimes
    # when prefixes exist only in files which are supposed to be deleted then
    # all such prefixes would be deleted as well.
    aws s3 rm ${S3_BUCKET} --recursive
  else
    COUNT_SLASH=$(echo "${S3_BUCKET}" | tr -cd '/' | wc -c)
    if [ "$COUNT_SLASH" -le 2 ]
    then
      aws s3 rm ${S3_BUCKET} --recursive
    else
      # Here we delete an S3 object. If this object has prefixes that
      # exists only in it then all these prefixes would be deleted as well
      aws s3 rm ${S3_BUCKET}
    fi
fi


