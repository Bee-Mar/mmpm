#!/usr/bin/env python3
""" Command line options for 'show' subcommand """

from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.package import RemotePackage
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogFactory.get_logger(__name__)


class Show(SubCmd):
    """
    The 'Show' subcommand allows users to view more details about a given MagicMirror package

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "show"
        self.help = "Show details about one or more packages"
        self.usage = f"{self.app_name} {self.name} [--remote]"
        self.database = MagicMirrorDatabase()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-r",
            "--remote",
            action="store_true",
            help="display remote detail for package(s) from GitHub/GitLab/Bitbucket APIs",
            dest="remote",
        )

    def exec(self, args, extra):
        if not extra:
            logger.error(f"No arguments provided. See '{self.app_name} {self.name} --help'")

        if not self.database.is_initialized():
            self.database.load()

        if args.remote:
            health = RemotePackage.health()

            for status in health.values():
                if status["error"]:
                    logger.fatal(status["error"])
                elif status["warning"]:
                    logger.warning(status["warning"])

        for query in extra:
            results = self.database.search(query, title_only=True)

            if not results:
                logger.error(f"No results found for '{query}'")

            for package in results:
                logger.debug(f"Showing information for {package}")
                package.display(remote=args.remote, detailed=True)
