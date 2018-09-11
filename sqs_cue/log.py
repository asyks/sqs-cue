#!/usr/bin/env python

import logging

import constants


def init_logger(log_level=logging.INFO):
    # Get the root logger, and create a console log handler
    logger = logging.getLogger()
    stream_handler = logging.StreamHandler()
    # Set the log level of the root logger and handler
    stream_handler.setLevel(log_level)
    logger.setLevel(log_level)
    # Create formatter and add it to the handler
    formatter = logging.Formatter(constants.LOG_RECORD_FORMAT)
    stream_handler.setFormatter(formatter)
    # Add the handler to the logger
    logger.addHandler(stream_handler)
