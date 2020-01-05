#!/usr/bin/env python3
import sys
import os
import subprocess
from mmpm import colors, utils

HOME_DIR = os.path.expanduser("~")


def plain_print(msg):
    '''
    Prints message 'msg' without a new line

    Arguments
    =========
    msg: String
    '''
    sys.stdout.write(msg)
    sys.stdout.flush()


def error_msg(msg):
    '''
    Displays error message to user, and exits program.

    Arguments
    =========
    msg: String
    '''
    print(colors.BRIGHT_RED + "ERROR: " + colors.BRIGHT_WHITE + msg)
    exit(0)


def warning_msg(msg):
    '''
    Displays warning message to user and continues program execution.

    Arguments
    =========
    msg: String
    '''
    print(colors.BRIGHT_YELLOW + "WARNING: " + colors.NORMAL_WHITE + msg)


def run_cmd(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')


def handle_warnings(return_code, std_err, success='done\n'):
    if return_code:
        print('\n')
        utils.warning_msg(std_err)
    else:
        utils.plain_print(colors.BRIGHT_WHITE + success)


def get_magicmirror_root():
    return os.environ['MMPM_MAGICMIRROR_ROOT'] if 'MMPM_MAGICMIRROR_ROOT' in os.environ else os.path.join(HOME_DIR, 'MagicMirror')
