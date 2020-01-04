#!/usr/bin/env python3
import sys


def plain_print(msg):
    '''
    Prints message 'msg' without a new line

    Arguments
    =========
    msg: String
    '''
    sys.stdout.write(msg)
    sys.stdout.flush()
