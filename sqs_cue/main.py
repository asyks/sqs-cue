#!/usr/bin/env python3.7

import asyncio

import config
import log
import sqs_client


def send_message(queue, message):
    client = sqs_client.SqsClient(
        access_key_id=queue['access_key_id'],
        access_key=queue['access_key'],
        region=queue['region'],
    )
    response = client.enqueue(queue['queue_url'], 'type1', message['Body'])

    return response


async def send_msg_async(queue, message):
    message_id = message['MessageId']
    queue_url = queue['queue_url']
    print(f'Sending message {message_id} to queue {queue_url}')

    response = send_message(queue, message)

    failure = False
    if (
        queue['critical']
        and response['ResponseMetadata']['HTTPStatusCode'] != 200
    ):
        failure = True

    return failure


async def async_send_message(queues, message):
    failures = await asyncio.gather(
        *(send_msg_async(queue, message) for queue in queues)
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

    # Retrieve messages from initial queue
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
                    async_send_message(config.senders, message)
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
