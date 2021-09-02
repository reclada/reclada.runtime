"""
   Encrypt and decrypt data in payload
"""
import logging
import os
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from srv.kms.kms import KMS

logger = logging.getLogger()
logger.setLevel(logging.INFO)

master_key_description = os.getenv("KMS_MASTER_KEY") or "dev_reclada"
kms = KMS(master_key_description)

def encrypt(payload):
    """
       Encrypt attribute data in payload.
       The structure of payload:
           {
             'type' - the type of actions [encrypt]
             'data' - the data for which the requested action needs to be executed
             'masterKey' - the name of the master key
           }
    """

    if 'data' not in payload:
        error_text = f'There is no data for encryption'
        logger.error(error_text)
        return {'error': error_text}

    # set the correct master key
    check_master_key(payload)

    # encrypt the data for the specified master key
    response = kms.encrypt_data(payload['data'])

    # return json with the encrypted data
    return {'data': response}


def decrypt(payload):
    """
        Decrypt the attribute data in payload
               The structure of payload:
           {
             'type' - the type of actions [decrypt]
             'data' - the data for which the requested action needs to be executed
             'masterKey' - the name of the master key
           }
    """

    # check if data attribute is present in payload
    if 'data' not in payload:
        error_text = f'There is no data for decryption'
        logger.error(error_text)
        return {'error': error_text}

    # check the master key in payload
    check_master_key(payload)

    # decrypt the data attribute
    try:
        response = kms.decrypt_data(payload['data'])
    except Exception as ex:
        logger.error(format(ex))
        return {'error': format(ex)}

    return {'data': response}


def check_master_key(payload):
    """
       This function check master key in payload and if it is present
       then creates the KMS client with this master key. If master key is not
       present then checks if the current master key is the same as specified during
       initialization if it is not then create the KMS client with the default master key
    """
    global kms
    # check if master key name is specified in payload then
    # we need to create KMS with this master key
    if 'masterKey' in payload:
        kms = KMS(payload['masterKey'])
    else:
        if kms.master_key_name != master_key_description:
            kms = KMS(master_key_description)


def lambda_handler(event, context):
    """
        This function handles requests from different lambda clients
    """
    # logging the even type
    logger.info(f'Event: {event}')

    # check if type attribute is present in payload
    if 'type' not in event:
        return {'error': 'type parameter must be present'}

    # get request type
    request_type = event['type']

    # handles the different request types
    if request_type == 'encrypt':
        return encrypt(event)
    elif request_type == 'decrypt':
        return decrypt(event)
    else:
        return {'error': 'request type not supported'}


if __name__ == '__main__':
    event_get = {
        'type': 'encrypt',
        'masterKey': 'dev_reclada',
        'data': 's3://bucket/key.pdf',
    }
    print(lambda_handler(event_get, None))

    event_post = {
        'type': 'decrypt',
        'masterKey': 'dev_reclada',
        'data': 'inbox/',
    }
    print(lambda_handler(event_post, None))
