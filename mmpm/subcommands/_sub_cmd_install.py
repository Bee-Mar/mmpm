#!/usr/bin/env python3
""" Command line options for 'install' subcommand """
from typing import List

from mmpm.gui import MMPMGui
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)


class Install(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "install"
        self.help = "Install MagicMirror packages"
        self.usage = f"{self.app_name} {self.name}"
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
            logger.msg.no_args(args.subcmd)
            return

        results: List[MagicMirrorPackage] = []

        for name in extra:
            if name == "MagicMirror":
                self.magicmirror.install()
            elif name == "mmpm-gui":
                self.gui.install(args.assume_yes)
            else:
                results.extend(filter(lambda pkg: name == pkg.title, self.database.packages))

                if not results:
                    logger.msg.error("Unable to locate package(s) based on query.")

        for package in results:
            package.install(assume_yes=args.assume_yes)
