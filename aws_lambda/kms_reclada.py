"""
   Encrypt and decrypt data in payload
"""
import logging
import os

from kms import KMS

logger = logging.getLogger()
logger.setLevel(logging.INFO)

master_key_description = os.getenv("KMS_MASTER_KEY") or "dev_reclada"
aws_access_key = os.getenv("AWS_ACCESS_KEY") or None
aws_secret_access_key = os.getenv("AWS_SECRET_KEY") or None
kms = KMS(master_key_description, aws_access_key, aws_secret_access_key)

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

    logger.info(f'Data is present in payload.')

    # set the correct master key
    check_master_key(payload)

    logger.info(f'Master Key is set.')

    # encrypt the data for the specified master key
    logger.info(f'Encryption started.')
    response = kms.encrypt_data(payload['data'])
    logger.info(f'Encryption ended.')

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

    logger.info(f'Data for decryption is present.')

    # check the master key in payload
    check_master_key(payload)

    logger.info(f'Master Key is set{master_key_description}.')

    # decrypt the data attribute
    try:
        logger.info(f'Begin decrypting.')
        response = kms.decrypt_data(payload['data'])
        logger.info(f'End decrypting.')
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



    if 'masterKey' in payload or 'aws_access_key' in payload:
        aws_access_key = payload['aws_access_key']
        aws_secret_access_key = payload['aws_access_secret_key']
        kms = KMS(payload['masterKey'], aws_access_key, aws_secret_access_key)
        logger.info(f'Master Key is set.{payload["masterKey"]} - {aws_access_key}')
    else:
        if kms.master_key_name != master_key_description:
            if aws_access_key != payload["aws_access_key"]:
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



