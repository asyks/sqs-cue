#!/usr/bin/env python

import constants
import log
import msg_faker
import sqs_client


def main():
    # create fake messages
    msg_dicts = []
    for _i in range(10):
        msg_dicts.append(msg_faker.create_msg_dict())

    # connect to sqs
    client = sqs_client.SqsClient(
        access_key_id=constants.ACCESS_KEY_ID,
        access_key=constants.ACCESS_KEY,
        region=constants.REGION,
    )

    # send messages to initial queue
    for msg_dict in msg_dicts:
        client.enqueue(
            constants.QUEUE_URL, sqs_client.DEFAULT_MSG_TYPE, msg_dict
        )

    # TODO: read messages from initial queue
    # TODO: send each message asynchronously to secondary queues


if __name__ == '__main__':
    log.init_logger()
    main()
