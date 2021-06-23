import json
import os
import uuid

import psycopg2

connection = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    database=os.getenv('PG_DATABASE'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
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
