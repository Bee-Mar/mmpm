#!/usr/bin/env python3
import sys
import os
import subprocess
import time
import datetime
import json
import requests

from typing import List, Optional, Tuple, Dict

import mmpm.color
import mmpm.consts
from pathlib import Path, PosixPath
from mmpm.models import MagicMirrorPackage
from mmpm.logger import MMPMLogger
from mmpm.env import get_env


logger = MMPMLogger.get_logger(__name__)
logger.setLevel(get_env(mmpm.consts.MMPM_LOG_LEVEL))


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


def keyboard_interrupt_log() -> None:
    '''
    Logs info message stating user killed a process with a keyboard interrupt,
    and exits program with error code of 127

    Parameters:
        None

    Returns:
        None
    '''
    print()
    logger.info('User killed process with keyboard interrupt')
    sys.exit(127)


def error_msg(msg: str) -> None:
    '''
    Logs error message, displays error message to user, and continues program execution

    Parameters:
        msg (str): The error message to be printed to stdout

    Returns:
        None
    '''
    logger.error(msg)
    print(mmpm.color.bright_red('ERROR:'), msg)


def warning_msg(msg: str) -> None:
    '''
    Logs warning message, displays warning message to user, and continues program execution

    Parameters:
        msg (str): The warning message to be printed to stdout

    Returns:
        None
    '''
    logger.warning(msg)
    print(mmpm.color.bright_yellow('WARNING:'), msg)


def fatal_msg(msg: str) -> None:
    '''
    Logs fatal message, displays fatal message to user, and halts program execution

    Parameters:
        msg (str): The fatal error message to be printed to stdout

    Returns:
        None
    '''
    logger.critical(msg)
    print(mmpm.color.bright_red('FATAL:'), msg)
    sys.exit(127)


def env_variables_error_msg(preamble: str = '') -> None:
    '''
    Helper method to log and display an error relating to a common issue of not
    setting environment variables properly

    Parameters:
        preamble (str): an optional argument to provide more specific error messaging

    Returns:
        None
    '''
    msg: str = mmpm.consts.MMPM_ENV_ERROR_MESSAGE

    if preamble:
        msg = f'{preamble} {msg}'

    error_msg(msg)


def env_variables_fatal_msg(preamble: str = '') -> None:
    '''
    Helper method to log and display a fatal error relating to a common issue of not
    setting environment variables properly

    Parameters:
        preamble (str): an optional argument to provide more specific error messaging

    Returns:
        None
    '''
    msg: str = mmpm.consts.MMPM_ENV_ERROR_MESSAGE

    if preamble:
        msg = f'{preamble} {msg}'

    fatal_msg(msg)


def assert_required_defaults_exist() -> None:
    '''
    Runs at the start of each `mmpm` command executed to ensure all the default
    files exist, and if they do not, they are created.

    Parameters:
        None

    Returns:
        None
    '''

    mmpm.consts.MMPM_CONFIG_DIR.mkdir(exist_ok=True)

    for data_file in mmpm.consts.MMPM_REQUIRED_DATA_FILES:
        data_file.touch()

    current_env: dict = {}

    with open(mmpm.consts.MMPM_ENV_FILE, 'r', encoding="utf-8") as env:
        try:
            current_env = json.load(env)
        except json.JSONDecodeError as error:
            logger.error(str(error))

    for key, value in mmpm.consts.MMPM_DEFAULT_ENV.items():
        if key not in current_env:
            current_env[key] = value

    with open(mmpm.consts.MMPM_ENV_FILE, 'w', encoding="utf-8") as env:
        json.dump(current_env, env, indent=2)



def run_cmd(command: List[str], progress=True, background=False) -> Tuple[int, str, str]:
    '''
    Executes shell command and captures errors

    Parameters:
        command (List[str]): The command string to be executed

    Returns:
        Tuple[returncode (int), stdout (str), stderr (str)]
    '''

    logger.info(f'Executing process `{" ".join(command)}` in foreground')

    if background:
        logger.info(f'Executing process `{" ".join(command)}` in background')
        subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return

    with subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        symbols = ['\u25DC', '\u25DD', '\u25DE', '\u25DF']

        if progress:
            def __spinner__():
                while True:
                    for symbol in symbols:
                        yield symbol

            spinner = __spinner__()

            sys.stdout.write(' ')

            while process.poll() is None:
                sys.stdout.write(next(spinner))
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write('\b')

        stdout, stderr = process.communicate()

        return process.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')


