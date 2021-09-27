import argparse
import json
import os
from urllib.parse import urlparse

import psycopg2


def init_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type')
    parser.add_argument('--runner-id')
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

    cursor = connection.cursor()
    data = {
        'class': 'Job',
        'attributes': {
            'type': args.type,
            'status': 'new',
        },
    }

    cursor.callproc('reclada_object.list', [json.dumps(data)])
    jobs = cursor.fetchall()[0][0]

    for job in jobs:
        data = {
            'class': 'Job',
            'id': job['id'],
            'attributes': {
                'type': job['attributes']['type'],
                'task': job['attributes']['task'],
                'command': job['attributes']['command'],
                'input_parameters': job['attributes']['inputParameters'],
                'status': 'pending',
                'runner': args.runner_id,
            },
        }
        cursor.callproc('reclada_object.update', [json.dumps(data)])

    connection.commit()
    connection.close()


if __name__ == '__main__':
    main()
