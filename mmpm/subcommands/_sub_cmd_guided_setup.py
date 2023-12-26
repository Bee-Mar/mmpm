#!/usr/bin/env python3
""" Command line options for 'guided-setup' subcommand """
import json
from os import getenv
from pathlib import Path

from mmpm.constants import color, paths
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.utils import confirm, get_host_ip, prompt

logger = MMPMLogFactory.get_logger(__name__)


class GuidedSetup(SubCmd):
    """
    The 'GuidedSetup' subcommand interactively walks users through the setup
    process of MMPM's features, and generates the next steps they should
    manually perform (if necessary)

    Custom Attributes:
        env (MMPMEnv): A singleton of MMPMEnv which contains environment variables
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "guided-setup"
        self.help = f"Interactively setup {self.app_name} and its features"
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
        mmpm_is_docker_image: bool = False
        install_ui: bool = False
        install_autocomplete: bool = False
        install_as_module: bool = False

        magicmirror_root = prompt("Enter the absolute path to your MagicMirror installation: ", default=f"{Path.home()}/MagicMirror")
        mmpm_is_docker_image = confirm("Is MMPM running as a Docker image?")

        if not mmpm_is_docker_image and confirm("Did you install MagicMirror using docker-compose?"):
            magicmirror_docker_compose_file = prompt(
                f"What is the absolute path to the MagicMirror docker-compose file (ie. {Path.home()}/docker-compose.yml)?"
            )

        if not mmpm_is_docker_image and not magicmirror_docker_compose_file and confirm("Are you using PM2 to start/stop MagicMirror?"):
            magicmirror_pm2_proc = prompt("What is the name of the PM2 process for MagicMirror?")

        magicmirror_uri = prompt("Enter the address and port used to access MagicMirror: ", default=f"http://{get_host_ip()}:8080")

        install_ui = not mmpm_is_docker_image and confirm("Would you like to install the MMPM UI (user interface)?")
        install_as_module = confirm("Would you like to hide/show MagicMirror modules through MMPM?")
        install_autocomplete = confirm("Would you like to install tab-autocomplete for the MMPM CLI?")

        with open(paths.MMPM_ENV_FILE, "w", encoding="utf-8") as env:
            json.dump(
                {
                    self.env.MMPM_MAGICMIRROR_ROOT.name: str(magicmirror_root),
                    self.env.MMPM_MAGICMIRROR_URI.name: magicmirror_uri,
                    self.env.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.name: magicmirror_pm2_proc,
                    self.env.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.name: str(magicmirror_docker_compose_file),
                    self.env.MMPM_IS_DOCKER_IMAGE.name: bool(mmpm_is_docker_image),
                },
                env,
                indent=2,
            )

        message = "Based on your responses, your environment variables have been set as:"
        line_break = color.b_green("-" * len(message))

        print("\n" + line_break)
        print("\nBased on your responses, your environment variables have been set as:")
        self.env.display()

        if install_as_module or install_ui or install_autocomplete:
            print("Execute the following commands to install the desired features:")

        if install_as_module:
            print(color.b_green("mmpm install -y MMM-mmpm"))
        if install_ui:
            print(color.b_green("mmpm ui install -y"))
        if install_autocomplete:
            print(color.b_green(f"mmpm completion --shell={Path(getenv('SHELL')).stem}"))
