#!/usr/bin/env python3
import sys
import os
import subprocess
import logging
import logging.handlers
import time
from os.path import join
from typing import List, Optional, Tuple
from re import sub
from mmpm import colors

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
MMPM_CONFIG_DIR: str = join(HOME_DIR, '.config', 'mmpm')
SNAPSHOT_FILE: str = join(MMPM_CONFIG_DIR, 'MagicMirror-modules-snapshot.json')
MMPM_EXTERNAL_SOURCES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-external-sources.json')
EXTERNAL_MODULE_SOURCES: str = 'External Module Sources'


class MMPMLogger():
    '''
    Object used for logging while MMPM is executing. Log files can be found in
    ~/.config/mmpm/log
    '''
    def __init__(self):
        self.log_file: str = os.path.join(MMPM_CONFIG_DIR, 'log', 'mmpm-cli-interface.log')
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


def separator(message) -> None:
    '''
    Used to pretty print a dashed line as long as the provided message

    Parameters:
        message (str): The string that will go under or above the dashed line

    Returns:
        None
    '''
    print(colors.RESET + "-" * len(message), flush=True)


def assert_snapshot_directory() -> bool:
    if not os.path.exists(MMPM_CONFIG_DIR):
        try:
            os.mkdir(MMPM_CONFIG_DIR)
        except OSError:
            error_msg('Failed to create directory for snapshot')
            return False
    return True


def calc_snapshot_timestamps() -> Tuple[float, float]:
    '''
    Calculates the expiration timestamp of the MagicMirror snapshot file

    Parameters:
        None

    Returns:
        Tuple[curr_snap (float), next_snap (float)]: The current timestamp and the exipration timestamp of the MagicMirror snapshot
    '''
    curr_snap = next_snap = None

    if os.path.exists(SNAPSHOT_FILE):
        curr_snap = os.path.getmtime(SNAPSHOT_FILE)
        next_snap = curr_snap + 6 * 60 * 60

    return curr_snap, next_snap


def should_refresh_modules(current_snapshot: float, next_snapshot: float) -> bool:
    '''
    Determines if the MagicMirror snapshot is expired

    Parameters:
        current_snapshot (float): The 'last modified' timestamp from os.path.getmtime
        next_snapshot (float): When the file should 'expire' based on a one day interval

    Returns:
        should_update (bool): If the file is expired and the data needs to be refreshed
    '''
    if not current_snapshot and not next_snapshot:
        return True
    return not os.path.exists(SNAPSHOT_FILE) or next_snapshot - time.time() <= 0.0


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

def sanitize_name(orig_name: str) -> str:
    '''
    Sanitizes a file- or foldername in that it removes bad characters.

    Parameters:
        orig_name (str): A file- or foldername with potential bad characters

    Returns:
        a cleaned version of the file- or foldername
    '''
    return sub('[//]', '', orig_name)

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


def done() -> str:
    '''
    Wrapper method to print green 'done' message

    Parameters:
        None

    Returns:
        message (str): The string 'done' in bright green

    '''
    return colors.B_GREEN + "done" + colors.RESET


def green_plus() -> str:
    '''
    Wrapper method to generate '[+]'

    Parameters:
        None

    Returns:
        message (str): The string '[+]', with the plus symbol being green
    '''
    return colors.RESET + "[" + colors.B_GREEN + "+" + colors.RESET + "]"


def clone(title: str, repo: str, target_dir: str = '') -> Tuple[int, str, str]:
    '''
    Wrapper method to clone a repository with logging information included

    Parameters:
        title (str): The title of the repository
        repo (str): The url of the repository
        target_dir (str): The target_dir of the repository (Optional)

    Returns:
        Tuple[returncode (int), stdout (str), stderr (str)]: Return code, stdout, and stderr of the process
    '''
    # by using "repo.split()", it allows the user to bake in additional commands when making custom sources
    # ie. git clone [repo] -b [branch] [target]
    log.logger.info(f'Cloning {repo} into {target_dir if target_dir else os.path.join(os.getcwd(), title)}')
    plain_print(green_plus() + f" Cloning {title} repository " + colors.RESET)

    command = ['git', 'clone'] + repo.split()

    if target_dir:
        command += [target_dir]

    return run_cmd(command)


