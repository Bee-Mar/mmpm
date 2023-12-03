#!/usr/bin/env python3
""" Command line options for 'db' subcommand """
import sys

from mmpm.gui import MMPMGui
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.sub_cmd import SubCmd
from pygments import formatters, highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import JsonLexer

logger = MMPMLogger.get_logger(__name__)


class Ui(SubCmd):
    """
    The 'Ui' subcommand allows users to interact with the MMPM user interface (UI), which includes
    displaying the UI URL, checking its status, installing, or removing it.

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
        gui (MMPMGui): An instance of the MMPMGui class for managing the MMPM user interface.
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "ui"
        self.help = f"Interact with the {self.app_name} UI "
        self.usage = f"{self.app_name} {self.name} [--url] [--status] <install/remove>"
        self.database = MagicMirrorDatabase()
        self.gui = MMPMGui()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-u",
            "--url",
            action="store_true",
            help=f"display the url of the {self.app_name} {self.name}",
            dest="url",
        )

        self.parser.add_argument(
            "-s",
            "--status",
            action="store_true",
            help=f"display the status of the {self.app_name} {self.name}",
            dest="status",
        )

        subparsers = self.parser.add_subparsers(
            dest="command",
            description=f"use `{self.app_name} {self.name} <subcommand> --help` to see more details",
            title=f"{self.app_name} {self.name} subcommands",
            metavar="",
        )

        install_parser = subparsers.add_parser("install", help=f"Install the {self.app_name} {self.name}")

        install_parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            help="assume yes",
            dest="assume_yes",
        )

        remove_parser = subparsers.add_parser("remove", help=f"Remove the {self.app_name} {self.name}")

        remove_parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            help="assume yes",
            dest="assume_yes",
        )

    def exec(self, args, extra):
        if not self.database.is_initialized():
            self.database.load()

        if extra:
            logger.error(f"Extra arguments are not accepted. See '{self.app_name} {self.name} --help'")
            return

        if args.url:
            print(self.gui.get_uri())
        elif args.status:
            raise NotImplementedError("TODO")  # TODO
        elif args.command == "install":
            self.gui.install(assume_yes=args.assume_yes)
        elif args.command == "remove":
            self.gui.remove(assume_yes=args.assume_yes)
        else:
            logger.error(f"No arguments provided. See '{self.app_name} {self.name} --help'")