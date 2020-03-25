#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess
from mmpm import colors, utils
from os.path import join
import logging
import logging.handlers
from typing import List

# String constants
MMPM_ENV_VAR: str = 'MMPM_MAGICMIRROR_ROOT'
MMPM_REPO_URL: str = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL: str = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL: str = 'https://github.com/Bee-Mar/mmpm/wiki/MMPM-Command-Line-Options'
MAGICMIRROR_MODULES_URL: str = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"

HOME_DIR: str = os.path.expanduser("~")
TITLE: str = 'Title'
REPOSITORY: str = 'Repository'
DESCRIPTION: str = 'Description'
AUTHOR: str = 'Author'
CATEGORY: str = 'Category'
MAGICMIRROR_ROOT: str = os.environ[MMPM_ENV_VAR] if MMPM_ENV_VAR in os.environ else os.path.join(HOME_DIR, 'MagicMirror')
MAGICMIRROR_CONFIG_FILE: str = join(MAGICMIRROR_ROOT, 'config', 'config.js')
MMPM_CONFIG_DIR: str = join(utils.HOME_DIR, '.config', 'mmpm')
SNAPSHOT_FILE: str = join(MMPM_CONFIG_DIR, 'MagicMirror-modules-snapshot.json')
MMPM_EXTERNAL_SOURCES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-external-sources.json')
EXTERNAL_MODULE_SOURCES: str = 'External Module Sources'


class MMPMLogger():
    '''
    Object used for logging while MMPM is executing. Log files can be found in
    ~/.config/mmpm/log
    '''
    def __init__(self):
        self.log_file: str = os.path.join(utils.MMPM_CONFIG_DIR, 'log', 'mmpm-cli-interface.log')
        self.log_format = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s'
        logging.basicConfig(filename=self.log_file, format=self.log_format)
        logger: logging.Logger = logging.getLogger()
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


log: MMPMLogger = MMPMLogger()


def plain_print(msg: str) -> None:
    '''
    Prints message 'msg' without a new line

    Parameters:
        msg (str): The message to be printed to stdout

    Returns:
        None
    '''
    sys.stdout.write(msg)
    sys.stdout.flush()


def error_msg(msg: str) -> None:
    '''
    Displays error message to user, and exits program.

    Parameters:
        msg (str): The error message to be printed to stdout
    '''
    print(colors.B_RED + "ERROR: " + colors.RESET + msg)


def warning_msg(msg: str) -> None:
    '''
    Displays warning message to user and continues program execution.

    Parameters:
        msg (str): The warning message to be printed to stdout

    Returns:
        None
    '''
    print(colors.B_YELLOW + "WARNING: " + colors.RESET + msg)


def run_cmd(command: List[str]) -> tuple:
    '''
    Executes shell command and captures errors

    Parameters:
        command (List[str]): The command string to be executed

    Returns:
        returncode (str): The integer return code of the executed subprocess
        stdout (str): The stdout output of the executed subprocess
        stderr (str): The stderr output of the executed subprocess
    '''

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')


def get_file_path(path: str) -> str:
    '''
    Wrapper method around os.path.exists with ternary operator

    Parameters:
        path (str): File path

    Returns:
        path (str): Either original path, if it exists, or empty string
    '''
    return path if os.path.exists(path) else ''


def open_default_editor(file_path: str) -> None:
    '''
    Method to determine user's text editor. First, checks the EDITOR env
    variable, if not found, attempts to see if 'nano' is installed, and if not,
    lets the system determine the editor using the 'edit' command

    Parameters:
        file_path (str): file path to open with editor

    Returns:
        None
    '''
    log.logger.info(f'Attempting to open {file_path} in users default editor')

    if not file_path:
        error_msg(f'MagicMirror config file not found. Please ensure {MMPM_ENV_VAR} is set properly.')
        sys.exit(1)

    editor: str = os.getenv('EDITOR') if os.getenv('EDITOR') else 'nano'
    return_code, _, _ = run_cmd(['which', editor])

    # fall back to the 'edit' command if you don't even have nano for some reason
    os.system(f'{editor} {file_path}') if not return_code else os.system(f'edit {file_path}')


def handle_installation_process() -> str:
    '''
    Utility method to handle installation/upgrade process of modules. If the
    install is successful, an empty string is returned. The installation
    process relies on the location of the current directory the os library
    detects.

    Parameters:
        None

    Returns:
        string: Empty, or the error message from the failed install
    '''

    if os.path.isfile(os.path.join(os.getcwd(), "package.json")):
        log.logger.info(f'Found package.json in {os.getcwd()}')
        utils.plain_print(colors.RESET + "Found package.json. Attempting to run 'npm install' ... ")
        return_code, _, std_err = utils.run_cmd(['npm', 'install'])

        if return_code:
            log.logger.info(f'Failed with return code {return_code}, and error message {error_msg}')
            print('\n')
            return std_err
        else:
            print(colors.B_GREEN + "done" + colors.RESET)

    if os.path.isfile(os.path.join(os.getcwd(),'Makefile')) or os.path.isfile(os.path.join(os.getcwd(), 'makefile')):
        log.logger.info(f'Found Makefile in {os.getcwd()}')
        utils.plain_print(colors.RESET + "Found Makefile. Attempting to run 'make'... ")
        return_code, _, std_err = utils.run_cmd(['make'])

        if return_code:
            log.logger.info(f'Failed with return code {return_code}, and error message {error_msg}')
            print('\n')
            return std_err
        else:
            print(colors.B_GREEN + "done" + colors.RESET)


    if os.path.isfile(os.path.join(os.getcwd(), 'CMakeLists.txt')):
        log.logger.info(f'Found CMakeLists.txt in {os.getcwd()}')
        utils.plain_print(colors.RESET + "Found CMakeLists.txt. Attempting to run 'cmake' ... ")
        os.system('mkdir -p build')
        os.chdir('build')
        return_code, _, std_err = utils.run_cmd(['cmake', '..'])

        if return_code:
            log.logger.info(f'Failed with return code {return_code}, and error message {error_msg}')
            print('\n')
            return std_err
        else:
            print(colors.B_GREEN + "done" + colors.RESET)

        if os.path.isfile(os.path.join(os.getcwd(),'Makefile')) or os.path.isfile(os.path.join(os.getcwd(), 'makefile')):
            log.logger.info(f'Makefile found in {os.getcwd()} after running cmake')
            utils.plain_print(colors.RESET + "Attempting to run 'make' on Makefile generated by CMake ... ")
            return_code, _, std_err = utils.run_cmd(['make'])
            utils.handle_warnings(return_code, std_err)
            log.logger.info(f"Changing back to parent directory: {os.path.dirname('..')}")
            os.chdir('..')

            if return_code:
                log.logger.info(f'Failed with return code {return_code}, and error message {error_msg}')
                print('\n')
                return std_err
            else:
                log.logger.info(f"Successful execution of 'make'")
                print(colors.B_GREEN + "done" + colors.RESET)

    print('\n')
    log.logger.info(f'Exiting installation handler from {os.getcwd()}')
    return ''
