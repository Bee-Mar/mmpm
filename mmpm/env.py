#!/usr/bin/env python3
import json
import mmpm.consts
from logging import INFO
from pathlib import Path, PosixPath
from mmpm.consts import MMPM_DEFAULT_ENV
from socket import gethostbyname, gethostname
from pygments import highlight, formatters
from pygments.lexers.data import JsonLexer



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
            # got rid of the logger to avoid circular imports here
            print(
                mmpm.color.bright_yellow('WARNING:'),
                f"Environment variable '{self.name}' is not valid."
            )

        with open(mmpm.consts.MMPM_ENV_FILE, 'r', encoding="utf-8") as env:
            env_vars = {}

            try:
                env_vars = json.load(env)
            except json.JSONDecodeError:
                print(
                    mmpm.color.bright_yellow('WARNING:'),
                    f"Environment variable '{self.name}' is not valid."
                )

            if self.name not in env_vars:
                print(
                    mmpm.color.bright_yellow('WARNING:'),
                    f"Value for {self.name} not in {mmpm.consts.MMPM_ENV_FILE}. Using default value."
                )
                value = self.default
            else:
                value = env_vars.get(self.name)

        return value



# Treating this mostly like an enum
class MMPMEnv:
    MMPM_MAGICMIRROR_ROOT = EnvVar("MMPM_MAGICMIRROR_ROOT", str(Path.home() / "MagicMirror"))
    MMPM_MAGICMIRROR_URI = EnvVar("MMPM_MAGICMIRROR_URI", f'http://{gethostbyname(gethostname())}:8080')
    MMPM_MAGICMIRROR_PM2_PROCESS_NAME = EnvVar("MMPM_MAGICMIRROR_PM2_PROCESS_NAME", "")
    MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE = EnvVar("MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE", "")
    MMPM_IS_DOCKER_IMAGE = EnvVar("MMPM_IS_DOCKER_IMAGE", False)
    MMPM_LOG_LEVEL = EnvVar("MMPM_LOG_LEVEL", INFO)

    @classmethod
    def display(cls) -> None:
        with open(mmpm.consts.MMPM_ENV_FILE, 'r', encoding="utf-8") as env:
            print(highlight(json.dumps(json.load(env), indent=2), JsonLexer(), formatters.TerminalFormatter()))

        print('Run `mmpm open --env` to edit the variable values')


