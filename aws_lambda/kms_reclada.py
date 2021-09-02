"""
   Encrypt and decrypt data in payload
"""
import json
import logging
import os
from urllib.parse import unquote_plus


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f'Event: {event}')
