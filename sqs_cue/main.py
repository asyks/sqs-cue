#!/usr/bin/env python3

import config
import log
import sqs_client


def log_poll_queue():
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
                client.delete_message(
                    config.ingress_queue['queue_url'], message
                )

    # TODO: send each message asynchronously to secondary queues


def main():
    log_poll_queue()


if __name__ == '__main__':
    log.init_logger()
    main()
