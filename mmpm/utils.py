#!/usr/bin/env python3
import sys
import os
import subprocess
import time
import datetime
import json
import pathlib
import requests

from logging import Logger
from typing import List, Optional, Tuple, Dict

import mmpm.color
import mmpm.consts
import mmpm.models

MagicMirrorPackage = mmpm.models.MagicMirrorPackage
MMPMLogger = mmpm.models.MMPMLogger

log: Logger = MMPMLogger().logger # type: ignore


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
    log.info('User killed process with keyboard interrupt')
    sys.exit(127)


def error_msg(msg: str) -> None:
    '''
    Logs error message, displays error message to user, and continues program execution

    Parameters:
        msg (str): The error message to be printed to stdout

    Returns:
        None
    '''
    log.error(msg)
    print(mmpm.color.bright_red('ERROR:'), msg)


def warning_msg(msg: str) -> None:
    '''
    Logs warning message, displays warning message to user, and continues program execution

    Parameters:
        msg (str): The warning message to be printed to stdout

    Returns:
        None
    '''
    log.warning(msg)
    print(mmpm.color.bright_yellow('WARNING:'), msg)


def fatal_msg(msg: str) -> None:
    '''
    Logs fatal message, displays fatal message to user, and halts program execution

    Parameters:
        msg (str): The fatal error message to be printed to stdout

    Returns:
        None
    '''
    log.critical(msg)
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

    os.system(f'mkdir -p {mmpm.consts.MMPM_CONFIG_DIR}')

    for data_file in mmpm.consts.MMPM_REQUIRED_DATA_FILES:
        os.system(f'touch {data_file}')

    current_env: dict = {}

    with open(mmpm.consts.MMPM_ENV_FILE, 'r', encoding="utf-8") as env:
        try:
            current_env = json.load(env)
        except json.JSONDecodeError as error:
            log.error(str(error))

    for key, value in mmpm.consts.MMPM_DEFAULT_ENV.items():
        if key not in current_env:
            current_env[key] = value

    with open(mmpm.consts.MMPM_ENV_FILE, 'w', encoding="utf-8") as env:
        json.dump(current_env, env, indent=2)


def calculate_expiration_date_of_database() -> Tuple[float, float]:
    '''
    Calculates the expiration timestamp of the MagicMirror database file. The
    database is considered expired if it is 24 hours or older

    Parameters:
        None

    Returns:
        Tuple[creation_date (float), expiration_date (float)]: The current timestamp and the exipration timestamp of the MagicMirror database
    '''
    creation_date = expiration_date = None

    if os.path.exists(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE):
        creation_date = os.path.getmtime(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE)
        expiration_date = creation_date + 24 * 60 * 60

    return creation_date, expiration_date


def should_refresh_database(creation_date: float, expiration_date: float) -> bool:
    '''
    Determines if the MagicMirror database is expired

    Parameters:
        creation_date (float): The 'last modified' timestamp from os.path.getmtime
        expiration_date (float): When the file should 'expire' based on a 12 hour interval

    Returns:
        should_update (bool): If the file is expired and the data needs to be refreshed
    '''
    return (not creation_date and not expiration_date) \
            or (not bool(os.stat(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE).st_size) or expiration_date - time.time() <= 0.0)


def run_cmd(command: List[str], progress=True, background=False) -> Tuple[int, str, str]:
    '''
    Executes shell command and captures errors

    Parameters:
        command (List[str]): The command string to be executed

    Returns:
        Tuple[returncode (int), stdout (str), stderr (str)]
    '''

    log.info(f'Executing process `{" ".join(command)}` in foreground')

    with subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        if background:
            log.info(f'Executing process `{" ".join(command)}` in background')
            return process.returncode, str(), str()

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


