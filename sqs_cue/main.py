#!/usr/bin/env python

import asyncio
import logging
import json

import config
import log
import sqs


logger = logging.getLogger(__name__)


def recursive_transform(transform, message, result={}):
    for tform_name, tform_value in transform.items():
        if isinstance(tform_value, dict):
            result[tform_name] = {}
            recursive_transform(
                tform_value, message, result[tform_name]
            )

        elif isinstance(tform_value, str):
            _msg_value = message
            for _msg_name in tform_value.split('.'):
                _msg_value = _msg_value[_msg_name]

            result[tform_name] = _msg_value


def transform_message(transform, message, result={}):
    if not transform:
        return message

    recursive_transform(transform, message, result)

    return result


async def handle_route(route, message):
    failure = False

    try:
        message_id = message['MessageId']
    except KeyError:
        logger.error("Received message did not contain key 'MessageId'")
        failure = True

    try:
        message_body = json.loads(message['Body'])
    except json.decoder.JSONDecodeError:
        logger.error("Received message body is not valid json")
        failure = True
    else:
        message_body_out = transform_message(route['transform'], message_body)

        if route['type'] == 'sqs':
            logger.info(
                'Sending message %s to queue %s', message_id, route['url']
            )

            client = sqs.Client(
                access_key_id=route['access_key_id'],
                access_key=route['access_key'],
                region=route['region'],
            )
            response = client.enqueue(route['url'], 'type1', message_body_out)

        if route['type'] == 'raw_http':
            logger.info(
                'Sending message %s as raw http request %s',
                message_id,
                json.dumps(message_body_out),
            )
            response = {}

        try:
            status_code = response['ResponseMetadata']['HTTPStatusCode']
        except KeyError:
            status_code = None

        if not failure and route['critical'] and status_code != 200:
            failure = True

    return failure


async def async_process_message(routes, message):
    failures = await asyncio.gather(
        *(handle_route(route, message) for route in routes)
    )

    if not failures or any(failures):
        success = False
    else:
        success = True

    return success


def long_poll_queue():
    # Instantiate Long Poller on receiver queue
    client = sqs.Client(
        access_key_id=config.receiver['access_key_id'],
        access_key=config.receiver['access_key'],
        region=config.receiver['region'],
    )
    dequeue = client.dequeue(config.receiver['url'])

    while True:
        try:
            message = next(dequeue)  # Retrieve message from receiver queue
        except StopIteration:
            raise StopIteration('Stopping Long Polling due to StopIteration')
        except KeyboardInterrupt:
            raise KeyboardInterrupt(
                'Stopping Long Polling due to KeyboardInterrupt'
            )
        else:
            if message:
                # Send message to each route asynchronously
                success = asyncio.run(
                    async_process_message(config.routes, message)
                )

                if success:
                    client.delete_message(
                        config.receiver['url'], message
                    )
                else:
                    logger.warning(
                        'Message %s handling failed.', message['MessageId'],
                    )


def main():
    long_poll_queue()


if __name__ == '__main__':
    log.init_logger()
    main()
