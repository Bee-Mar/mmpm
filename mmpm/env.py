#!/usr/bin/env python3
import json
import sys
from logging import INFO
from os.path import getmtime
from pathlib import Path
from socket import gethostbyname, gethostname

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import JsonLexer

from mmpm.constants import color, paths
from mmpm.singleton import Singleton

MMPM_DEFAULT_ENV: dict = {
    "MMPM_MAGICMIRROR_ROOT": Path(paths.HOME_DIR / "MagicMirror"),
    "MMPM_MAGICMIRROR_URI": "http://localhost:8080",
    "MMPM_MAGICMIRROR_PM2_PROCESS_NAME": "",
    "MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE": "",
    "MMPM_IS_DOCKER_IMAGE": False,
    "MMPM_LOG_LEVEL": "WARN",
}


class EnvVar:
    __slots__ = "name", "default", "__tipe", "__value", "__mtime"

    def __init__(self, name: str = "", default=None, mtime: float = None):
        self.name: str = name
        self.default = default
        self.__tipe = type(default)  # avoid name clashing with 'type'
        self.__mtime: float = mtime
        self.__value = None

    def get(self):
        """
        Reads environment variables from the MMPM_ENV_FILE. In order to ensure
        hot-reloading is usable in the GUI, the environment variables need to be
        re-read from the file each time. Otherwise, cached data will be sent back
        to the user.

        Parameters:
            None

        Returns:
            value:  the value of the environment variable key
        """

        mtime: float = getmtime(paths.MMPM_ENV_FILE)

        if mtime != self.__mtime or self.__value is None:  # cache the value until the file modification time changes
            with open(paths.MMPM_ENV_FILE, "r", encoding="utf-8") as env:
                env_vars = {}

                try:
                    env_vars = json.load(env)
                except json.JSONDecodeError:
                    print(color.b_yellow("WARNING:"), f"Unable to parse environment variables file.")

                self.__value = self.__tipe(self.default if self.name not in env_vars else env_vars.get(self.name))

            self.__mtime = mtime

        return self.__value


# Treating this kind of like an enum
class MMPMEnv(Singleton):
    __slots__ = tuple({key.lower() for key in MMPM_DEFAULT_ENV.keys()})

    def __init__(self):
        super().__init__()
        self.MMPM_MAGICMIRROR_ROOT: EnvVar = None
        self.MMPM_MAGICMIRROR_URI: EnvVar = None
        self.MMPM_MAGICMIRROR_PM2_PROCESS_NAME: EnvVar = None
        self.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: EnvVar = None
        self.MMPM_IS_DOCKER_IMAGE: EnvVar = None
        self.MMPM_LOG_LEVEL: EnvVar = None

        env_vars = {}

        with open(paths.MMPM_ENV_FILE, "r", encoding="utf-8") as env_file:
            try:
                env_vars = json.load(env_file)
            except json.JSONDecodeError:
                pass

            for key in MMPM_DEFAULT_ENV:
                if key not in env_vars:
                    env_vars[key] = MMPM_DEFAULT_ENV[key]

        env_vars["MMPM_MAGICMIRROR_ROOT"] = str(env_vars["MMPM_MAGICMIRROR_ROOT"])

        with open(paths.MMPM_ENV_FILE, "w", encoding="utf-8") as env:
            json.dump(env_vars, env, indent=2)

        mtime: float = getmtime(paths.MMPM_ENV_FILE)

        for key, value in MMPM_DEFAULT_ENV.items():
            if hasattr(self, key):
                setattr(self, key, EnvVar(name=key, default=value, mtime=mtime))

    def get(self) -> dict:
        current_env = {}

        with open(paths.MMPM_ENV_FILE, "r", encoding="utf-8") as env:
            current_env = json.load(env)

        return current_env

    def display(self) -> None:  # pragma: no cover
        print(highlight(json.dumps(self.get(), indent=2), JsonLexer(), TerminalFormatter()))
