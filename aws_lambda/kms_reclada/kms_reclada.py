"""
   Encrypt and decrypt data in payload
"""
import logging
import os

from kms import KMS

logger = logging.getLogger()
logger.setLevel(logging.INFO)

master_key_description = os.getenv("KMS_MASTER_KEY") or "dev_reclada"
aws_access_key = os.getenv("AWS_ACCESS_KEY_RECLADA") or os.getenv("AWS_ACCESS_KEY")
aws_access_secret_key = os.getenv("AWS_SECRET_KEY_RECLADA") or os.getenv("AWS_ACCESS_KEY")
kms_client = None

def encrypt(payload):
    """
       Encrypt attribute data in payload.
       The structure of payload:
           {
             'type' - the type of actions [encrypt]
             'data' - the data for which the requested action needs to be executed
             'masterKey' - the name of the master key
             'aws_access_key' - user's AWS key
             'aws_access_secret_key' - user's AWS secret key
           }
    """

    if 'data' not in payload:
        error_text = f'There is no data for encryption'
        logger.error(error_text)
        return {'error': error_text}

    # set the correct master key
    check_master_key(payload)

    # encrypt the data for the specified master key
    response = kms_client.encrypt_data(payload['data'])

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
             'aws_access_key' - user's AWS key
             'aws_access_secret_key' - user's AWS secret key
           }
    """
    global kms_client

    # check if data attribute is present in payload
    if 'data' not in payload:
        error_text = f'There is no data for decryption'
        logger.error(error_text)
        return {'error': error_text}

    # check the master key in payload
    check_master_key(payload)

    # decrypt the data attribute
    try:
        response = kms_client.decrypt_data(payload['data'])
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
    global kms_client, master_key_description
    # check if master key name is specified in payload then
    # we need to create KMS with this master key

    if 'aws_access_key' in payload and 'aws_access_secret_key' in payload:
        aws_access_key = payload['aws_access_key']
        aws_access_secret_key = payload['aws_access_secret_key']
    else:
        aws_access_key = os.getenv("AWS_ACCESS_KEY_RECLADA") or None
        aws_access_secret_key = os.getenv("AWS_SECRET_KEY_RECLADA") or None

    if 'masterKey' in payload:
        master_key_description = payload['masterKey']
        kms_client = KMS(master_key_description, aws_access_key, aws_access_secret_key)
        logger.info(f'Master Key is set {payload["masterKey"]} - {aws_access_key}')
    else:
        if kms_client is None or kms_client.master_key_name != master_key_description:
            kms_client = KMS(master_key_description, aws_access_key, aws_access_secret_key)
    logger.info(f'Master Key is set {payload["masterKey"]} - {aws_access_key}')

def lambda_handler(event, context):
    """
        This function handles requests from different lambda clients
    """
    # logging the even type
    logger.info(f'Event: {event}')

    # check if type attribute is present in payload
    if 'type' not in event:
        return {'error': 'type parameter must be present'}
    logger.info(f'Type of operation is present.')

    # get request type
    request_type = event['type']

    # handles the different request types
    if request_type == 'encrypt':
        return encrypt(event)
    elif request_type == 'decrypt':
        return decrypt(event)
    else:
        return {'error': 'request type not supported'}



