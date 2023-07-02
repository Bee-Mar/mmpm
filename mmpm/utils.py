#!/usr/bin/env python3
import sys
import os
import subprocess
import time
import datetime
import json
import requests
import socket
from mmpm.constants import paths, symbols
from mmpm.logger import MMPMLogger
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path, PosixPath


logger = MMPMLogger.get_logger(__name__)


def get_host_ip() -> str:
    address: str = "localhost"

    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        _socket.connect(("8.8.8.8", 80))
        address = _socket.getsockname()[0]
    except socket.gaierror as error:
        logger.error(f"Failed to determine host IP address: {error}")
    finally:
        _socket.close()

    return address


def run_cmd(command: List[str], progress=True, background=False) -> Tuple[int, str, str]:
    '''
    Executes shell command and captures errors

    Parameters:
        command (List[str]): The command string to be executed

    Returns:
        Tuple[returncode (int), stdout (str), stderr (str)]
    '''

    logger.info(f'Executing process `{" ".join(command)}`')

    if background:
        logger.info(f'Executing process `{" ".join(command)}` in background')
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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


def edit(file: PosixPath) -> Optional[None]:
    '''
    Checks if the requested file exists, and if not, the file is created. Then, the 'edit'
    command is used to open the file.

    Parameters:
        file (PosixPath): file path to open with 'edit' command

    Returns:
        None
    '''

    if not file.exists():
        try:
            logger.msg.warning(f'{file} does not exist. Creating file.')
            file.parent.mkdir(parents=True, exist_ok=True)
            file.touch(mode=0o664, exist_ok=True)
        except OSError as error:
            logger.msg.fatal(f'Unable to create {file}: {str(error)}')

    logger.info(f'Opening {file} for user to edit')
    command = os.getenv("EDITOR", os.getenv("VISUAL", "edit"))
    os.system(f'{command} {file}')


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
    os.system(f'for process in $(pgrep {process}); do kill -9 $process; done')
    print(f'{symbols.GREEN_CHECK_MARK}')



def prompt(user_prompt: str, valid_ack: List[str] = ['yes', 'y'], valid_nack: List[str] = ['no', 'n']) -> bool:
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
    response = None

    try:
        while response not in (valid_ack, valid_nack):
            response = input(f"{user_prompt} [{'/'.join(valid_ack)}] or [{'/'.join(valid_nack)}]: ")

            if response in valid_ack:
                return True
            elif response in valid_nack:
                return False
            else:
                logger.msg.warning(f"Respond with [{'/'.join(valid_ack)}] or [{'/'.join(valid_nack)}]")

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
    logger.msg.fatal(f'`mmpm {subcommand}` does not accept additional arguments. See `mmpm {subcommand} --help`')


def fatal_invalid_option(subcommand: str) -> None:
    '''
    Helper method to return a standardized error message when the user provides an invalid option

    Parameters:
        subcommand (str): the name of the mmpm subcommand

    Returns:
        None
    '''
    logger.msg.fatal(f'Invalid option supplied to `mmpm {subcommand}`. See `mmpm {subcommand} --help`')



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
    logger.msg.fatal(message)


def fatal_no_arguments_provided(subcommand: str) -> None:
    '''
    Helper method to return a standardized error message when the user provides no arguments

    Parameters:
        subcommand (str): the name of the mmpm subcommand

    Returns:
        None
    '''
    logger.msg.fatal(f'no arguments provided. See `mmpm {subcommand} --help` for usage')


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
            logger.msg.warning('A non-empty response must be given')
            continue
        elif user_response in forbidden_responses:
            logger.msg.warning(f'Invalid response, {user_response} {reason}')
            continue
        return user_response



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



def systemctl(subcmd: str, services: List[str] = []) -> subprocess.CompletedProcess:
    '''
    A wrapper around a subprocess.run call to target systemctl

    Parameters:
        subcmd (str): the systemctl subcommand, ie. stop, start, restart, status, etc
        services (List[str]): the systemd service(s) being queried

    Returns:
        process (subprocess.CompletedProcess): the completed subprocess following execution
    '''
    return subprocess.run(['sudo', 'systemctl', subcmd] + services, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# TODO: maybe still need this?
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
