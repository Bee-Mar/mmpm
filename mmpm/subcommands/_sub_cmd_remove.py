#!/usr/bin/env python3
""" Command line options for 'remove' subcommand """
from mmpm.constants import color
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)


class Remove(SubCmd):
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

        for name in extra:
            for package in filter(lambda pkg: name == pkg.title, self.database.packages):
                if not package.is_installed:
                    logger.error(f"'{package.title}' is not installed")
                    continue

                if package.remove(assume_yes=args.assume_yes):
                    logger.info(f"Removed {color.n_green(package.title)}")
