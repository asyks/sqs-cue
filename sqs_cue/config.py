import yaml

import constants


class YamlConfigError(KeyError):
    pass


def validate_queue_config(directive, queue_config):
    try:
        queue_url = queue_config['url']
    except KeyError:
        raise YamlConfigError(
            f"{directive} queue is type 'sqs', but queue 'url' not provided"
        )

    if not hasattr(queue_config, 'access_key_id'):
        raise YamlConfigError(
            f"{directive} with queue_url {queue_url} missing access_key_id"
        )
    if not hasattr(queue_config, 'access_key'):
        raise YamlConfigError(
            f"{directive} with queue_url {queue_url} missing access_key"
        )
    if not hasattr(queue_config, 'region'):
        raise YamlConfigError(
            f"{directive} with queue_url {queue_url} missing region"
        )


with open(constants.QUEUE_CONFIG_FILE, 'r') as config_file:
    queue_config = yaml.load(config_file)

# Source receiver sqs queue config
try:
    receiver = queue_config['receiver']
except KeyError:
    raise YamlConfigError('no source receiver provided')
else:
    validate_queue_config(receiver)

# Destination route sqs queue config
try:
    routes = queue_config['routes']
except KeyError:
    raise YamlConfigError('no destination routes provided')
else:
    for route in routes:
        try:
            route_type = route['type']
        except KeyError:
            raise YamlConfigError('route type not specified')

        if route['type'] == 'sqs':
            validate_queue_config(route)
