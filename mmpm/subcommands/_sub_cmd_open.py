#!/usr/bin/env python3
""" Command line options for 'open' subcommand """
from os import getenv, system
from pathlib import PosixPath
from shutil import copyfile
from typing import Optional

from mmpm.constants import paths, urls
from mmpm.env import MMPMEnv
from mmpm.logger import MMPMLogger
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.utils import run_cmd

logger = MMPMLogger.get_logger(__name__)


class Open(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "open"
        self.help = "Open config files, documentation, wikis, and MagicMirror itself"
        self.usage = f"{self.app_name} {self.name} [option]"
        self.env = MMPMEnv()

    def edit(self, file: PosixPath) -> Optional[None]:
        """
        Checks if the requested file exists, and if not, the file is created. Then, the 'edit'
        command is used to open the file.

        Parameters:
            file (PosixPath): file path to open with 'edit' command

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

        logger.info(f"Opening {file} for user to edit")
        command = getenv("EDITOR", getenv("VISUAL", "edit"))
        system(f"{command} {file}")

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        group = self.parser.add_mutually_exclusive_group()

        group.add_argument(
            "--config",
            action="store_true",
            help="open MagicMirror config/config.js file in your $EDITOR",
            dest="config",
        )

        group.add_argument(
            "--css",
            action="store_true",
            help="open MagicMirror css/custom.css file (if it exists) in your $EDITOR",
            dest="custom_css",
        )

        group.add_argument(
            "--gui",
            action="store_true",
            help="open the MMPM GUI in your default browser",
            dest="gui",
        )

        group.add_argument(
            "--magicmirror",
            action="store_true",
            help="open MagicMirror in your default browser (uses the MMPM_MAGICMIRROR_URI address)",
            dest="magicmirror",
        )

        group.add_argument(
            "--mm-wiki",
            action="store_true",
            help="open the MagicMirror GitHub wiki in your default browser",
            dest="mm_wiki",
        )

        group.add_argument(
            "--mm-docs",
            action="store_true",
            help="open the MagicMirror documentation in your default browser",
            dest="mm_docs",
        )

        group.add_argument(
            "--mmpm-wiki",
            action="store_true",
            help="open the MMPM GitHub wiki in your default browser",
            dest="mmpm_wiki",
        )

        group.add_argument(
            "--env",
            action="store_true",
            help="open the MMPM run-time environment variables JSON configuration file in your $EDITOR",
            dest="mmpm_env",
        )

    def exec(self, args, extra):
        if extra:
            logger.msg.extra_args(args.subcmd)
        elif args.config:
            root = self.env.mmpm_magicmirror_root.get() / "config"
            config_js = root / "config.js"
            config_js_sample = root / "config.js.sample"

            if not config_js.stat().st_size and config_js_sample.exists():
                copyfile(config_js_sample, config_js)

            self.edit(config_js)

        elif args.custom_css:
            self.edit(self.env.mmpm_magicmirror_root.get() / "css" / "custom.css")
        elif args.magicmirror:
            run_cmd(["xdg-open", self.env.MMPM_MAGICMIRROR_URI.get()], background=True)
        elif args.gui:
            run_cmd(["xdg-open", self.gui.get_uri()], background=True)
        elif args.mm_wiki:
            run_cmd(["xdg-open", urls.MAGICMIRROR_WIKI_URL], background=True)
        elif args.mm_docs:
            run_cmd(["xdg-open", urls.MAGICMIRROR_DOCUMENTATION_URL], background=True)
        elif args.mmpm_wiki:
            run_cmd(["xdg-open", urls.MMPM_WIKI_URL], background=True)
        elif args.mmpm_env:
            self.edit(paths.MMPM_ENV_FILE)
        else:
            logger.msg.no_args(args.subcmd)
