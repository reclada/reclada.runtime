# s3_get_presigned_url AWS Lambda function 

## Description

_s3_get_presigned_url_ AWS Lambda function provides generating of presigned URLs for files downloading from AWS S3 or uploading to AWS S3.

Normally it's called from AWS RDS stored procedure.

Event description to get presigned URL for downloading from S3:
```
{
    'type': request type [get]
    'uri': S3 object URI
    'expiration': URL expiration duration in seconds
}
```

Event description to get presigned URL for uploading to S3:
```
{
    'type': request type [post]
    'bucketName': name of the S3 bucket to upload to
    'folderPath': folder path inside the S3 bucket to upload to
    'fileName': name of the file
    'fileType': MIME type of the file
    'fileSize': size of the file
    'expiration': URL expiration duration in seconds
}
```

## Installation

- Upload the source code of the function. The source code is zipped in _s3_get_presigned_url.zip_ file and can be found in _installation_ folder.
- Attach the permissions to the function. For _Resource_ parameter use the S3 bucket ARN:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::bucket-name/*"
        }
    ]
}
```