def sanitize_name(orig_name: str) -> str:
    '''
    Sanitizes a file- or foldername in that it removes bad characters.

    Parameters:
        orig_name (str): A file- or foldername with potential bad characters

    Returns:
        a cleaned version of the file- or foldername
    '''
    from re import sub
    return sub('[//]', '', orig_name)


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
    log.info(f'Attempting to open {path_to_file} in users default editor')

    if not os.path.exists(path_to_file):
        try:
            warning_msg(f'{path_to_file} does not exist. Creating the directory and empty file')
            pathlib.Path('/'.join(path_to_file.split('/')[:-1])).mkdir(parents=True, exist_ok=True)
            pathlib.Path(path_to_file).touch(mode=0o664, exist_ok=True)
        except OSError as error:
            fatal_msg(f'Unable to create {path_to_file}: {str(error)}')

    editor = os.getenv('EDITOR') if os.getenv('EDITOR') else 'nano'
    error_code, _, _ = run_cmd(['which', editor], progress=False)

    # fall back to the 'edit' command if you don't even have nano for some reason
    os.system(f'{editor} {path_to_file}') if not error_code else os.system(f'edit {path_to_file}')


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
    log.info(f'Cloning {repo} into {target_dir if target_dir else os.path.join(os.getcwd(), title)}')
    plain_print(f"{mmpm.consts.GREEN_DASHES} Cloning repository")

    # by using "repo.split()", it allows the user to bake in additional commands when making custom sources
    # ie. git clone [repo] -b [branch] [target]
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
    log.info(f"Running 'cmake ..' in {os.getcwd()}")
    plain_print(f"{mmpm.consts.GREEN_DASHES} Found CMakeLists.txt. Building with `cmake`")

    os.system('mkdir -p build')
    os.chdir('build')
    os.system('rm -rf *')
    return run_cmd(['cmake', '..'])


def make() -> Tuple[int, str, str]:
    '''
    Used to run make from a directory known to have a Makefile

    Parameters:
        None

    Returns:
        Tuple[error_code (int), stdout (str), error_message (str)]
    '''
    from multiprocessing import cpu_count

    log.info(f"Running 'make -j {cpu_count()}' in {os.getcwd()}")
    plain_print(f"{mmpm.consts.GREEN_DASHES} Found Makefile. Running `make -j {cpu_count()}`")
    return run_cmd(['make', '-j', f'{cpu_count()}'])


def npm_install() -> Tuple[int, str, str]:
    '''
    Used to run npm install from a directory known to have a package.json file

    Parameters:
        None

    Returns:
        Tuple[error_code (int), stdout (str), error_message (str)]
    '''
    log.info(f"Running 'npm install' in {os.getcwd()}")
    plain_print(f"{mmpm.consts.GREEN_DASHES} Found package.json. Running `npm install`")
    return run_cmd(['npm', 'install'])


def bundle_install() -> Tuple[int, str, str]:
    '''
    Used to run npm install from a directory known to have a package.json file

    Parameters:
        None

    Returns:
        Tuple[error_code (int), stdout (str), error_message (str)]
    '''
    log.info(f"Running 'bundle install' in {os.getcwd()}")
    plain_print(f"{mmpm.consts.GREEN_DASHES} Found Gemfile. Running `bundle install`")
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
    log.info(f'Failed with return code {error_code}, and error message {error_message}')


def install_dependencies(directory: str) -> str:
    '''
    Utility method that detects package.json, Gemfiles, Makefiles, and
    CMakeLists.txt files, and handles the build process for each of the
    previously mentioned files. If the install is successful, an empty string
    is returned. The installation process relies on the location of the current
    directory the os library detects.

    Parameters:
        directory (str): the root directory of the package

    Returns:
        stderr (str): success if the string is empty, fail if not
    '''

    os.chdir(directory)

    if package_requirements_file_exists(mmpm.consts.PACKAGE_JSON):
        error_code, _, stderr = npm_install()

        if error_code:
            print(mmpm.consts.RED_X)
            basic_fail_log(error_code, stderr)
            return str(stderr)
        else:
            print(mmpm.consts.GREEN_CHECK_MARK)

    if package_requirements_file_exists(mmpm.consts.GEMFILE):
        error_code, _, stderr = bundle_install()

        if error_code:
            print(mmpm.consts.RED_X)
            basic_fail_log(error_code, stderr)
            return str(stderr)
        else:
            print(mmpm.consts.GREEN_CHECK_MARK)

    if package_requirements_file_exists(mmpm.consts.MAKEFILE):
        error_code, _, stderr = make()

        if error_code:
            print(mmpm.consts.RED_X)
            basic_fail_log(error_code, stderr)
            return str(stderr)
        else:
            print(mmpm.consts.GREEN_CHECK_MARK)


    if package_requirements_file_exists(mmpm.consts.CMAKELISTS):
        error_code, _, stderr = cmake()

        if error_code:
            print(mmpm.consts.RED_X)
            basic_fail_log(error_code, stderr)
            return str(stderr)
        else:
            print(mmpm.consts.GREEN_CHECK_MARK)

        if package_requirements_file_exists(mmpm.consts.MAKEFILE):
            error_code, _, stderr = make()

            if error_code:
                print(mmpm.consts.RED_X)
                basic_fail_log(error_code, stderr)
                print()
                return str(stderr)
            else:
                print(mmpm.consts.GREEN_CHECK_MARK)

    os.chdir(directory)
    print(f'{mmpm.consts.GREEN_DASHES} Installation complete ' + mmpm.consts.GREEN_CHECK_MARK)
    log.info(f'Exiting installation handler from {os.getcwd()}')
    return ''


