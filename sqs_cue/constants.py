#!/usr/bin/env python

import os


LOG_RECORD_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

ENVIRONMENT = os.environ.get(
    'ENVIRONMENT',
    'dev'
)

# SQS client access
ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
REGION = os.environ.get('REGION', 'us-west-2')
QUEUE_URL = os.environ.get('QUEUE_URL')
