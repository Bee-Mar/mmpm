#!/usr/bin/env python3
import sys
import os
import subprocess
from multiprocessing import cpu_count
from collections import Counter, defaultdict
import logging
import logging.handlers
import time
from os.path import join
from typing import List, Optional, Tuple, IO, Any
from re import sub
from mmpm import colors, consts
from shutil import which
from ctypes import cdll, c_char_p, c_int, POINTER, c_bool


class MMPMLogger():
    '''
    Object used for logging while MMPM is executing. Log files can be found in
    ~/.config/mmpm/log
    '''
    def __init__(self):
        self.log_file: str = consts.MMPM_LOG_FILE
        self.log_format: str = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s'
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
    Displays error message to user, and continues program execution.

    Parameters:
        msg (str): The error message to be printed to stdout
    '''
    print(colored_text(colors.B_RED, "ERROR:"), msg)


def warning_msg(msg: str) -> None:
    '''
    Displays warning message to user and continues program execution.

    Parameters:
        msg (str): The warning message to be printed to stdout

    Returns:
        None
    '''
    print(colored_text(colors.B_YELLOW, "WARNING:"), msg)


def fatal_msg(msg: str) -> None:
    '''
    Displays fatal error message to user and halts program execution

    Parameters:
        msg (str): The fatal error message to be printed to stdout

    Returns:
        None
    '''
    print(colored_text(colors.B_RED, "FATAL:"), msg)
    sys.exit(127)


def separator(message) -> None:
    '''
    Used to pretty print a dashed line as long as the provided message

    Parameters:
        message (str): The string that will go under or above the dashed line

    Returns:
        None
    '''
    print(colored_text(colors.RESET, "-" * len(message)), flush=True)


def assert_snapshot_directory() -> bool:
    if not os.path.exists(consts.MMPM_CONFIG_DIR):
        try:
            os.mkdir(consts.MMPM_CONFIG_DIR)
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

    if os.path.exists(consts.SNAPSHOT_FILE):
        curr_snap = os.path.getmtime(consts.SNAPSHOT_FILE)
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
    return not os.path.exists(consts.SNAPSHOT_FILE) or next_snapshot - time.time() <= 0.0


def run_cmd(command: List[str], progress=True) -> Tuple[int, str, str]:
    '''
    Executes shell command and captures errors

    Parameters:
        command (List[str]): The command string to be executed

    Returns:
        Tuple[returncode (int), stdout (str), stderr (str)]
    '''

    log.logger.info(f'Executing process `{" ".join(command)}`')

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
        fatal_msg(f'MagicMirror config file not found. Please ensure {consts.MMPM_ENV_VARS[consts.MMPM_MAGICMIRROR_ROOT]} is set properly.')
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
    return colored_text(colors.B_GREEN, "done")


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
    plain_print(green_plus() + f" {colored_text(colors.N_CYAN, f'Cloning {title} repository')} " + colors.RESET)

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
    log.logger.info(f"Running 'make -j {cpu_count()}' in {os.getcwd()}")
    plain_print(green_plus() + f" Found Makefile. Attempting to run 'make -j {cpu_count()}'")
    return run_cmd(['make', '-j', f'{cpu_count()}'])


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


def install_module(module: dict, target: str, modules_dir: str, assume_yes: bool = False) -> bool:
    '''
    Used to display more detailed information that presented in normal search results

    Parameters:
        modules (dict): MagicMirror modules database snapshot
        modules_to_install (List[str]): list of modules provided by user through command line arguments

    Returns:
        installation_candidates (List[dict]): list of modules whose module names match those of the modules_to_install
    '''

    error_code, _, stderr = clone(module[consts.TITLE], module[consts.REPOSITORY], target)

    if error_code:
        warning_msg("\n" + stderr)
        return False

    print(done())

    os.chdir(target)
    error: str = install_dependencies()
    os.chdir('..')

    if error:
        error_msg(error)
        failed_install_path = os.path.join(modules_dir, module[consts.TITLE])

        message: str = f"Failed to install {module[consts.TITLE]} at '{failed_install_path}'"

        if assume_yes:
            message = f'{message}. Removing directory due to --yes flag'
            error_msg(message)
            log.logger.info(message)
            return False

        log.logger.info(message)

        yes = prompt_user(
            f"{colored_text(colors.B_RED, 'ERROR:')} Failed to install {module[consts.TITLE]} at '{failed_install_path}'. Remove the directory?",
            assume_yes=assume_yes
        )

        if yes:
            message = f"User chose to remove {module[consts.TITLE]} at '{failed_install_path}'"
            run_cmd(['rm', '-rf', failed_install_path], progress=False)
            print(f"\nRemoved '{failed_install_path}'\n")
        else:
            message = f"Keeping {module[consts.TITLE]} at '{failed_install_path}'"
            print(f'\n{message}\n')
            log.logger.info(message)

        return False

    return True


def install_dependencies() -> str:
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

    if package_requirements_file_exists(consts.PACKAGE_JSON):
        error_code, _, stderr = npm_install()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            print(done())

    if package_requirements_file_exists(consts.GEMFILE):
        error_code, _, stderr = bundle_install()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            print(done())

    if package_requirements_file_exists(consts.MAKEFILE):
        error_code, _, stderr = make()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            print(done())


    if package_requirements_file_exists(consts.CMAKELISTS):
        error_code, _, stderr = cmake()

        if error_code:
            basic_fail_log(error_code, stderr)
            print('\n')
            return str(stderr)
        else:
            print(done())

        if package_requirements_file_exists(consts.MAKEFILE):
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

    processes = ['node', 'npm', 'electron']

    log.logger.info('Killing processes associated with MagicMirror: {processes}')

    for process in processes:
        kill_pids_of_process(process)


def display_table(table, rows: int, columns: int) -> None:
    '''
    Calls the shared mmpm library to print the contents of a provided matrix

    Parameters:
        data: List[bytes]

    Returns:
        None
    '''

    libmmpm = cdll.LoadLibrary(consts.LIBMMPM_SHARED_OBJECT)

    __display_table__ = libmmpm.display_table
    __display_table__.argtypes = [POINTER(POINTER(c_char_p)), c_int, c_int]
    __display_table__.restype = None
    __display_table__(table, rows, columns)


def allocate_table_memory(rows: int, columns: int):
    '''
    Calls the shared mmpm library to allocate memory for a matrix `rows` times
    `columns` times `sizeof(char*)`, and returns a pointer to the memory

    Parameters:
        data: List[bytes]

    Returns:
        table (POINTER(POINTER(c_char_p))): the allocated memory
    '''
    libmmpm = cdll.LoadLibrary(consts.LIBMMPM_SHARED_OBJECT)

    allocate_table_memory = libmmpm.allocate_table_memory
    allocate_table_memory.argtypes = [c_int, c_int]
    allocate_table_memory.restype = POINTER(POINTER(c_char_p))

    table = allocate_table_memory(rows, columns)
    return table


def to_bytes(string: str) -> bytes:
    '''
    Wrapper method to convert a string to UTF-8 encoded bytes

    Parameters:
        string (str): The text that will be UTF-8 encoded

    Returns:
        message (str): The UTF-8 encoded string

    '''
    return bytes(string, 'utf-8')


def colored_text(color: str, message: str) -> str:
    '''
    Returns the `color` concatenated with the `message` string

    Parameters:
        message (str): The text that will be displayed in the `color`
        color (str): The colorama color

    Returns:
        message (str): The original text concatenated with the colorama color
    '''
    return (color + message + colors.RESET)


def prompt_user(user_prompt: str, valid_ack: List[str] = ['yes', 'y'], valid_nack: List[str] = ['no', 'n'], assume_yes: bool = False) -> bool:
    '''
    Prompts user with the `user_prompt` until a response matches a value in the
    `valid_ack` or `valid_nack` lists, or a KeyboardInterrupt is caught. If
    `assume_yes` is true, the `user_prompt` is printed followed by a 'yes', and
    function returns True

    Parameters:
        user_prompt (str): The text that will be presented to the user
        valid_ack (List[str]): valid 'yes' responses
        valid_nack (List[str]): valid 'no' responses
        assume_yes (bool): if True, the `user_prompt` is printed followed by 'yes'

    Returns:
        response (bool): True if the response is in the `valid_ack` list, False if in `valid_nack` or KeyboardInterrupt
    '''
    if assume_yes:
        print(f"{user_prompt} [{'/'.join(valid_ack)}] or [{'/'.join(valid_nack)}]: yes")
        return True

    response = None

    try:
        while response not in (valid_ack, valid_nack):
            response = input(f"{user_prompt} [{'/'.join(valid_ack)}] or [{'/'.join(valid_nack)}]: ")

            if response in valid_ack:
                return True
            elif response in valid_nack:
                return False
            else:
                warning_msg(f"Respond with [{'/'.join(valid_ack)}] or [{'/'.join(valid_nack)}]")

    except KeyboardInterrupt:
        return False

    return False


def unknown_additional_arguments(subcommand: str) -> str:
    '''
    Helper method to return a standardized error message when the user provides too many arguments

    Parameters:
        subcommand (str): the name of the mmpm subcommand

    Returns:
        message (str): the standardized error message

    '''
    return f'`mmpm {subcommand}` does not accept additional arguments. See `mmpm {subcommand} --help`'
