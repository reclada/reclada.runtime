import os
from urllib.parse import urlparse

import boto3


class S3:
    def __init__(self):
        self.client = boto3.client(
            service_name='s3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION_NAME'),
        )

    def copy_file_to_local(self, file_uri, local_dir):
        parsed_uri = urlparse(file_uri)
        bucket = parsed_uri.netloc
        key = parsed_uri.path.lstrip('/')
        name = key.split('/')[-1]
        file_path = os.path.join(local_dir, name)

        with open(file_path, 'wb') as file:
            self.client.download_fileobj(bucket, key, file)

        return file_path

    # TODO:
    def copy_file_to_s3(self, file_path, file_uri):
        with open(file_path, 'rb') as file:
            self.client.upload_fileobj(file, 'mybucket', 'mykey')
