#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess
from mmpm import colors, utils
from os.path import join
import logging
import logging.handlers

# String constants
MMPM_ENV_VAR = 'MMPM_MAGICMIRROR_ROOT'
MMPM_REPO_URL = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL = 'https://github.com/Bee-Mar/mmpm/wiki/MMPM-Command-Line-Options'
MAGICMIRROR_MODULES_URL = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"

HOME_DIR = os.path.expanduser("~")
TITLE = 'Title'
REPOSITORY = 'Repository'
DESCRIPTION = 'Description'
AUTHOR = 'Author'
CATEGORY = 'Category'
MAGICMIRROR_ROOT = os.environ[MMPM_ENV_VAR] if MMPM_ENV_VAR in os.environ else os.path.join(HOME_DIR, 'MagicMirror')
MAGICMIRROR_CONFIG_FILE = join(MAGICMIRROR_ROOT, 'config', 'config.js')
MMPM_CONFIG_DIR = join(utils.HOME_DIR, '.config', 'mmpm')
SNAPSHOT_FILE = join(MMPM_CONFIG_DIR, 'MagicMirror-modules-snapshot.json')
MMPM_EXTERNAL_SOURCES_FILE = join(MMPM_CONFIG_DIR, 'mmpm-external-sources.json')
EXTERNAL_MODULE_SOURCES = 'External Module Sources'


class MMPMLogger():
    def __init__(self):
        self.log_file = os.path.join(utils.MMPM_CONFIG_DIR, 'log', 'mmpm-cli-interface.log')
        logging.basicConfig(filename=self.log_file)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        self.handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            mode='a',
            maxBytes=1024*1024,
            backupCount=2,
            encoding=None,
            delay=0
        )

        logger.addHandler(self.handler)
        self.logger = logger


log = MMPMLogger()


def plain_print(msg):
    '''
    Prints message 'msg' without a new line

    Parameters:
        msg (str): The message to be printed to stdout

    Returns:
        None
    '''
    sys.stdout.write(msg)
    sys.stdout.flush()


def error_msg(msg):
    '''
    Displays error message to user, and exits program.

    Parameters:
        msg (str): The error message to be printed to stdout
    '''
    print(colors.B_RED + "ERROR: " + colors.RESET + msg)


def warning_msg(msg):
    '''
    Displays warning message to user and continues program execution.

    Parameters:
        msg (str): The warning message to be printed to stdout

    Returns:
        None
    '''
    print(colors.B_YELLOW + "WARNING: " + colors.RESET + msg)


def run_cmd(command):
    '''
    Executes shell command and captures errors

    Parameters:
        command (str): The command string to be executed

    Returns:
        returncode (str): The integer return code of the executed subprocess
        stdout (str): The stdout output of the executed subprocess
        stderr (str): The stderr output of the executed subprocess
    '''
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')


def handle_warnings(return_code, std_err, success='done\n'):
    '''
    Used in conjuction with 'run_cmd' to display warnings properly, if any were
    produced, otherwise the command's stdout is printed

    Parameters:
        return_code (int): The return code produced by the subprocess executed within 'run_cmd'
        std_err (int): The stderr output produced from the subprocess executed within 'run_cmd'
        success (str): The success message to display to the user

    Returns:
        None
    '''
    if return_code:
        print('\n')
        utils.warning_msg(std_err)
    else:
        utils.plain_print(colors.B_WHITE + success)


def get_file_path(path):
    return path if os.path.exists(path) else ''


def open_default_editor(file_path):
    if not file_path:
        error_msg(f'MagicMirror config file not found. Please ensure {MMPM_ENV_VAR} is set properly.')
        sys.exit(1)

    editor = os.getenv('EDITOR') if os.getenv('EDITOR') else 'nano'
    return_code, _, _ = run_cmd(['which', editor])

    # fall back to the 'edit' command if you don't even have nano...which idk why you wouldn't, but whatever
    os.system(f'{editor} {file_path}') if not return_code else os.system(f'edit {file_path}')
