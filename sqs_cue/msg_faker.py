#!/usr/bin/env python

import random


def create_msg_dict():
    msg_dict = {
        'key': random.getrandbits(100),
        'name': random.getrandbits(100),
    }

    return msg_dict