def open_default_editor(path_to_file: str) -> Optional[None]:
    '''
    Method to determine user's text editor. First, checks the EDITOR env
    variable, if not found, attempts to see if 'nano' is installed, and if not,
    lets the system determine the editor using the 'edit' command

    Parameters:
        path_to_file (str): file path to open with editor

    Returns:
        None
    '''
    logger.info(f'Attempting to open {path_to_file} in users default editor')

    if not os.path.exists(path_to_file):
        try:
            warning_msg(f'{path_to_file} does not exist. Creating the directory and empty file')
            Path('/'.join(path_to_file.split('/')[:-1])).mkdir(parents=True, exist_ok=True)
            Path(path_to_file).touch(mode=0o664, exist_ok=True)
        except OSError as error:
            fatal_msg(f'Unable to create {path_to_file}: {str(error)}')

    editor = os.getenv('EDITOR') if os.getenv('EDITOR') else 'nano'
    error_code, _, _ = run_cmd(['which', editor], progress=False)

    # fall back to the 'edit' command if you don't even have nano for some reason
    os.system(f'{editor} {path_to_file}') if not error_code else os.system(f'edit {path_to_file}')


def basic_fail_log(error_code: int, error_message: str) -> None:
    '''
    Wrapper method for simple failure logging

    Parameters:
        error_code (int): The return code
        error_message (str): The error message itself

    Returns:
        None
    '''
    logger.info(f'Failed with return code {error_code}, and error message {error_message}')


