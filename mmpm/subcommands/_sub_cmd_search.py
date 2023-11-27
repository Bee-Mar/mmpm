#!/usr/bin/env python3
""" Command line options for 'search' subcommand """
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)


class Search(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "search"
        self.help = f"Search for MagicMirror packages"
        self.usage = f"{self.app_name} {self.name} <query> [--case-sensitive] [--exclude-installed]"
        self.database = MagicMirrorDatabase()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-t",
            "--title-only",
            action="store_true",
            help="only show the title of the packages matching the search results",
            dest="title_only",
        )

        self.parser.add_argument(
            "-c",
            "--case-sensitive",
            action="store_true",
            help="search for packages using a case-sensitive query",
            dest="case_sensitive",
        )

        self.parser.add_argument(
            "-e",
            "--exclude-installed",
            action="store_true",
            help="exclude installed packages from search results",
            dest="exclude_installed",
        )

    def exec(self, args, extra):
        if not extra:
            logger.msg.no_args(args.subcmd)
            return

        if len(extra) > 1:
            logger.fatal(f"Too many arguments. `{self.app_name} {args.subcmd}` only accepts one search argument")
            return

        if not self.database.is_initialized():
            self.database.load()

        query_result = self.database.search(extra[0], case_sensitive=args.case_sensitive, title_only=args.title_only)

        for package in query_result:
            package.display(title_only=args.title_only)
