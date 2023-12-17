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
from yaspin import yaspin
from yaspin.spinners import Spinners

from mmpm.__version__ import version as current_version
from mmpm.constants import color
from mmpm.log.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)


def repo_up_to_date(path: Path):
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
    logger.debug("Getting host IP")

    address: str = "localhost"
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        skt.connect(("8.8.8.8", 80))
        address = skt.getsockname()[0]
        logger.debug(f"Determined Host IP={address}")
    except socket.gaierror as error:
        logger.error(f"Failed to determine host IP address: {error}")
    finally:
        skt.close()

    return address


def run_cmd(command: List[str], progress=True, background=False, message: str = "") -> Tuple[int, str, str]:
    """
    Executes shell command and captures errors

    Parameters:
        command (List[str]): The command string to be executed

    Returns:
        Tuple[returncode (int), stdout (str), stderr (str)]
    """
    if background:
        logger.debug(f"Executing command `{' '.join(command)}` in background")
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
    Kills all processes of given name

    Parameters:
        process (str): the name of the process

    Returns:
        processes (List[str]): list of the processes IDs found
    """

    logger.info(f"Getting process IDs related to '{process_name}'")

    with subprocess.Popen(["pgrep", process_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as pids:
        stdout, _ = pids.communicate()
        processes = stdout.decode("utf-8")

        logger.debug(f"Found process IDs: {processes}")

        return [proc_id for proc_id in processes.split("\n") if proc_id]


def kill_pids_of_process(process: str) -> None:
    """
    Kills all processes of given name

    Parameters:
        process (str): the name of the process

    Returns:
        processes (str): the processes IDs found
    """
    os.system(f"for process in $(pgrep {process}); do kill -9 $process; done")
    logger.debug(f"Stopped all processes of type {process}")


def safe_get_request(url: str) -> requests.Response:
    """
    Wrapper method around the 'requests.get' call, containing a try, except block

    Parameters:
        url (str): the url used for the API request

    Returns:
        response (requests.Response): the Reponse object, which may be empty if the request failed
    """
    try:
        logger.debug(f"Creating request for {url}")
        data = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as error:
        logger.error(str(error))
        return requests.Response()
    return data


def upgrade() -> bool:
    error_code, stdout, stderr = run_cmd(
        ["python3", "-m", "pip", "install", "--upgrade", "--no-cache-dir", "mmpm"],
        message="Upgrading MMPM",
    )

    if error_code:
        logger.error(stderr)
        return False

    logger.debug(stdout)
    return True


def update_available() -> bool:
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
