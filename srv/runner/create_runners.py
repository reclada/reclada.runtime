"""
Creates reclada objects of class Runner in DB
"""
import argparse
import json
import os
import uuid
from urllib.parse import urlparse

import psycopg2


def init_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type')
    parser.add_argument('--number', default=5)
    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()

    credentials = urlparse(os.getenv('DB_URI'))

    connection = psycopg2.connect(
        host=credentials.hostname,
        database=credentials.path[1:],
        user=credentials.username,
        password=credentials.password,
    )

    for _ in range(int(args.number)):
        cursor = connection.cursor()

        data = {
            'class': 'Runner',
            'attributes': {
                'command': '',
                'status': 'down',
                'type': args.type,
                'task': str(uuid.uuid4()),
                'environment': str(uuid.uuid4()),
            },
        }
        cursor.callproc('reclada_object.create', [json.dumps(data)])
        connection.commit()
    connection.close()


if __name__ == '__main__':
    main()
