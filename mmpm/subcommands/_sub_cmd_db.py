#!/usr/bin/env python3
""" Command line options for 'db' subcommand """
import sys

from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)


class Db(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "db"
        self.help = "Refresh or display basic details about the database"
        self.usage = f"{self.app_name} {self.name} [--refresh] [--info] [--dump]"
        self.database = MagicMirrorDatabase()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        group = self.parser.add_mutually_exclusive_group()

        group.add_argument(
            "-i",
            "--info",
            action="store_true",
            help="display information about the MagicMirror packages database",
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
            self.database.info()
        elif args.dump:
            self.database.dump()
        else:
            logger.error(f"No arguments provided. See '{self.app_name} {self.name} --help'")
