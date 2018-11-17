#!/usr/bin/env python3.7

import asyncio

import config
import log
import sqs_client


async def print_message(queue, message):
    message_id = message['MessageId']
    queue_url = queue['queue_url']
    print(f'Sending message {message_id} to queue {queue_url}')

    return True


async def async_send_message(queues, message):
    statuses = await asyncio.gather(
        *(print_message(queue, message) for queue in queues)
    )
    print(statuses)


def long_poll_queue():
    client = sqs_client.SqsClient(
        access_key_id=config.ingress_queue['access_key_id'],
        access_key=config.ingress_queue['access_key'],
        region=config.ingress_queue['region'],
    )

    # Retrieve messages from initial queue
    dequeue = client.dequeue(config.ingress_queue['queue_url'])
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
                asyncio.run(
                    async_send_message(
                        config.egress_queues, message
                    )
                )

                client.delete_message(
                    config.ingress_queue['queue_url'], message
                )


def main():
    long_poll_queue()


if __name__ == '__main__':
    log.init_logger()
    main()
