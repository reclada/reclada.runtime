"""
Reads S3 folder and creates datasource in DB
"""
import argparse
import json
import os
from urllib.parse import urlparse

import boto3
import psycopg2

connection = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    database=os.getenv('PG_DATABASE'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
)


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
                    yield self.s3_folder_uri + content["Key"]


def lambda_handler(uri):
    cursor = connection.cursor()

    try:
        data = {
            'class': 'DataSource',
            'attrs': {
                'name': uri.split('/')[-1],
                'uri': uri,
            },
        }

        cursor.callproc('reclada_object.create', [json.dumps(data)])
        connection.commit()
    except Exception:
        connection.rollback()
    finally:
        cursor.close()


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
            file_uri = next(s3_file_uris)
            lambda_handler(file_uri)
        except StopIteration:
            break

    connection.close()


if __name__ == '__main__':
    main()
