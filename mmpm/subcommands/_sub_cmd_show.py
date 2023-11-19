#!/usr/bin/env python3
""" Command line options for 'show' subcommand """

from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.package import RemotePackage
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)

class Show(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "show"
        self.help = "Show details about one or more packages"
        self.usage = f"{self.app_name} {self.name} [--remote]"
        self.database = MagicMirrorDatabase()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
                '-r',
                '--remote',
                action='store_true',
                help='display remote detail for package(s) from GitHub/GitLab/Bitbucket APIs',
                dest='remote'
                )

    def exec(self, args, extra):
        if not extra:
            logger.msg.no_args(args.subcmd)

        if args.remote:
            health = RemotePackage.health() # TODO: figure out something better than this

            for status in health.values():
                if status['error']:
                    logger.msg.fatal(status['error'])
                elif status['warning']:
                    logger.msg.warning(status['warning'])

        for query in extra:
            for package in self.database.search(query, title_only=True):
                package.display(remote=args.remote, detailed=True)

