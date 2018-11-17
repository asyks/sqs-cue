import yaml

import constants


with open(constants.QUEUE_CONFIG_FILE, 'r') as config_file:
    queue_config = yaml.load(config_file)

ingress_queue = queue_config['ingress_queues'][0]
egress_queues = queue_config['egress_queues']