def package_requirements_file_exists(file_name: str) -> bool:
    '''
    Case-insensitive search for existing package specification file in current directory

    Parameters:
        file_name (str): The name of the file to search for

    Returns:
        bool: True if the file exists, False if not
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
    plain_print(green_plus() + " Found CMakeLists.txt. Attempting build with 'cmake'")

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
    plain_print(green_plus() + " Found Makefile. Attempting to run 'make'")
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
    plain_print(green_plus() + " Found package.json. Running 'npm install'")
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
    plain_print(green_plus() + "Found Gemfile. Running 'bundle install'")
    return run_cmd(['bundle', 'install'])


def basic_fail_log(error_code: int, error_message: str) -> None:
    '''
    Wrapper method for simple failure logging

    Parameters:
        error_code (int): The return code
        error_message (str): The error message itself

    Returns:
        None
    '''
    log.logger.info(f'Failed with return code {error_code}, and error message {error_message}')


def handle_installation_process() -> str:
    '''
    Utility method to handle installation/upgrade process of modules. If the
    install is successful, an empty string is returned. The installation
    process relies on the location of the current directory the os library
    detects.

    Parameters:
        None

    Returns:
        stderr (str): Success if the string is empty, fail if not
    '''

    if package_requirements_file_exists(PACKAGE_JSON):
        error_code, _, stderr = npm_install()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            print(done())

    if package_requirements_file_exists(GEMFILE):
        error_code, _, stderr = bundle_install()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            print(done())

    if package_requirements_file_exists(MAKEFILE):
        error_code, _, stderr = make()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            print(done())


    if package_requirements_file_exists(CMAKELISTS):
        error_code, _, stderr = cmake()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            print(done())

        if package_requirements_file_exists(MAKEFILE):
            error_code, _, stderr = make()

            if error_code:
                basic_fail_log(error_code, stderr)
                print('\n')
                return str(stderr)
            else:
                print(done())

    print(green_plus() + f' Installation ' + done())
    log.logger.info(f'Exiting installation handler from {os.getcwd()}')
    return ''


def get_pids(process_name: str) -> List[str]:
    '''
    Kills all processes of given name

    Parameters:
        process (str): the name of the process

    Returns:
        processes (List[str]): list of the processes IDs found
    '''

    log.logger.info(f'Getting process IDs for {process_name} proceses')

    pids = subprocess.Popen(['pgrep', process_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = pids.communicate()
    processes = stdout.decode('utf-8')

    log.logger.info(f'Found processes: {processes}')

    return [proc_id for proc_id in processes.split('\n') if proc_id]


def kill_pids_of_process(process: str):
    '''
    Kills all processes of given name

    Parameters:
        process (str): the name of the process

    Returns:
        processes (str): the processes IDs found
    '''
    log.logger.info(f'Killing all processes of type {process}')
    os.system(f'for process in $(pgrep {process}); do kill -9 $process; done')


def kill_magicmirror_processes() -> None:
    '''
    Kills all processes commonly related to MagicMirror

    Parameters:
        None

    Returns:
        None
    '''

    kill_pids_of_process('chromium')
    kill_pids_of_process('node')
    kill_pids_of_process('npm')


def start_magicmirror() -> None:
    '''
    Launches MagicMirror

    Parameters:
       None

    Returns:
        None
    '''
    log.logger.info('Starting MagicMirror')
    original_dir = os.getcwd()
    os.chdir(MAGICMIRROR_ROOT)

    log.logger.info("Running 'npm start' in the background")
    os.system('npm start &')
    os.chdir(original_dir)
