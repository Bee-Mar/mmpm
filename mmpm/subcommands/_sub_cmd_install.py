#!/usr/bin/env python3
""" Command line options for 'install' subcommand """
from typing import List

from mmpm.constants import color
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.utils import confirm

logger = MMPMLogFactory.get_logger(__name__)


class Install(SubCmd):
    """
    The 'Install' subcommand allows users to install MagicMirror packages to their modules folder, and handles much of the dependency installation

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "install"
        self.help = "Install MagicMirror packages"
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

        results: List[MagicMirrorPackage] = []

        for name in extra:
            results.extend([pkg for pkg in self.database.packages if name == pkg.title])

            if not results:
                logger.error("Unable to locate package(s) based on query.")

        for package in results:
            if package.is_installed:
                logger.error(f"'{package.title}' is already installed")
                continue

            if not args.assume_yes and not confirm(f"Install {package.title} ({package.repository})?"):
                continue

            if package.install():
                logger.info(f"Installed {color.n_green(package.title)} ({package.repository})")
            elif confirm(f"Installation failed. Would you like to remove {package.title}?"):
                package.is_installed = True
                package.remove()
