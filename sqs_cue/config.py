import yaml

import constants


with open(constants.QUEUE_CONFIG_FILE, 'r') as config_file:
    queue_config = yaml.load(config_file)

receiver = queue_config['receiver']
routes = queue_config['routes']
