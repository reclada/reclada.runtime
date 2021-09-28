#!/bin/bash
# This script copies all files from the specified folder to the specified s3 bucket
# If there is no parameter with the bucket name then AWS_S3_BUCKET_NAME environment variable is used as the bucket name.

# The source folder needs to be specified as the first parameter of the script
SOURCE_FOLDER=${1:?"The source folder needs to be specified. $(exit 0)"}

# The bucket name is supposed to be specified as the second parameter or
# in the environment variable AWS_S3_BUCKET_NAME and we need to check if it is specified.
# The bucket name should be specified in URI form for example s3://dev1-reclada-bucket or
# in the form of the plain name for example dev1-reclada-bucket
if [ -n "$2" ]
  then
    S3_BUCKET="$2"
  elif [ -n "${AWS_S3_BUCKET_NAME}" ]
    then
      S3_FOLDER="/${SOURCE_FOLDER#/*/}"
      if [ "${AWS_S3_BUCKET_NAME:0:5}" == "s3://" ]
      then
        S3_BUCKET="${AWS_S3_BUCKET_NAME%/}${S3_FOLDER}"
      else
        S3_BUCKET="s3://${AWS_S3_BUCKET_NAME%/}${S3_FOLDER}"
      fi
  else
      printf "The S3 bucket name is not specified.\n"
      exit 0
fi

printf "The name of the S3 bucket %s\n" $S3_BUCKET

# Here we need to check if aws cli is installed
aws --version 2> /dev/null
if [ $? -ne 0 ]
  then
    printf "The aws client needs to be installed.\n"
fi

# Now we are ready to start a copy process
for file_name in "$1"*; do
   if ! [ -d "${file_name}" ]
     then
       # here we are coping a file to S3 bucket
       aws s3 cp """${file_name}""" "${S3_BUCKET}" --sse
  fi
done