def get_pids(process_name: str) -> List[str]:
    '''
    Kills all processes of given name

    Parameters:
        process (str): the name of the process

    Returns:
        processes (List[str]): list of the processes IDs found
    '''

    log.info(f'Getting process IDs for {process_name} proceses')

    with subprocess.Popen(['pgrep', process_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as pids:
        stdout, _ = pids.communicate()
        processes = stdout.decode('utf-8')

        log.info(f'Found processes: {processes}')

        return [proc_id for proc_id in processes.split('\n') if proc_id]


def kill_pids_of_process(process: str) -> None:
    '''
    Kills all processes of given name

    Parameters:
        process (str): the name of the process

    Returns:
        processes (str): the processes IDs found
    '''
    log.info(f'Killing all processes of type {process}')
    plain_print(f'{mmpm.consts.GREEN_PLUS} stopping MagicMirror electron processes ')
    os.system(f'for process in $(pgrep {process}); do kill -9 $process; done')
    print(f'{mmpm.consts.GREEN_CHECK_MARK}')


def kill_magicmirror_processes() -> None:
    '''
    Kills all processes commonly related to MagicMirror

    Parameters:
        None

    Returns:
        None
    '''

    processes = ['electron']

    log.info(f'Killing processes associated with MagicMirror: {processes}')

    for process in processes:
        kill_pids_of_process(process)
        log.info(f'Killed pids of process {process}')


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


def get_existing_package_directories() -> List[str]:
    '''
    Retrieves list of directories found in MagicMirror modules directory

    Parameters:
        None

    Returns:
        directories (List[str]): a list of directories found in the MagicMirror modules directory
    '''
    MAGICMIRROR_MODULES_DIR: str = os.path.join(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV), 'modules')

    if not os.path.exists(MAGICMIRROR_MODULES_DIR):
        return []

    dirs: List[str] = os.listdir(MAGICMIRROR_MODULES_DIR)
    return [d for d in dirs if os.path.isdir(os.path.join(MAGICMIRROR_MODULES_DIR, d))]


def list_of_dict_to_list_of_magicmirror_packages(list_of_dict: List[dict]) -> List[MagicMirrorPackage]:
    '''
    Converts a list of dictionary contents to a list of MagicMirrorPackage objects

    Parameters:
        list_of_dict (List[dict]): a list of dictionaries representing MagicMirrorPackage data

    Returns:
        packages (List[MagicMirrorPackage]): a list of MagicMirrorPackage objects
    '''

    return [MagicMirrorPackage(**pkg) for pkg in list_of_dict]


def get_difference_of_packages(original: Dict[str, List[MagicMirrorPackage]], exclude: Dict[str, List[MagicMirrorPackage]]) -> Dict[str, List[MagicMirrorPackage]]:
    '''
    Calculates the difference between two dictionaries of MagicMirrorPackages.
    The result returned is the 'original' minus 'exclude'

    Parameters:
        original (Dict[str, List[MagicMirrorPackage]]): the full dictionary of packages
        exclude (Dict[str, List[MagicMirrorPackage]]): the dictionary of packges to be removed

    Returns:
        difference (Dict[str, List[MagicMirrorPackage]]]): the reduced set of packages
    '''

    from collections import defaultdict
    difference: Dict[str, List[MagicMirrorPackage]] = defaultdict(list)

    for category in original:
        if not exclude[category]:
            difference[category] = original[category]
            continue

        for orig_pkg in original[category]:
            if orig_pkg not in exclude[category]:
                difference[category].append(orig_pkg)

    return difference


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
        log.error(str(error))
        return requests.Response()
    return data


def get_remote_repo_api_health() -> Dict[str, dict]:
    '''
    Contacts GitHub, GitLab, and Bitbucket APIs to ensure they are up and
    running. Also, captures the number of requests that may be made to the
    GitHub API, which is more restrictive than GitLab and Bitbucket

    Parameters:
        None

    Returns:
        health (dict): a dictionary corresponding to each of the APIs,
                       containing errors and/or warnings, if applicable.
                       If no errors or warnings are present, the API is reachable
    '''
    health: dict = {
        mmpm.consts.GITHUB: {
            mmpm.consts.ERROR: '',
            mmpm.consts.WARNING: ''
        },
        mmpm.consts.GITLAB: {
            mmpm.consts.ERROR: '',
            mmpm.consts.WARNING: ''
        },
        mmpm.consts.BITBUCKET:{
            mmpm.consts.ERROR: '',
            mmpm.consts.WARNING: ''
        }
    }

    github_api_response: requests.Response = safe_get_request('https://api.github.com/rate_limit')

    if not github_api_response.status_code or github_api_response.status_code != 200:
        health[mmpm.consts.GITHUB][mmpm.consts.ERROR] = 'Unable to contact GitHub API'

    github_api: dict = json.loads(github_api_response.text)
    reset: int = github_api['rate']['reset']
    remaining: int = github_api['rate']['remaining']

    reset_time = datetime.datetime.utcfromtimestamp(reset).strftime('%Y-%m-%d %H:%M:%S')

    if not remaining:
        health[mmpm.consts.GITHUB][mmpm.consts.ERROR] = f'Unable to use `--verbose` option. No GitHub API requests remaining. Request count will reset at {reset_time}'
    elif remaining < 10:
        health[mmpm.consts.GITHUB][mmpm.consts.WARNING] = f'{remaining} GitHub API requests remaining. Request count will reset at {reset_time}'

    try:
        # GitLab doesn't have rate limits that will cause any issues with checking for repos
        gitlab_api = requests.head('https://gitlab.com', allow_redirects=True, timeout=10)

        if gitlab_api.status_code != 200:
            health[mmpm.consts.GITLAB][mmpm.consts.ERROR] = 'GitLab server returned invalid response'
    except requests.exceptions.RequestException:
        health[mmpm.consts.GITLAB][mmpm.consts.ERROR] = 'Unable to communicate with GitLab server'

    try:
        # Bitbucket rate limits are similar to GitLab
        bitbucket_api = requests.head('https://bitbucket.org', allow_redirects=True, timeout=10)

        if bitbucket_api.status_code != 200:
            health[mmpm.consts.BITBUCKET][mmpm.consts.ERROR] = 'Bitbucket server returned invalid response'
    except requests.exceptions.RequestException:
        health[mmpm.consts.GITLAB][mmpm.consts.ERROR] = 'Unable to communicate with Bitbucket server'

    return health


def __format_bitbucket_api_details__(data: dict, url: str) -> dict:
    '''
    Helper method to format remote repository data from Bitbucket

    Parameters:
        data (dict): JSON data from the API request
        url (str): the constructed url of the API used to retrieve additional info

    Returns:
        details (dict): a dictionary with star, forks, and issue counts, and creation and last updated dates
    '''
    stars = safe_get_request(f'{url}/watchers')
    forks = safe_get_request(f'{url}/forks')
    issues = safe_get_request(f'{url}/issues')

    return {
        'Stars': int(json.loads(stars.text)['pagelen']) if stars else 'N/A',
        'Issues': int(json.loads(issues.text)['pagelen']) if issues else 'N/A',
        'Created': data['created_on'].split('T')[0] if data else 'N/A',
        'Last Updated': data['updated_on'].split('T')[0] if data else 'N/A',
        'Forks': int(json.loads(forks.text)['pagelen']) if forks else 'N/A'
    } if data and stars else {}


def __format_gitlab_api_details__(data: dict, url: str) -> dict:
    '''
    Helper method to format remote repository data from GitLab

    Parameters:
        data (dict): JSON data from the API request
        url (str): the constructed url of the API used to retrieve additional info

    Returns:
        details (dict): a dictionary with star, forks, and issue counts, and creation and last updated dates
    '''
    issues = safe_get_request(f'{url}/issues')

    return {
        'Stars': data['star_count'] if data else 'N/A',
        'Issues': len(json.loads(issues.text)) if issues else 'N/A',
        'Created': data['created_at'].split('T')[0] if data else 'N/A',
        'Last Updated': data['last_activity_at'].split('T')[0] if data else 'N/A',
        'Forks': data['forks_count'] if data else 'N/A'
    } if data else {}


def __format_github_api_details__(data: dict) -> dict:
    '''
    Helper method to format remote repository data from GitHub

    Parameters:
        data (dict): JSON data from the API request

    Returns:
        details (dict): a dictionary with star, forks, and issue counts, and creation and last updated dates
    '''
    return {
        'Stars': data['stargazers_count'] if data else 'N/A',
        'Issues': data['open_issues'] if data else 'N/A',
        'Created': data['created_at'].split('T')[0] if data else 'N/A',
        'Last Updated': data['updated_at'].split('T')[0] if data else 'N/A',
        'Forks': data['forks_count'] if data else 'N/A',
    } if data else {}


def get_remote_package_details(package: MagicMirrorPackage) -> dict:
    '''
    Retrieves details about the provided MagicMirrorPackage from it's
    repository. GitHub, GitLab, and Bitbucket projects are supported

    Parameters:
        package (MagicMirrorPackage): the packge to be queried

    Returns:
        details (dict): a dictionary with star, forks, and issue counts, and creation and last updated dates
    '''
    spliced: List[str] = package.repository.split('/')
    user: str = spliced[-2]
    project: str = spliced[-1].replace('.git', '') # in case the user added .git to the end of the url

    if 'github' in package.repository:
        url = f'https://api.github.com/repos/{user}/{project}'
        log.info(f'Constructed {url} to request more details for {package.title}')
        data = safe_get_request(url)

        if not data:
            log.error(f'Unable to retrieve {package.title} details, data was empty')

        return __format_github_api_details__(json.loads(data.text)) if data else {}

    elif 'gitlab' in package.repository:
        url = f'https://gitlab.com/api/v4/projects/{user}%2F{project}'
        log.info(f'Constructed {url} to request more details for {package.title}')
        data = safe_get_request(url)

        if not data:
            log.error(f'Unable to retrieve {package.title} details, data was empty')

        return __format_gitlab_api_details__(json.loads(data.text), url) if data else {}
    elif 'bitbucket' in package.repository:
        url = f'https://api.bitbucket.org/2.0/repositories/{user}/{project}'
        log.info(f'Constructed {url} to request more details for {package.title}')
        data = safe_get_request(url)

        if not data:
            log.error(f'Unable to retrieve {package.title} details, data was empty')

        return __format_bitbucket_api_details__(json.loads(data.text), url) if data else {}

    return {}


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
        log.info('attempting to disconnect from MagicMirror websocket')
        client.disconnect()
    except (OSError, BrokenPipeError, Exception):
        log.info('encountered OSError when disconnecting from websocket, ignoring')
    return True


def get_env(key: str) -> str:
    '''
    Reads environment variables from the MMPM_ENV_FILE. In order to ensure
    hot-reloading is usable in the GUI, the environment variables need to be
    re-read from the file each time. Otherwise, cached data will be sent back
    to the user.

    Parameters:
        None

    Returns:
        value (str): the value of the environment variable key
    '''

    value: str = ''

    with open(mmpm.consts.MMPM_ENV_FILE, 'r', encoding="utf-8") as env:
        try:
            value = json.load(env)[key]
        except json.JSONDecodeError:
            log.warning(f'environment variable {key} does not exist, returning empty string')

    return value


def reset_available_upgrades_for_environment(env: str) -> bool:
    '''
    Resets a given MagicMirror installation environment within the ~/.config/mmpm/mmpm-available-upgrades.json to have no upgrades available.

    Parameters:
        env (str): the path of a MagicMirror installation

    Returns:
        success (bool): True on success, False on failure
    '''

    upgrades: dict = {}

    log.info(f'Resetting available upgrades for {env}')

    with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'r', encoding="utf-8") as available_upgrades:
        try:
            upgrades = json.load(available_upgrades)
        except (json.JSONDecodeError, OSError) as error:
            log.error(f'Encountered error when reading {mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE}: {str(error)}')
            upgrades = {mmpm.consts.MMPM: False, env: {mmpm.consts.PACKAGES: [], mmpm.consts.MAGICMIRROR: False}}

    try:
        with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w', encoding="utf-8") as available_upgrades:
            upgrades[env] = {mmpm.consts.PACKAGES: [], mmpm.consts.MAGICMIRROR: False}
            json.dump(upgrades, available_upgrades)

    except OSError as error:
        log.error(str(error))
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
    mmpm.utils.log.critical(f"{proc.stderr.decode('utf-8')}\n{proc.stdout.decode('utf-8')}")
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
            log.warning('Reached fith second of 10 second timeout for connecting to MagicMirror websocket')
            print('\nIs MagicMirror running, and are MMPM env variables set properly? If MagicMirror is a Docker image, open MagicMirror in your browser to activate the connection.')
        if not timer:
            log.warning('Reached 10 second timeout for connecting to MagicMirror websocket. Closing connection')
            print('10 second timeout reached, closing connection.')
            break

    socketio_client_disconnect(client)
