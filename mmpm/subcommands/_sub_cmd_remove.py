#!/usr/bin/env python3
""" Command line options for 'remove' subcommand """
from typing import List

from mmpm.constants import color
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.utils import confirm

logger = MMPMLogFactory.get_logger(__name__)


class Remove(SubCmd):
    """
    The 'Remove' subcommand allows users to uninstall MagicMirror packages from their modules folder

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "remove"
        self.help = "Remove installed MagicMirror packages"
        self.usage = f"{self.app_name} {self.name} <package(s)> [--yes]"
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

        package_titles: List[str] = {package.title: package for package in self.database.packages}

        for name in extra:
            package = package_titles.get(name)

            if package is None:
                logger.error(f"'{name}' is not found in the installed packages")
                continue

            if not package.is_installed:
                logger.error(f"'{package.title}' is not installed")
                continue

            if not args.assume_yes and not confirm(f"Remove {package.title} ({package.repository})?"):
                continue

            if package.remove():
                logger.info(f"Removed {color.n_green(package.title)} ({package.repository})")
