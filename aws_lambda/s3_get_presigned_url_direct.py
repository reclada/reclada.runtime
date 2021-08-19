"""
Get presigned url for s3 object
"""
import argparse
import json
import logging
import os
from urllib.parse import urlparse

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

def create_client():
    return boto3.client(
        service_name='s3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION_NAME'),
    )


class S3Folder:
    def __init__(self, s3_folder_uri, client=None):
        self.s3_folder_uri = s3_folder_uri.rstrip("/") + "/"
        self._client = client or create_client()
        self._paginator = self._client.get_paginator("list_objects_v2")

        self._parsed_uri = urlparse(self.s3_folder_uri)
        self.bucket_name = self._parsed_uri.netloc
        self.prefix = self._parsed_uri.path.lstrip("/")

    @property
    def page_iterator(self):
        return self._paginator.paginate(
            Bucket=self.bucket_name,
            Prefix=self.prefix,
        )

    def get_files_uris(self):
        for page in self.page_iterator:
            for content in page.get("Contents", []):
                if not content["Key"].endswith("/"):
                    yield self.s3_folder_uri, content["Key"]


def init_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('s3_folder')
    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()
    s3_folder = S3Folder(args.s3_folder)
    s3_file_uris = s3_folder.get_files_uris()

    while True:
        try:
            bucket, object = next(s3_file_uris)
            json_param = {
                "bucket_name" : s3_folder.bucket_name,
                "object_name" : object,
                "expiration" : 60000,
            }
            presigned_url = lambda_handler(json_param)
            print(presigned_url)
        except StopIteration:
            break



if __name__ == '__main__':
    main()

