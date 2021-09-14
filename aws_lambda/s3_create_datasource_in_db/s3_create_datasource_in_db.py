"""
Creates object of the class File (subclass of DataSource) in DB when a new file appears in S3
"""
import json
import logging
import mimetypes
import os
from urllib.parse import unquote_plus

from psycopg2.pool import SimpleConnectionPool

logger = logging.getLogger()
logger.setLevel(logging.INFO)

connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    host=os.getenv('PG_HOST'),
    database=os.getenv('PG_DATABASE'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
)


def update_mimetypes():
    """
    Adds mime types from DB

    """
    connection = connection_pool.getconn()
    cursor = connection.cursor()

    data = {
        'class': 'FileExtension',
        'attributes': {},
    }
    try:
        # Read file extensions form DB
        cursor.callproc('reclada_object.list', [json.dumps(data)])
        extensions = cursor.fetchall()[0][0]

        if extensions is None:
            return

        # Add new mime types to the list of known ones
        for extension in extensions:
            mimetypes.add_type(
                type=extension['attributes']['mimeType'],
                ext=extension['attributes']['extension'],
                strict=False,
            )
    except Exception as err:
        logger.error(f'An exception occurred while receiving mimetypes: {err}')
    finally:
        cursor.close()
        connection_pool.putconn(connection)


mimetypes.init()
update_mimetypes()


def lambda_handler(event, context):
    logger.info(f'Event: {event}')

    connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        for record in event['Records']:
            checksum = record['s3']['object']['eTag']
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            name = key.split('/')[-1]
            uri = 's3://' + bucket + '/' + key

            if key.endswith('/'):  # if key is folder
                continue

            # Determine the mime type
            mime_type = mimetypes.guess_type(uri, strict=False)[0]

            data = {
                'class': 'File',
                'attributes': {
                    'name': name,
                    'uri': uri,
                    'mimeType': mime_type or 'unknown',
                    'checksum': checksum,
                },
            }
            # Create object in DB
            cursor.callproc('reclada_object.create', [json.dumps(data)])

        connection.commit()
    except Exception as err:
        logger.error(f'An exception occurred while creating datasource: {err}')
        connection.rollback()
    finally:
        cursor.close()
        connection_pool.putconn(connection)
