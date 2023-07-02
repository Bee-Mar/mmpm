#!/usr/bin/env python3
import json
from logging import INFO
from pathlib import Path, PosixPath
from socket import gethostbyname, gethostname
from pygments import highlight, formatters
from pygments.lexers.data import JsonLexer
from mmpm.singleton import Singleton
from mmpm.constants import paths, color

MMPM_DEFAULT_ENV: dict = {
    "MMPM_MAGICMIRROR_ROOT": str(paths.HOME_DIR / "MagicMirror"),
    "MMPM_MAGICMIRROR_URI": 'http://localhost:8080',
    "MMPM_MAGICMIRROR_PM2_PROCESS_NAME": '',
    "MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE": '',
    "MMPM_IS_DOCKER_IMAGE": False,
    "MMPM_LOG_LEVEL": "INFO"
}

class EnvVar:
    def __init__(self, name: str = "", default=None):
        self.name = name
        self.default = default


    def get(self):
        """
        Reads environment variables from the MMPM_ENV_FILE. In order to ensure
        hot-reloading is usable in the GUI, the environment variables need to be
        re-read from the file each time. Otherwise, cached data will be sent back
        to the user.

        Parameters:
            None

        Returns:
            value (str): the value of the environment variable key
        """

        value: str = ""

        if self.name not in MMPM_DEFAULT_ENV:
            # got rid of the logger to avoid circular imports here
            print(color.b_yellow("WARNING:"), f"Environment variable '{self.name}' is not valid.")

        with open(paths.MMPM_ENV_FILE, "r", encoding="utf-8") as env:
            env_vars = {}

            try:
                env_vars = json.load(env)
            except json.JSONDecodeError:
                pass

            value = self.default if self.name not in env_vars else env_vars.get(self.name)

        return value


# Treating this kind of like an enum
class MMPMEnv(Singleton):
    def init(self):
        env_vars = {}

        with open(paths.MMPM_ENV_FILE, "r", encoding="utf-8") as env:
            try:
                env_vars = json.load(env)
            except json.JSONDecodeError:
                pass

            for key, value in MMPM_DEFAULT_ENV.items():
                if key not in env_vars:
                    env_vars[key] = MMPM_DEFAULT_ENV[key]

        with open(paths.MMPM_ENV_FILE, "w", encoding="utf-8") as env:
            json.dump(env_vars, env, indent=2)

        self.mmpm_magicmirror_root = EnvVar("MMPM_MAGICMIRROR_ROOT", str(Path.home() / "MagicMirror"))
        self.mmpm_magicmirror_uri = EnvVar("MMPM_MAGICMIRROR_URI", f"http://{gethostbyname(gethostname())}:8080")
        self.mmpm_magicmirror_pm2_process_name = EnvVar("MMPM_MAGICMIRROR_PM2_PROCESS_NAME", "")
        self.mmpm_magicmirror_docker_compose_file = EnvVar("MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE", "")
        self.mmpm_is_docker_image = EnvVar("MMPM_IS_DOCKER_IMAGE", False)
        self.mmpm_log_level = EnvVar("MMPM_LOG_LEVEL", INFO)


    def display(cls) -> None:
        with open(paths.MMPM_ENV_FILE, "r", encoding="utf-8") as env:
            print(highlight(json.dumps(json.load(env), indent=2), JsonLexer(), formatters.TerminalFormatter()))

        print("Run `mmpm open --env` to edit the variable values")
