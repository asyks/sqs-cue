#!/usr/bin/env python

import constants
import log
import sqs_client


def log_poll_queue():
    # connect to sqs
    client = sqs_client.SqsClient(
        access_key_id=constants.ACCESS_KEY_ID,
        access_key=constants.ACCESS_KEY,
        region=constants.REGION,
    )

    # retrieve messages from initial queue
    dequeue = client.dequeue(constants.QUEUE_URL)
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
                client.delete_message(constants.QUEUE_URL, message)

    # TODO: send each message asynchronously to secondary queues


def main():
    log_poll_queue()


if __name__ == '__main__':
    log.init_logger()
    main()
