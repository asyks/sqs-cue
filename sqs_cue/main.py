#!/usr/bin/env python

import asyncio
import logging

import config
import log
import sqs


logger = logging.getLogger(__name__)


async def transform_message(transformer, message):
    if not transformer:
        return message
    else:
        return message

    # Retrieve transformer, execute, return result


async def handle_route(route, message):
    failure = False

    try:
        message_id = message['MessageId']
    except KeyError:
        logger.error("Received message did not contain key 'MessageId'")
        failure = True

    else:
        if route['type'] == 'sqs':
            try:
                queue_url = route['url']
            except KeyError:
                raise KeyError(
                    "route is type 'sqs', but queue 'url' not provided"
                )

            try:
                access_key_id = route['access_key_id']
                access_key = route['access_key']
                region = route['region']
            except KeyError:
                raise KeyError(
                    "route with queue_url {queue_url} is misconfigured, "
                    "must provide: access_key_id, access_key, and region"
                )

            logger.info(
                'Sending message %s to queue %s', message_id, queue_url
            )

            client = sqs.Client(
                access_key_id=access_key_id,
                access_key=access_key,
                region=region
            )
            response = client.enqueue(route['url'], 'type1', message['Body'])

        if route['type'] == 'raw_http':
            logger.info(
                'Sending message %s as raw http request', message_id
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
    try:
        queue_url = config.receiver['url']
    except KeyError:
        raise KeyError("receiver queue 'url' not provided")

    try:
        access_key_id = config.receiver['access_key_id']
        access_key = config.receiver['access_key']
        region = config.receiver['region']
    except KeyError:
        raise KeyError(
            "receiver with queue_url {queue_url} is misconfigured, "
            "must provide: access_key_id, access_key, and region"
        )

    # Instantiate Long Poller on receiver queue
    client = sqs.Client(
        access_key_id=access_key_id,
        access_key=access_key,
        region=region
    )
    dequeue = client.dequeue(queue_url)

    while True:
        try:
            message = next(dequeue)
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
