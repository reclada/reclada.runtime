import json
import os
import uuid
from urllib.parse import urlparse

import psycopg2


def main():
    credentials = urlparse(os.getenv('DB_URI'))

    connection = psycopg2.connect(
        host=credentials.hostname,
        database=credentials.path[1:],
        user=credentials.username,
        password=credentials.password,
    )

    for _ in range(5):
        cursor = connection.cursor()

        data = {
            'class': 'Runner',
            'attrs': {
                'command': '',
                'status': 'down',
                'type': 'DOMINO',
                'task': str(uuid.uuid4()),
                'environment': str(uuid.uuid4()),
            },
        }
        cursor.callproc('reclada_object.create', [json.dumps(data)])
        connection.commit()

    connection.close()


if __name__ == '__main__':
    main()
