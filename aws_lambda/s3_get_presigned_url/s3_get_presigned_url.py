"""
Get presigned url for S3 object
"""
import logging
import os
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')


def generate_presigned_get(event):
    """
    Generates presigned URL for downloading from S3
    """
    if 'uri' not in event:
        return {'error': 'uri parameter must be present'}

    parsed_uri = urlparse(event['uri'])
    bucket = parsed_uri.netloc
    key = parsed_uri.path.lstrip('/')

    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': key,
            },
            ExpiresIn=event.get('expiration') or 3600,
        )
    except ClientError as err:
        logging.error(err)
        return {'error': err}

    # The response contains the presigned URL for downloading from S3
    return {'url': url}


def generate_presigned_post(event):
    """
    Generates presigned URL for uploading to S3
    """
    if 'fileName' not in event:
        return {'error': 'fileName parameter must be present'}

    if 'fileType' not in event:
        return {'error': 'fileType parameter must be present'}

    if 'fileSize' not in event:
        return {'error': 'fileSize parameter must be present'}

    bucket = event.get('bucketName') or os.getenv('DEFAULT_S3_BUCKET')
    if not bucket:
        return {'error': 'bucketName parameter or DEFAULT_S3_BUCKET environment variable must be present'}

    try:
        response = s3_client.generate_presigned_post(
            Bucket=bucket,
            Key=os.path.join(
                event.get('folderPath') or 'inbox/',
                event['fileName'],
            ),
            Fields={
                'Content-Type': event['fileType'],
            },
            Conditions=[
                {'Content-Type': event['fileType']},
                ['content-length-range', 1, event['fileSize']],
            ],
            ExpiresIn=event.get('expiration') or 3600,
        )
    except ClientError as err:
        logging.error(err)
        return {'error': err}

    # The response contains the presigned URL for uploading to S3
    return response


def lambda_handler(event, context):
    logger.info(f'Event: {event}')

    if 'type' not in event:
        return {'error': 'type parameter must be present'}

    request_type = event['type']

    if request_type == 'get':
        return generate_presigned_get(event)
    elif request_type == 'post':
        return generate_presigned_post(event)
    else:
        return {'error': 'request type not supported'}


if __name__ == '__main__':
    event_get = {
        'type': 'get',
        'uri': 's3://bucket/key.pdf',
        'expiration': 3600,
    }
    print(lambda_handler(event_get, None))

    event_post = {
        'type': 'post',
        'bucketName': 'bucket',
        'folderPath': 'inbox/',
        'fileName': 'key.pdf',
        'fileType': 'application/pdf',
        'fileSize': 100,
        'expiration': 3600,
    }
    print(lambda_handler(event_post, None))
