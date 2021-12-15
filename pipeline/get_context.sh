#!/bin/bash
# This script restore the pipeline context from the S3 bucket.
# It copies the input and output dir from S3 bucket to the local drive
aws s3 cp "s3://${AWS_S3_BUCKET_NAME}/output/${_S3_OUTPUT_DIR}/context/output" "${_OUTPUT_DIR}"--recursive --sse
aws s3 cp "s3://${AWS_S3_BUCKET_NAME}/output/${_S3_OUTPUT_DIR}/context/input" "${_INPUT_DIR}"--recursive --sse
