#!/usr/bin/env python

import datetime
import json
import logging

import boto3


logger = logging.getLogger(__name__)


DEFAULT_MSG_TYPE = 'default-message-type'
DEFAULT_MSG_GRP_ID = 'default-message-group'


def iso_timestamp(dt):
    timestamp = dt.isoformat()
    if bool(dt.microsecond) and len(dt.isoformat()) > 19:
        timestamp = timestamp[:-4]

    return timestamp


class SqsClient(object):

    @staticmethod
    def _extract_value(message, key):
        value = None

        try:
            value = message[key]
        except KeyError:
            logger.warn(u'KeyError: message did not contain key "%s"', key)

        return value

    def __init__(self, access_key_id=None, access_key=None, region=None):
        self.sqs = None

        if all((access_key_id, access_key, region)):
            self.connect_to_sqs(access_key_id, access_key, region)

        return super(SqsClient, self).__init__()

    def connect_to_sqs(self, access_key_id, access_key, region):
        self.sqs = boto3.client(
            'sqs',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_key,
            region_name=region,
        )

        logger.info(
            u'Connected to AWS SQS region: %s',
            self.sqs._client_config.region_name
        )

        return self.sqs

    @classmethod
    def create_msg_attrs(cls, msg_type, timestamp=None):
        if not timestamp:
            timestamp = iso_timestamp(datetime.datetime.utcnow())

        msg_attrs = {
            'msgType': {
                'StringValue': msg_type,
                'DataType': 'String'
            },
            'msgSentTimestamp': {
                'StringValue': timestamp,
                'DataType': 'String'
            },
        }

        return msg_attrs

    @classmethod
    def create_msg_body(cls, msg_type, msg_dict, timestamp=None):
        if not timestamp:
            timestamp = iso_timestamp(datetime.datetime.utcnow())

        msg_body = {
            'msgType': msg_type,
            'msgBodyData': msg_dict,
            'msgSentTimestamp': timestamp,
        }

        return msg_body

    def send_message(
        self, queue_url, msg_attrs, msg_body, msg_grp_id=DEFAULT_MSG_GRP_ID
    ):
        msg_body = json.dumps(msg_body)

        response = self.sqs.send_message(
            QueueUrl=queue_url,
            MessageAttributes=msg_attrs,
            MessageBody=msg_body,
            MessageGroupId=msg_grp_id,
        )

        _msg_id = self._extract_value(response, 'MessageId')

        logger.info(u'Sent MessageId=%s to Queue=%s', _msg_id, queue_url)

        return response

    def receive_message(self, queue_url):
        response = self.sqs.receive_message(QueueUrl=queue_url)

        message = {}
        try:
            _messages = response['Messages']
        except KeyError:
            logger.warn(
                u'KeyError: sqs response did not contain key "Messages"',
            )
        else:
            message = _messages.pop()

        _msg_id = self._extract_value(message, 'MessageId')

        logger.info(u'Received MessageId=%s from Queue=%s', _msg_id, queue_url)

        return message

    def delete_message(self, queue_url, message):
        _recp_hndl = self._extract_value(message, 'ReceiptHandle')

        response = self.sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=_recp_hndl,
        )

        _metadata = self._extract_value(response, 'ResponseMetadata')
        _status_code = self._extract_value(_metadata, 'HTTPStatusCode')

        if _status_code == 200:
            _msg_id = self._extract_value(message, 'MessageId')
            logger.info(
                u'Deleted MessageId=%s from Queue=%s', _msg_id, queue_url
            )
        else:
            raise Exception('SQS delete message request failed')

    def enqueue(self, queue_url, msg_type, msg_dict):
        timestamp = iso_timestamp(datetime.datetime.utcnow())

        msg_attrs = self.create_msg_attrs(msg_type, timestamp=timestamp)

        msg_body = self.create_msg_body(
            msg_type, msg_dict, timestamp=timestamp
        )

        response = self.send_message(queue_url, msg_attrs, msg_body)

        return response

    def dequeue(self, queue_url):
        while True:

            message = self.receive_message(queue_url)
            if not message:
                break

            self.delete_message(queue_url, message)

            yield message
