"""
Get presigned url for s3 object
"""
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(payload):
    logger.info(f': {payload}')

    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': payload["bucket_name"],
                                                            'Key': payload["object_name"]},
                                                    ExpiresIn=payload["expiration"])
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response