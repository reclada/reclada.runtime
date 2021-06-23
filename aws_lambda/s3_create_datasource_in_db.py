"""
Creates datasource in DB when a new file appears in S3
"""
import json
import logging
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


def lambda_handler(event, context):
    logger.info(f'Event: {event}')

    connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            name = key.split('/')[-1]
            uri = 's3://' + bucket + '/' + key

            if key.endswith('/'):  # if key is folder
                continue

            data = {
                'class': 'DataSource',
                'attrs': {
                    'name': name,
                    'uri': uri,
                },
            }

            cursor.callproc('reclada_object.create', [json.dumps(data)])
        connection.commit()
    except Exception as err:
        logger.error(f'An exception occurred while creating datasource: {err}')
        connection.rollback()
    finally:
        cursor.close()
        connection_pool.putconn(connection)
