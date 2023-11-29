#!/usr/bin/env python3
""" Command line options for 'guided-setup' subcommand """
from os.path import normpath
from pathlib import Path

from mmpm.constants import color, paths
from mmpm.env import MMPMEnv
from mmpm.logger import MMPMLogger
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.utils import get_host_ip, prompt, validate_input

logger = MMPMLogger.get_logger(__name__)


class GuidedSetup(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "guided-setup"
        self.help = "Interactive setup of MMPM and features"
        self.usage = f"{self.app_name} {self.name}"
        self.env = MMPMEnv()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

    def exec(self, args, extra):
        """
        Provides the user a guided configuration of the environment variables, and
        feature installation. This can be re-run as many times as necessary.

        Parameters:
            None

        Returns:
            None
        """
        print(color.b_green("Welcome to MMPM's guided setup!\n"))
        print("I'll help you setup your environment variables and additional features. Let's get started!\n")

        magicmirror_root: str = f"{Path.home()}/MagicMirror"
        magicmirror_uri: str = f"http://{get_host_ip()}:8080"
        magicmirror_pm2_proc: str = ""
        magicmirror_docker_compose_file: str = ""
        MMPM_IS_DOCKER_IMAGE: bool = False
        install_gui: bool = False
        install_autocomplete: bool = False
        install_as_module: bool = False

        magicmirror_root = validate_input(f"What is the absolute path to your MagicMirror installation (ie. {Path.home()}/MagicMirror)?")
        MMPM_IS_DOCKER_IMAGE = prompt("Is MMPM running as a Docker image?")

        if not MMPM_IS_DOCKER_IMAGE and prompt("Did you install MagicMirror using docker-compose?"):
            magicmirror_docker_compose_file = validate_input(
                f"What is the absolute path to the MagicMirror docker-compose file (ie. {Path.home()}/docker-compose.yml)?"
            )

        if not MMPM_IS_DOCKER_IMAGE and not magicmirror_docker_compose_file and prompt("Are you using PM2 to start/stop MagicMirror?"):
            magicmirror_pm2_proc = validate_input("What is the name of the PM2 process for MagicMirror?")

        if not prompt(f"Is {magicmirror_uri} the address used to open MagicMirror in your browser?"):
            magicmirror_uri = validate_input("Enter the address and port used to access MagicMirror:")

        install_gui = not MMPM_IS_DOCKER_IMAGE and prompt("Would you like to install the MMPM GUI (web interface)?")
        install_as_module = prompt("Would you like to hide/show MagicMirror modules through MMPM?")
        install_autocomplete = prompt("Would you like to install tab-autocomplete for the MMPM CLI?")

        with open(paths.MMPM_ENV_FILE, "w", encoding="utf-8") as env:
            json.dump(
                {
                    self.env.MMPM_MAGICMIRROR_ROOT.name: normpath(magicmirror_root),
                    self.env.MMPM_MAGICMIRROR_URI.name: magicmirror_uri,
                    self.env.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.name: magicmirror_pm2_proc,
                    self.env.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.name: normpath(magicmirror_docker_compose_file),
                    self.env.MMPM_IS_DOCKER_IMAGE.name: MMPM_IS_DOCKER_IMAGE,
                },
                env,
                indent=2,
            )

        message = "Based on your responses, your environment variables have been set as:"
        line_break = color.b_green("-" * len(message))

        print("\n" + line_break)
        print("\nBased on your responses, your environment variables have been set as:")
        self.env.display()

        print("Execute the following commands to install the desired features:")

        if install_as_module:
            print(color.b_green("mmpm install MMM-mmpm"))
        if install_gui:
            print(color.b_green("mmpm install --gui"))
        if install_autocomplete:
            print(color.b_green("mmpm completion"))
