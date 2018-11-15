import os


LOG_RECORD_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
QUEUE_CONFIG_FILE = os.environ.get('QUEUE_CONFIG_FILE')
