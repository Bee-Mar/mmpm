#!/usr/bin/env python3
import json
import mmpm.consts
from pathlib import Path, PosixPath
from mmpm.logger import MMPMLogger
from mmpm.consts import MMPM_DEFAULT_ENV
from socket import gethostbyname, gethostname
from pygments import highlight, formatters
from pygments.lexers.data import JsonLexer

logger = MMPMLogger.get_logger(__name__)


class EnvVar:
    def __init__(self, name: str = "", default = None):
        self.name = name
        self.default = default

    def get(self):
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

        if self.name not in MMPM_DEFAULT_ENV:
            logger.fatal(f"Environment variable '{self.name}' does is not valid.")


        with open(mmpm.consts.MMPM_ENV_FILE, 'r', encoding="utf-8") as env:
            env_vars = {}

            try:
                env_vars = json.load(env)
            except json.JSONDecodeError:
                logger.warning(f"Environment variable '{self.name}' does is not valid.")

            if self.name not in env_vars:
                logger.fatal(f"Value for {self.name} not in {mmpm.consts.MMPM_ENV_FILE}. Using default value.")
                value = self.default
            else:
                value = env_vars.get(self.name)

        return value


# Treating this basically like an enum
class MMPMEnv:
    mmpm_magicmirror_root = EnvVar("MMPM_MAGICMIRROR_ROOT", str(Path.home() / "MagicMirror"))
    mmpm_magicmirror_uri = EnvVar("MMPM_MAGICMIRROR_URI", f'http://{gethostbyname(gethostname())}:8080')
    mmpm_magicmirror_pm2_process_name = EnvVar("MMPM_MAGICMIRROR_PM2_PROCESS_NAME", "")
    mmpm_magicmirror_docker_compose_file = EnvVar("MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE", "")
    mmpm_is_docker_image = EnvVar("MMPM_IS_DOCKER_IMAGE", False)
    mmpm_log_level = EnvVar("MMPM_LOG_LEVEL", "INFO")

    @classmethod
    def display(cls) -> None:

        with open(mmpm.consts.MMPM_ENV_FILE, 'r', encoding="utf-8") as env:
            print(highlight(json.dumps(json.load(env), indent=2), JsonLexer(), formatters.TerminalFormatter()))

        print('Run `mmpm open --env` to edit the variable values')



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

    if key not in MMPM_DEFAULT_ENV:
        logger.fatal(f"Environment variable '{key}' does is not valid.")


    with open(mmpm.consts.MMPM_ENV_FILE, 'r', encoding="utf-8") as env:
        env_vars = {}

        try:
            env_vars = json.load(env)
        except json.JSONDecodeError:
            logger.warning(f"Environment variable '{key}' does is not valid.")

        if key not in env_vars:
            logger.fatal(f"Value for {key} not in {mmpm.consts.MMPM_ENV_FILE}. Using default value.")
            value = MMPM_DEFAULT_ENV[key]
        else:
            value = env_vars.get(key)

    return value
