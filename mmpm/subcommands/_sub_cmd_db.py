#!/usr/bin/env python3
""" Command line options for 'db' subcommand """
import json

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import JsonLexer

from mmpm.constants import color
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogFactory.get_logger(__name__)


class Db(SubCmd):
    """
    The 'Db' subcommand allows users to refresh or display basic details about the MagicMirror packages database.

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "db"
        self.help = "Display database metadata, or display raw database contents"
        self.usage = f"{self.app_name} {self.name} [--<option>]"
        self.database = MagicMirrorDatabase()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        group = self.parser.add_mutually_exclusive_group()

        group.add_argument(
            "-i",
            "--info",
            action="store_true",
            help="display database metadata",
            dest="info",
        )

        group.add_argument(
            "-d",
            "--dump",
            action="store_true",
            help="dump the database contents to stdout as JSON",
            dest="dump",
        )

    def exec(self, args, extra):
        if not self.database.is_initialized():
            self.database.load()

        if extra:
            logger.error(f"Extra arguments are not accepted. See '{self.app_name} {self.name} --help'")
            return

        if args.info:
            info = self.database.info()
            convert_string = lambda s: " ".join([s.split("_")[0].capitalize()] + [word.lower() for word in s.split("_")[1:]])

            for key, value in info.items():
                print(f"{color.n_green(convert_string(key))}:\n\t{value}\n")

        elif args.dump:
            print(
                highlight(
                    json.dumps(
                        self.database.packages,
                        indent=2,
                        default=lambda package: package.serialize(),
                    ),
                    JsonLexer(),
                    TerminalFormatter(),
                ),
            )
        else:
            logger.error(f"No arguments provided. See '{self.app_name} {self.name} --help'")