def get_pids(process_name: str) -> List[str]:
    '''
    Kills all processes of given name

    Parameters:
        process (str): the name of the process

    Returns:
        processes (List[str]): list of the processes IDs found
    '''

    logger.info(f'Getting process IDs for {process_name} proceses')

    with subprocess.Popen(['pgrep', process_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as pids:
        stdout, _ = pids.communicate()
        processes = stdout.decode('utf-8')

        logger.info(f'Found processes: {processes}')

        return [proc_id for proc_id in processes.split('\n') if proc_id]


def kill_pids_of_process(process: str) -> None:
    '''
    Kills all processes of given name

    Parameters:
        process (str): the name of the process

    Returns:
        processes (str): the processes IDs found
    '''
    logger.info(f'Killing all processes of type {process}')
    plain_print(f'{mmpm.consts.GREEN_PLUS} stopping MagicMirror electron processes ')
    os.system(f'for process in $(pgrep {process}); do kill -9 $process; done')
    print(f'{mmpm.consts.GREEN_CHECK_MARK}')



# TODO: remove the assume_yes
def prompt_user(user_prompt: str, valid_ack: List[str] = ['yes', 'y'], valid_nack: List[str] = ['no', 'n'], assume_yes: bool = False) -> bool:
    '''
    Prompts user with the `user_prompt` until a response matches a value in the
    `valid_ack` or `valid_nack` lists, or a KeyboardInterrupt is caught. If
    `assume_yes` is true, the `user_prompt` is printed followed by a 'yes', and
    function returns True

    Parameters:
        user_prompt (str): the text that will be presented to the user
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
        print()
        return False

    return False


def fatal_invalid_additional_arguments(subcommand: str) -> None:
    '''
    Helper method to return a standardized error message when the user provides too many arguments

    Parameters:
        subcommand (str): the name of the mmpm subcommand

    Returns:
        None
    '''
    fatal_msg(f'`mmpm {subcommand}` does not accept additional arguments. See `mmpm {subcommand} --help`')


def fatal_invalid_option(subcommand: str) -> None:
    '''
    Helper method to return a standardized error message when the user provides an invalid option

    Parameters:
        subcommand (str): the name of the mmpm subcommand

    Returns:
        None
    '''
    fatal_msg(f'Invalid option supplied to `mmpm {subcommand}`. See `mmpm {subcommand} --help`')



def fatal_too_many_options(args) -> None:
    '''
    Helper method to return a standardized error message when the user provides too many options

    Parameters:
        subcommand (str): the name of the mmpm subcommand

    Returns:
        None
    '''

    if 'title_only' in args.__dict__:
        message: str = f'`mmpm {args.subcmd}` only accepts one optional argument in addition to `--title-only`. See `mmpm {args.subcmd} --help`'
    else:
        message = f'`mmpm {args.subcmd}` only accepts one optional argument. See `mmpm {args.subcmd} --help`'
    fatal_msg(message)


def fatal_no_arguments_provided(subcommand: str) -> None:
    '''
    Helper method to return a standardized error message when the user provides no arguments

    Parameters:
        subcommand (str): the name of the mmpm subcommand

    Returns:
        None
    '''
    fatal_msg(f'no arguments provided. See `mmpm {subcommand} --help` for usage')


def assert_valid_input(prompt: str, forbidden_responses: List[str] = [], reason: str = '') -> str:
    '''
    Continues to prompt user with given input until the response provided is of
    non-zero length and not found in the list forbidden responses

    Parameters:
        prompt (str): the prompt given to the user
        forbidden_responses (List[str]): a list of responses the user may not supply
        reason (str): a reason why the user may not supply one of the 'forbidden_responses'

    Returns:
        user_response (str): valid, user provided input
    '''
    while True:
        user_response = input(prompt)
        if not user_response: # pylint: disable=no-else-continue
            warning_msg('A non-empty response must be given')
            continue
        elif user_response in forbidden_responses:
            warning_msg(f'Invalid response, {user_response} {reason}')
            continue
        return user_response



def list_of_dict_to_list_of_magicmirror_packages(list_of_dict: List[dict]) -> List[MagicMirrorPackage]:
    '''
    Converts a list of dictionary contents to a list of MagicMirrorPackage objects

    Parameters:
        list_of_dict (List[dict]): a list of dictionaries representing MagicMirrorPackage data

    Returns:
        packages (List[MagicMirrorPackage]): a list of MagicMirrorPackage objects
    '''

    return [MagicMirrorPackage(**pkg) for pkg in list_of_dict]


def assert_one_option_selected(args) -> bool:
    '''
    Determines if more than one option has been selected by a user for use with a subcommand

    Parameters:
        args (argparse.Namespace): an argparse Namespace object containing chosen arguments

    Returns:
        yes (bool): True if one option is selected, False if more than one is selected
    '''
    args = args.__dict__
    # comparing to True, because some of arguments are not booleans
    return not len([args[option] for option in args if args[option] == True and option != 'title_only']) > 1


def safe_get_request(url: str) -> requests.Response:
    '''
    Wrapper method around the 'requests.get' call, containing a try, except block

    Parameters:
        url (str): the url used for the API request

    Returns:
        response (requests.Response): the Reponse object, which may be empty if the request failed
    '''
    try:
        data = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as error:
        logger.error(str(error))
        return requests.Response()
    return data



def is_magicmirror_running() -> bool:
    '''
    The status of MagicMirror running is determined by the presence of certain
    types of processes running. If those are found, it's assumed to be running,
    otherwise, not

    Parameters:
        None

    Returns:
        running (bool): True if running, False if not
    '''
    return bool(get_pids('electron') or get_pids('pm2'))


def socketio_client_factory():
    '''
    Wrapper method to return a consistent paramaterized socketio.Client object

    Parameters:
        None

    Returns:
        client (socketio.Client): the socketio Client object
    '''

    import socketio # socketio is a very slow import, so only doing it when absolutely necessary
    client = socketio.Client()

    try:
        client = socketio.Client(logger=log, reconnection=True, request_timeout=3000)
    except Exception:
        error_msg('Failed to connect to MagicMirror websocket. Is MagicMirror running?')
    return client


def socketio_client_disconnect(client) -> bool:
    '''
    Wrapper method to include try/except block for handling any issues encountered during disconnect

    Parameters:
        client (socketio.Client): the client object instance

    Returns:
        success (bool): True on success, False if not
    '''
    try:
        logger.info('attempting to disconnect from MagicMirror websocket')
        client.disconnect()
    except (OSError, BrokenPipeError, Exception):
        logger.info('encountered OSError when disconnecting from websocket, ignoring')
    return True



def reset_available_upgrades_for_environment(env: str) -> bool:
    '''
    Resets a given MagicMirror installation environment within the ~/.config/mmpm/mmpm-available-upgrades.json to have no upgrades available.

    Parameters:
        env (str): the path of a MagicMirror installation

    Returns:
        success (bool): True on success, False on failure
    '''

    upgrades: dict = {}

    logger.info(f'Resetting available upgrades for {env}')

    with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'r', encoding="utf-8") as available_upgrades:
        try:
            upgrades = json.load(available_upgrades)
        except (json.JSONDecodeError, OSError) as error:
            logger.error(f'Encountered error when reading {mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE}: {str(error)}')
            upgrades = {mmpm.consts.MMPM: False, env: {mmpm.consts.PACKAGES: [], mmpm.consts.MAGICMIRROR: False}}

    try:
        with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w', encoding="utf-8") as available_upgrades:
            upgrades[env] = {mmpm.consts.PACKAGES: [], mmpm.consts.MAGICMIRROR: False}
            json.dump(upgrades, available_upgrades)

    except OSError as error:
        logger.error(str(error))
        return False

    return True


def systemctl(subcmd: str, services: List[str] = []) -> subprocess.CompletedProcess:
    '''
    A wrapper around a subprocess.run call that is used within the
    `mmpm.core.install_mmpm_gui` and `mmpm.core.remove_mmpm_gui` functions.
    Used to keep things more DRY.

    Parameters:
        subcmd (str): the systemctl subcommand, ie. stop, start, restart, status, etc
        services (List[str]): the systemd service(s) being queried

    Returns:
        process (subprocess.CompletedProcess): the completed subprocess following execution
    '''
    return subprocess.run(['sudo', 'systemctl', subcmd] + services, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def log_gui_install_error_and_prompt_for_removal(proc: subprocess.CompletedProcess, message: str) -> bool:
    '''
    A utility method to handle logging during installtion of the MMPM GUI, in an attempt to keep things more DRY.

    Parameters:
        proc (subprocess.CompletedProcess): the subprocess that was executed
        message (str): the error message that will be displayed

    Returns:
        yes (bool): the response of the user, whether or not to remove the MMPM GUI following a failed install
    '''
    print(mmpm.consts.RED_X)
    logger.critical(f"{proc.stderr.decode('utf-8')}\n{proc.stdout.decode('utf-8')}")
    mmpm.utils.error_msg(f'{message}. See `mmpm log` for details')
    return prompt_user('Remove the MMPM GUI?')


def background_timer_thread(stop_event, arg, client): # pylint: disable=unused-argument
    '''
    Excecuted as a background thread when the user attemps to call `mmpm mm-ctl
    --status`, or the hide/show options. At 5 seconds, the user is warned, and
    at 10 seconds the connection is closed.

    Parameters:
        stop_event (threading.Event): the thread event object that allows the calling
                                      process to communicate with the thread

        arg (str): the trigger input to let the thread know it has been communicated with
        client (socketio.Client): the client object that was used to open the connection

    Returns:
        None
    '''
    timer: int = 10

    while not stop_event.wait(1):
        timer -= 1
        if timer == 5:
            logger.warning('Reached fith second of 10 second timeout for connecting to MagicMirror websocket')
            print('\nIs MagicMirror running, and are MMPM env variables set properly? If MagicMirror is a Docker image, open MagicMirror in your browser to activate the connection.')
        if not timer:
            logger.warning('Reached 10 second timeout for connecting to MagicMirror websocket. Closing connection')
            print('10 second timeout reached, closing connection.')
            break

    socketio_client_disconnect(client)
