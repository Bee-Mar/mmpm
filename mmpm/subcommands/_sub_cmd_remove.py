#!/usr/bin/env python3
""" Command line options for 'remove' subcommand """
from mmpm.gui import MMPMGui
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)

class Remove(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "remove"
        self.help = "Remove installed packages"
        self.usage = f"{self.app_name} {self.name} <package(s)> [--yes]"
        self.magicmirror = MagicMirror()
        self.gui = MMPMGui()
        self.database = MagicMirrorDatabase()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument( '--magicmirror',
                action='store_true',
                default=False,
                help='remove MagicMirror, if not already installed',
                dest='magicmirror'
                )

        self.parser.add_argument(
                '-y',
                '--yes',
                action='store_true',
                default=False,
                help='assume yes for user response and do not show prompt',
                dest='assume_yes'
                )

        self.parser.add_argument(
                '--gui',
                action='store_true',
                default=False,
                help='remove the MMPM GUI (sudo permission required)',
                dest='gui'
                )

    def exec(self, args, extra):
        if not extra:
            logger.msg.no_args(args.subcmd)
            return

        for name in extra:
            if name == "MagicMirror":
                self.magicmirror.remove()
            elif name == "mmpm-gui":
                self.gui.remove(args.assume_yes)
            else:
                for package in filter(lambda pkg : name == pkg.title, self.database.packages):
                    package.remove(assume_yes=args.assume_yes)
