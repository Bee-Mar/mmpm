"""Command line options for 'open' subcommand"""

import subprocess
import sys
from os import getenv
from pathlib import Path
from shlex import split
from shutil import copyfile, which

from mmpm.constants import paths, urls
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.magicmirror import MagicMirrorConfigs
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.utils import run_cmd

logger = MMPMLogFactory.get_logger(__name__)


class Open(SubCmd):
    """
    The 'Open' subcommand allows users to open various configuration files, documentation,
    wikis, and the MagicMirror application itself.

    Custom Attributes:
        env (MMPMEnv): An instance of the MMPMEnv class for managing environment variables.
        mm_configs (MagicMirrorConfigs): Locations of the MagicMirror configuration files.
        [Method] edit(self, file: PosixPath): see method docs
    """

    env: MMPMEnv = MMPMEnv()

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "open"
        self.help = "Open config files, documentation, wikis, and MagicMirror itself"
        self.usage = f"{self.app_name} {self.name} <config/css/env/ui/magicmirror/mm-wiki/mm-docs/mmpm-wiki>"
        self.mm_configs = MagicMirrorConfigs()

    def edit(self, file: Path) -> None:
        """
        Checks if the requested file exists, and if not, the file is created.
        Then, opens the file for editing using the system's default editor.

        Parameters:
            file (PosixPath): The file path to open for editing.

        Returns:
            None
        """

        if not file.exists():
            try:
                logger.warning(f"{file} does not exist. Creating file.")
                file.parent.mkdir(parents=True, exist_ok=True)
                file.touch(mode=0o664, exist_ok=True)
            except OSError as error:
                logger.fatal(f"Unable to create {file}: {str(error)}")
                sys.exit(1)

        editor = getenv("EDITOR") or getenv("VISUAL") or "nano"
        logger.info(f"Opening {file} for user to edit")
        subprocess.run([*split(editor), str(file)], check=False)

    def open_in_browser(self, url: str) -> None:
        """
        Opens the provided URL in the user's default browser via xdg-open.

        Parameters:
            url (str): The URL to open.

        Returns:
            None
        """

        if not which("xdg-open"):
            logger.error("The executable 'xdg-open' could not be found. Unable to open a browser.")
            sys.exit(1)

        run_cmd(["xdg-open", url], background=True)

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        subparsers = self.parser.add_subparsers(
            dest="command",
            description=f"use `{self.app_name} {self.name} <subcommand> --help` to see more details",
            title=f"{self.app_name} {self.name} subcommands",
            metavar="",
        )

        subparsers.add_parser("config", help="open MagicMirror config/config.js file in your $EDITOR")
        subparsers.add_parser("css", help="open MagicMirror css/custom.css file in your $EDITOR")
        subparsers.add_parser("env", help="open the MMPM run-time environment variables JSON configuration file in your $EDITOR")
        subparsers.add_parser("ui", help="open the MMPM UI in your default browser")
        subparsers.add_parser("magicmirror", help="open MagicMirror in your default browser (uses the MMPM_MAGICMIRROR_URI address)")
        subparsers.add_parser("mm-wiki", help="open the MagicMirror GitHub wiki in your default browser")
        subparsers.add_parser("mm-docs", help="open the MagicMirror documentation in your default browser")
        subparsers.add_parser("mmpm-wiki", help="open the MMPM GitHub wiki in your default browser")

    def exec(self, args, extra):
        if extra:
            logger.error(f"Extra arguments are not accepted. See '{self.app_name} {self.name} --help'")
        elif args.command == "config":
            config_js = self.mm_configs.config_js
            config_js_sample = self.mm_configs.config_js_sample

            if not config_js.exists() and not config_js_sample.exists():
                logger.error(f"Unable to find {config_js.name} or {config_js_sample.name}. Unable to access MagicMirror config.")
                sys.exit(1)

            # seed config.js from the sample only when it's missing or empty
            if (not config_js.exists() or not config_js.stat().st_size) and config_js_sample.exists():
                copyfile(config_js_sample, config_js)

            self.edit(config_js)

        elif args.command == "css":
            self.edit(self.mm_configs.custom_css)
        elif args.command == "env":
            self.edit(paths.MMPM_ENV_FILE)
        elif args.command == "magicmirror":
            self.open_in_browser(self.env.MMPM_MAGICMIRROR_URI.get())
        elif args.command == "ui":
            self.open_in_browser(f"http://{urls.HOST}:{urls.MMPM_UI_PORT}")
        elif args.command == "mm-wiki":
            self.open_in_browser(urls.MAGICMIRROR_WIKI_URL)
        elif args.command == "mm-docs":
            self.open_in_browser(urls.MAGICMIRROR_DOCUMENTATION_URL)
        elif args.command == "mmpm-wiki":
            self.open_in_browser(urls.MMPM_WIKI_URL)
        else:
            logger.error(f"No arguments provided. See '{self.app_name} {self.name} --help'")
