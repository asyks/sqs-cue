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

QUEUE_URL_BASE = 'https://sqs.us-west-2.amazonaws.com/776591507825/'

# Layer 1 Queues
QUEUE_URL = os.environ.get(
    'QUEUE_URL', QUEUE_URL_BASE + 'ua-DEV-cust-usgdata.fifo'
)

# Layer 2 Queues
QUEUE_URL_BILLING = QUEUE_URL_BASE + 'ua-DEV-cudata-bllng.fifo'
QUEUE_URL_CRM = QUEUE_URL_BASE + 'ua-DEV-cudata-crm.fifo'
QUEUE_URL_DW = QUEUE_URL_BASE + 'ua-DEV-cudata-dw.fifo'

LAYER_TWO_QUEUES = (QUEUE_URL_BILLING, QUEUE_URL_CRM, QUEUE_URL_DW)
