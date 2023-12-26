#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import List, Tuple

import git
import requests
from packaging import version
from prompt_toolkit import prompt as ptk_prompt
from prompt_toolkit.shortcuts import confirm as ptk_confirm
from yaspin import yaspin
from yaspin.spinners import Spinners

from mmpm.__version__ import version as current_version
from mmpm.constants import color
from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)


def repo_up_to_date(path: Path):
    """
    Checks if the Git repository at the given path is up-to-date with its remote origin.

    Parameters:
        path (Path): The file system path to the Git repository.

    Returns:
        bool: True if the local repository is up-to-date, False otherwise.
    """

    try:
        repo = git.Repo(path)

        # Ensure the repository is not bare (unlikely, but still should check)
        if repo.bare:
            logger.error(f"Repository in {path} is bare. Cannot determine if out-of-date.")
            return False

        logger.debug(f"Fetching information for repo found in '{path}'")
        remote = repo.remotes.origin
        remote.fetch()

        # Get local and remote HEAD commit
        local_commit = repo.head.commit
        remote_commit = repo.refs["origin/HEAD"].commit  # type: ignore

        logger.debug(f"SHAs found in '{path}' -- local={local_commit.hexsha} & remote={remote_commit.hexsha}")

        remote = repo.remotes.origin
        return local_commit.hexsha != remote_commit.hexsha
    except Exception as error:
        logger.error(f"Failed to get status of repo located at {path}: {error}")
        return False


def get_host_ip() -> str:
    """
    Retrieves the local IP address of the host machine.

    Returns:
        str: The local IP address.
    """

    logger.debug("Getting host IP")

    address = "localhost"
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        skt.connect(("8.8.8.8", 80))
        address = skt.getsockname()[0]
        logger.debug(f"Determined Host IP={address}")
    except socket.gaierror as error:
        logger.error(f"Failed to determine host IP address: {error}")
        address = "localhost"  # just to be extra safe and make sure it's set to something usable
    finally:
        skt.close()

    return address


def run_cmd(command: List[str], progress=True, background=False, message: str = "") -> Tuple[int, str, str]:
    """
    Executes a shell command and captures its output and errors.

    Parameters:
        command (List[str]): The command and its arguments to be executed.
        progress (bool): If True, displays a spinner during command execution.
        background (bool): If True, runs the command in the background.
        message (str): The message to display alongside the spinner.

    Returns:
        Tuple[int, str, str]: A tuple containing the command's return code, standard output, and standard error.
    """
    if background:
        logger.debug(f"Executing command `{' '.join(command)}` in background")

        # fully detach the terminal from the process so nothing hangs
        with open(os.devnull, "wb") as devnull:
            # pylint: disable=subprocess-popen-preexec-fn
            subprocess.Popen(command, stdout=devnull, stderr=devnull, stdin=devnull, close_fds=True, preexec_fn=os.setsid)

        return 0, "", ""

    logger.debug(f'Executing command `{" ".join(command)}`')

    with subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        if progress:
            with yaspin(text=message, color="green") as spinner:
                spinner.spinner = Spinners.bouncingBar

                while process.poll() is None:
                    time.sleep(0.1)

        stdout, stderr = process.communicate()

        return process.returncode, stdout.decode("utf-8"), stderr.decode("utf-8")


def get_pids(process_name: str) -> List[str]:
    """
    Retrieves process IDs for all processes with the given name.

    Parameters:
        process_name (str): The name of the process to search for.

    Returns:
        List[str]: A list of process IDs.
    """

    logger.info(f"Getting process IDs related to '{process_name}'")

    with subprocess.Popen(["pgrep", process_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as pids:
        stdout, _ = pids.communicate()
        processes = stdout.decode("utf-8")

        logger.debug(f"Found process IDs: {processes}")

        return [proc_id for proc_id in processes.split("\n") if proc_id]


def kill_pids_of_process(process: str) -> None:
    """
    Terminates all processes with the given name.

    Parameters:
        process (str): The name of the process to be terminated.
    """
    os.system(f"for process in $(pgrep {process}); do kill -9 $process; done")
    logger.debug(f"Stopped all processes of type {process}")


def safe_get_request(url: str) -> requests.Response:
    """
    Safely performs a GET request to the specified URL, handling any exceptions.

    Parameters:
        url (str): The URL to send the GET request to.

    Returns:
        requests.Response: The response from the GET request.
    """
    try:
        logger.debug(f"Creating request for {url}")
        data = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as error:
        logger.error(str(error))
        return requests.Response()
    return data


def upgrade() -> bool:
    """
    Attempts to upgrade the MMPM package using pip.

    Returns:
        bool: True if the upgrade is successful, False otherwise.
    """

    error_code, stdout, stderr = run_cmd(
        ["python3", "-m", "pip", "install", "--upgrade", "mmpm"],
        message="Upgrading MMPM",
    )

    if error_code:
        logger.error(stderr)
        return False

    logger.debug(stdout)
    return True


def update_available() -> bool:
    """
    Checks if an update is available for MMPM on PyPi.

    Returns:
        bool: True if an update is available, False otherwise.
    """

    url = "https://pypi.org/pypi/mmpm/json"

    logger.debug("Getting remote version of MMPM from PyPi")
    print(f"Retrieving: {url} [{color.n_cyan('mmpm')}]")

    try:
        contents = urllib.request.urlopen(url).read()
        remote_version = json.loads(contents)["info"]["version"]
        logger.debug(f"Found remote={remote_version} & installed={current_version}")
    except (json.JSONDecodeError, urllib.error.URLError, Exception) as error:
        logger.error(f"Failed to get remote version of MMPM: {error}")

    return version.parse(remote_version) > version.parse(current_version)


# wrapping prompt_toolkit so it's easier to switch out in the future if desired
def confirm(message: str) -> bool:  # pragma: no cover
    """
    Displays a confirmation prompt to the user with the given message.

    Parameters:
        message (str): The message to display in the confirmation prompt.

    Returns:
        bool: True if the user confirms, False otherwise.
    """

    return ptk_confirm(message)


# wrapping prompt_toolkit so it's easier to switch out in the future if desired
def prompt(message: str, default=""):  # pragma: no cover
    """
    Displays a prompt to the user with the given message and waits for input.

    Parameters:
        message (str): The message to display in the prompt.

    Returns:
        str: The user's input as a string.
    """
    return ptk_prompt(message, default=default)
