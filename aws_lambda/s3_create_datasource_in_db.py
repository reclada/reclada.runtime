"""
Creates datasource in DB when a new file appears in S3
"""
import json
import logging
import os

import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

conn = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    database=os.getenv('PG_DATABASE'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
)


def lambda_handler(event, context):
    logger.info(f'Event: {event}')
    logger.info(f'Context: {context}')

    cur = conn.cursor()

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
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

        cur.callproc('reclada_object.create', [json.dumps(data)])

    conn.commit()
    cur.close()
    conn.close()

    response = {'event': event, 'context': context}
    return response
