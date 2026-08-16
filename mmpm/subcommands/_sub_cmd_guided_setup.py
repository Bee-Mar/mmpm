"""Command line options for 'guided-setup' subcommand"""

import json
from os import getenv
from pathlib import Path
from shutil import which

from mmpm.constants import color, paths
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.ui import MMPMui
from mmpm.utils import confirm, get_host_ip, prompt

logger = MMPMLogFactory.get_logger(__name__)


class GuidedSetup(SubCmd):
    """
    The 'GuidedSetup' subcommand interactively walks users through the setup
    process of MMPM's features, and offers to install the selected features
    when finished. It can be re-run at any time; prompts are prefilled with
    the current environment values.

    Custom Attributes:
        env (MMPMEnv): A singleton of MMPMEnv which contains environment variables
    """

    env: MMPMEnv = MMPMEnv()

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "guided-setup"
        self.help = f"Interactively setup {self.app_name} and its features"
        self.usage = f"{self.app_name} {self.name}"

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

    def __prompt_for_path__(self, message: str, default: str = "", must_exist_hint: str = "") -> str:
        """
        Prompts for a filesystem path, warning (with the option to re-enter)
        when the provided path does not exist.

        Parameters:
            message (str): the prompt message
            default (str): value prefilled in the prompt
            must_exist_hint (str): short description of what should exist at the path

        Returns:
            str: the path provided by the user (possibly nonexistent, if they insisted)
        """

        while True:
            response: str = prompt(message, default=default).strip()

            if not response or Path(response).expanduser().exists():
                return response

            logger.warning(f"'{response}' does not exist{f' ({must_exist_hint})' if must_exist_hint else ''}")

            if confirm("Keep this value anyway?"):
                return response

    def exec(self, args, extra):
        """
        Provides the user a guided configuration of the environment variables, and
        feature installation. This can be re-run as many times as necessary; the
        prompts are prefilled with the current environment values.

        Parameters:
            None

        Returns:
            None
        """
        print(color.b_green("Welcome to MMPM's guided setup!\n"))
        print("I'll help you setup your environment variables and additional features. Let's get started!\n")

        current_root = str(self.env.MMPM_MAGICMIRROR_ROOT.get() or Path.home() / "MagicMirror")
        current_uri = self.env.MMPM_MAGICMIRROR_URI.get() or f"http://{get_host_ip()}:8080"
        current_pm2_proc = self.env.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.get() or ""
        current_compose_file = str(self.env.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.get() or "")

        magicmirror_pm2_proc: str = ""
        magicmirror_docker_compose_file: str = ""

        magicmirror_root = self.__prompt_for_path__(
            "Enter the absolute path to your MagicMirror installation: ",
            default=current_root,
            must_exist_hint="it will be created when MagicMirror is installed",
        )

        mmpm_is_docker_image = confirm("Is MMPM running as a Docker image?")

        if not mmpm_is_docker_image and confirm("Did you install MagicMirror using docker-compose?"):
            magicmirror_docker_compose_file = self.__prompt_for_path__(
                f"What is the absolute path to the MagicMirror docker-compose file (ie. {Path.home()}/docker-compose.yml)? ",
                default=current_compose_file,
            )

        if not mmpm_is_docker_image and not magicmirror_docker_compose_file and confirm("Are you using PM2 to start/stop MagicMirror?"):
            magicmirror_pm2_proc = prompt("What is the name of the PM2 process for MagicMirror? ", default=current_pm2_proc)

        while True:
            magicmirror_uri = prompt("Enter the address and port used to access MagicMirror: ", default=current_uri).strip()

            if magicmirror_uri.startswith(("http://", "https://")):
                break

            logger.warning(f"'{magicmirror_uri}' does not begin with http:// or https://")

            if confirm("Keep this value anyway?"):
                break

        install_ui = not mmpm_is_docker_image and confirm("Would you like to install the MMPM UI (user interface)?")

        install_as_module = confirm(
            f"Would you like to install the MMM-mmpm module so MMPM can control module visibility (used by `{self.app_name} mm hide/show`)?"
        )

        install_autocomplete = confirm("Would you like to setup tab-autocomplete for the MMPM CLI?")

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

        print(f"\n{line_break}\n{message}")
        self.env.display()
        print(line_break)

        if install_as_module:
            self.__install_mmpm_module__()

        if install_ui:
            self.__install_ui__()

        if install_autocomplete:
            self.__show_autocomplete_setup__()

        print(color.b_green("\nSetup complete!"), f"Run `{self.app_name} list --installed` at any time to see your installed packages.")

    def __install_mmpm_module__(self) -> None:
        database = MagicMirrorDatabase()

        if not database.is_initialized():
            database.load()

        package = next((pkg for pkg in database.packages if pkg.title == "MMM-mmpm"), None)

        if package is None:
            logger.error(f"Unable to locate MMM-mmpm in the database. Run `{self.app_name} add MMM-mmpm` to try again.")
        elif package.is_installed:
            logger.info("MMM-mmpm is already installed")
        elif package.install():
            logger.info(f"Installed {color.n_green(package.title)} ({package.repository})")
        else:
            logger.error(f"Failed to install MMM-mmpm. Run `{self.app_name} add MMM-mmpm` to try again.")

    def __install_ui__(self) -> None:
        if not which("pm2"):
            logger.error(f"pm2 is not in your PATH. Please run `npm install -g pm2`, then run `{self.app_name} ui install`.")
            return

        ui = MMPMui()

        if ui.install():
            logger.info("Installed MMPM-UI")
            print(f"Run `{self.app_name} ui url` to display the UI address, or execute `{self.app_name} open --ui` to open it.")
        else:
            logger.error(f"Failed to install the MMPM UI. Run `{self.app_name} ui install` to try again.")
            ui.delete()

    def __show_autocomplete_setup__(self) -> None:
        shell = getenv("SHELL")

        if shell:
            print("To enable tab-autocomplete, run the following, and add it to your shell's startup file:")
            print(color.b_green(f"{self.app_name} completion --shell={Path(shell).stem}"))
        else:
            print(f"Unable to detect your shell. Run `{self.app_name} completion --shell=<shell>` to setup tab-autocomplete.")
