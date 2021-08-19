"""
Get presigned url for s3 object
"""
import logging
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')


def lambda_handler(event, context):
    logger.info(f'Event: {event}')

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
            ExpiresIn=event['expiration'],
        )
    except ClientError as err:
        logging.error(err)
        return {}

    # The response contains the presigned URL
    return {'url': url}
