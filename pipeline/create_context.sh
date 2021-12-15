#!/bin/bash
# This script create a context that is going to be used in the pipeline.
# In order to create context it needs:
#  1. Create a folder in S3 bucket with the name of the pipeline
#  2. Place a json file with the following name 1.json to the created folder. Where 1 indicates
#     the stage number that is supposed to be initiated on the next step
touch 1.json
aws s3 cp 1.json "s3://${AWS_S3_BUCKET_NAME}/inbox/pipelines/${_JOB_ID}"