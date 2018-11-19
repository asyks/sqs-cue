#!/usr/bin/env python3.7

import asyncio

import config
import log
import sqs_client


async def handle_route(route, message):
    message_id = message['MessageId']

    if route['type'] == 'sqs':
        try:
            queue_url = route['queue_url']
        except KeyError:
            raise KeyError("route is type 'sqs', but 'queue_url' not provided")

        try:
            access_key_id = route['access_key_id']
            access_key = route['access_key']
            region = route['region']
        except KeyError:
            raise KeyError(
                "route with queue_url {queue_url} is misconfigured, "
                "must provide: access_key_id, access_key, and region"
            )

        print(f'Sending message {message_id} to queue {queue_url}')
        client = sqs_client.SqsClient(
            access_key_id=access_key_id, access_key=access_key, region=region
        )
        response = client.enqueue(route['queue_url'], 'type1', message['Body'])

    if route['type'] == 'raw':
        print(f'Sending message {message_id} as request')

    try:
        status_code = response['ResponseMetadata']['HTTPStatusCode']
    except KeyError:
        status_code = None

    failure = False
    if route['critical'] and status_code != 200:
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
    client = sqs_client.SqsClient(
        access_key_id=config.receiver['access_key_id'],
        access_key=config.receiver['access_key'],
        region=config.receiver['region'],
    )

    # Retrieve messages from receiver queue
    dequeue = client.dequeue(config.receiver['queue_url'])
    while True:
        try:
            message = next(dequeue)
        except StopIteration:
            print('Stopping Long Polling due to StopIteration')
            break
        except KeyboardInterrupt:
            print('Stopping Long Polling due to KeyboardInterrupt')
            break
        else:
            if message:
                success = asyncio.run(
                    async_process_message(config.routes, message)
                )

                message_id = message['MessageId']
                if success:
                    client.delete_message(
                        config.receiver['queue_url'], message
                    )
                else:
                    print(f'Message {message_id} handling failed.')


def main():
    long_poll_queue()


if __name__ == '__main__':
    log.init_logger()
    main()
