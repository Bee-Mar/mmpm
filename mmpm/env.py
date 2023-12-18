#!/usr/bin/env python3
import json
from os.path import getmtime
from pathlib import Path

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
    "MMPM_LOG_LEVEL": "INFO",
}


class EnvVar:
    """
    Represents a re-readable environment variable stored in the MMPM_ENV_FILE.
    When a change in the last-modified time of the MMPM_ENV_FILE, the value is
    re-read. The __slots__ are predefined to improve efficiency.

    Attributes:
        name (str): the name of the environment variable
        default (Any): the default value
        __tipe (object): the class the environment should be initialized as
        __mtime (object): the last modified time of the MMPM_ENV_FILE
        __value (object): the value read from the MMPM_ENV_FILE

    Methods:
        get(): Returns the value of the environment variable
    """

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
        hot-reloading is usable in the UI, the environment variables need to be
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
                    print(
                        color.b_yellow("WARNING:"),
                        "Unable to parse environment variables file.",
                    )

                # make sure we construct the expected type using from parsed data, otherwise instead of
                # something like a Path object we would return a string
                self.__value = self.__tipe(self.default if self.name not in env_vars else env_vars.get(self.name))

            self.__mtime = mtime

        return self.__value


class MMPMEnv(Singleton):
    """
    MMPMEnv, a singleton class, serves as the centralized source for managing and accessing environment variables
    within the MMPM application. It reads and writes environment variables to the MMPM_ENV_FILE, ensuring that all
    components of the application have consistent and up-to-date configurations. The class is designed to dynamically
    reflect changes made to the environment variables in the MMPM_ENV_FILE.

    Attributes:
        MMPM_MAGICMIRROR_ROOT (EnvVar): Environment variable for the root directory of MagicMirror.
        MMPM_MAGICMIRROR_URI (EnvVar): Environment variable for the URI of the MagicMirror.
        MMPM_MAGICMIRROR_PM2_PROCESS_NAME (EnvVar): Environment variable for the PM2 process name of MagicMirror.
        MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE (EnvVar): Environment variable for the Docker compose file path.
        MMPM_IS_DOCKER_IMAGE (EnvVar): Environment variable indicating if MMPM is running as a Docker image.
        MMPM_LOG_LEVEL (EnvVar): Environment variable for the logging level.

    Methods:
        __init__(): Initializes the MMPMEnv instance, loading environment variables from MMPM_ENV_FILE.
        get(): Retrieves the current environment variables as a dictionary.
        display(): Prints the current environment variables in a formatted JSON structure for easy viewing.
    """

    __slots__ = tuple({key.lower() for key in MMPM_DEFAULT_ENV})

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

            for key, value in MMPM_DEFAULT_ENV.items():
                if key not in env_vars:
                    env_vars[key] = value

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
