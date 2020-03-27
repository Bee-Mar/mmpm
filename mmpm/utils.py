#!/usr/bin/env python3
import sys
import os
import subprocess
import logging
import logging.handlers
import time
from os.path import join
from typing import List, Optional, Tuple
from mmpm import colors, utils

# String constants
MMPM_ENV_VAR: str = 'MMPM_MAGICMIRROR_ROOT'
MMPM_REPO_URL: str = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL: str = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL: str = 'https://github.com/Bee-Mar/mmpm/wiki'
MAGICMIRROR_MODULES_URL: str = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"
MAKEFILE: str = 'Makefile'
CMAKELISTS: str = 'CMakeLists.txt'
PACKAGE_JSON: str = 'package.json'
GEMFILE: str = 'Gemfile'

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


def separator(message):
    '''
    Used to pretty print a dashed line as long as the provided message

    Parameters:
        message (str): The string that will go under or above the dashed line

    Returns:
        None

    '''
    print(colors.RESET + "-" * len(message), flush=True)


def run_cmd(command: List[str], progress=True) -> Tuple[int, str, str]:
    '''
    Executes shell command and captures errors

    Parameters:
        command (List[str]): The command string to be executed

    Returns:
        Tuple[returncode (int), stdout (str), stderr (str)]
    '''

    log.logger.info(f'Executing process {" ".join(command)}')

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if progress:
        sys.stdout.write(' [')

        while process.poll() is None:
            sys.stdout.write('#')
            time.sleep(.25)
            sys.stdout.flush()

    stdout, stderr = process.communicate()

    if progress:
        sys.stdout.write('] ')

    return process.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')


def get_file_path(path: str) -> str:
    '''
    Wrapper method around os.path.exists with ternary operator

    Parameters:
        path (str): File path

    Returns:
        path (str): Either original path, if it exists, or empty string
    '''
    return path if os.path.exists(path) else ''


def open_default_editor(file_path: str) -> Optional[None]:
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

    editor = os.getenv('EDITOR') if os.getenv('EDITOR') else 'nano'
    error_code, _, _ = run_cmd(['which', editor], progress=False)

    # fall back to the 'edit' command if you don't even have nano for some reason
    os.system(f'{editor} {file_path}') if not error_code else os.system(f'edit {file_path}')


def done():
    ''' Wrapper method to print green 'done' message '''
    print(colors.B_GREEN + "done" + colors.RESET)


def package_requirements_file_exists(file_name: str) -> bool:
    '''
    Case-insensitive search for existing package specification file in current directory

    Parameters:
        file_name (str): The name of the file to search for

    Returns:
        bool: True if found, False if not
    '''
    for name in [file_name, file_name.lower(), file_name.upper()]:
        if os.path.isfile(os.path.join(os.getcwd(), name)):
            return True
    return False


def cmake() -> Tuple[int, str, str]:
    ''' Used to run make from a directory known to have a CMakeLists.txt file

    Parameters:
        None

    Returns:
        Tuple[error_code (int), stdout (str), error_message (str)]

    '''
    log.logger.info(f"Running 'cmake ..' in {os.getcwd()}")
    plain_print(colors.RESET + "Found CMakeLists.txt. Attempting build with 'cmake'")

    run_cmd(['mkdir', '-p', 'build'], progress=False)
    os.chdir('build')
    run_cmd(['rm', '-rf', '*'], progress=False)
    return run_cmd(['cmake', '..'])


def make() -> Tuple[int, str, str]:
    '''
    Used to run make from a directory known to have a Makefile

    Parameters:
        None

    Returns:
        Tuple[error_code (int), stdout (str), error_message (str)]
    '''
    log.logger.info(f"Running 'make' in {os.getcwd()}")
    plain_print(colors.RESET + "Found Makefile. Attempting to run 'make'")
    return run_cmd(['make'])


def npm_install() -> Tuple[int, str, str]:
    '''
    Used to run npm install from a directory known to have a package.json file

    Parameters:
        None

    Returns:
        Tuple[error_code (int), stdout (str), error_message (str)]
    '''
    log.logger.info(f"Running 'npm install' in {os.getcwd()}")
    plain_print("Found package.json. Running 'npm install'")
    return run_cmd(['npm', 'install'])


def bundle_install() -> Tuple[int, str, str]:
    '''
    Used to run npm install from a directory known to have a package.json file

    Parameters:
        None

    Returns:
        Tuple[error_code (int), stdout (str), error_message (str)]
    '''
    log.logger.info(f"Running 'bundle install' in {os.getcwd()}")
    plain_print("Found Gemfile. Running 'bundle install'")
    return run_cmd(['bundle', 'install'])


def basic_fail_log(error_code, error):
    '''
    Wrapper method for simple failure logging

    Parameters:
        None

    Returns:
        None
    '''
    log.logger.info(f'Failed with return code {error_code}, and error message {error}')


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

    if package_requirements_file_exists(PACKAGE_JSON):
        error_code, _, stderr = npm_install()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            done()

    if package_requirements_file_exists(GEMFILE):
        error_code, _, stderr = bundle_install()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            done()

    if package_requirements_file_exists(MAKEFILE):
        error_code, _, stderr = make()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            done()


    if package_requirements_file_exists(CMAKELISTS):
        error_code, _, stderr = cmake()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            done()

        if package_requirements_file_exists(MAKEFILE):
            error_code, _, stderr = make()

            if error_code:
                basic_fail_log(error_code, stderr)
                print('\n')
                return str(stderr)
            else:
                done()

    print('\n')
    log.logger.info(f'Exiting installation handler from {os.getcwd()}')
    return ''
