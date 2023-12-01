#!/usr/bin/env python3
""" Command line options for 'install' subcommand """
from typing import List

from mmpm.gui import MMPMGui
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.utils import prompt

logger = MMPMLogger.get_logger(__name__)


class Install(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "install"
        self.help = "Install MagicMirror packages"
        self.usage = f"{self.app_name} {self.name} <package(s)> [--yes]"
        self.magicmirror = MagicMirror()
        self.gui = MMPMGui()
        self.database = MagicMirrorDatabase()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            default=False,
            help="assume yes for user response and do not show prompt",
            dest="assume_yes",
        )

    def exec(self, args, extra):
        if not extra:
            logger.error(f"No arguments provided. See '{self.app_name} {self.name} --help'")
            return

        if not self.database.is_initialized():
            self.database.load()

        results: List[MagicMirrorPackage] = []

        for name in extra:
            if name == "MagicMirror":
                self.magicmirror.install()
            elif name == "mmpm-gui":
                self.gui.install(args.assume_yes)
            else:
                results.extend(filter(lambda pkg: name == pkg.title, self.database.packages))

                if not results:
                    logger.error("Unable to locate package(s) based on query.")

        for package in results:
            if package.is_installed:
                logger.warning(f"{package.title} is already installed")
                continue

            if package.install(assume_yes=args.assume_yes):
                logger.info(f"Installed {package.title}")
                continue
            elif prompt(f"Installation failed. Would you like to remove {package.title}?"):
                package.is_installed = True
                package.remove(assume_yes=True)
