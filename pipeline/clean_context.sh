#!/bin/bash
# This script clean the pipeline context that was used in the pipeline.
# It will clean all files from /mnt/output and from /mnt/input folders to the S3 bucket
aws s3 rm "s3://${AWS_S3_BUCKET_NAME}/output/${_JOB_ID}/context/output/" --recursive > /dev/null
aws s3 rm "s3://${AWS_S3_BUCKET_NAME}/output/${_JOB_ID}/context/input/" --recursive  > /dev/null
aws s3 rm "s3://${AWS_S3_BUCKET_NAME}/inbox/pipelines/${_JOB_ID}/" > /dev/null