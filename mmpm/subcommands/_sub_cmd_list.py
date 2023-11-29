#!/usr/bin/env python3
""" Command line options for 'list' subcommand """
from argparse import _SubParsersAction

from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)


class List(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "list"
        self.help = "List items such as installed packages, packages available, available upgrades, etc"
        self.usage = f"{self.app_name} {self.name} [-a] [-i] [-e] [-c] [-g] [--upgradable]"
        self.database = MagicMirrorDatabase()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        # FIXME: this is almost correct. --title-only shouldn't be allowed with --gui-url or --upgradable

        self.parser.add_argument(
            "-t",
            "--title-only",
            action="store_true",
            help="display the title only of packages (used with -c, -a, -e, or -i)",
            dest="title_only",
        )

        group = self.parser.add_mutually_exclusive_group()

        group.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="list all available packages in the marketplace",
            dest="all",
        )

        group.add_argument(
            "-i",
            "--installed",
            action="store_true",
            help="list all locally installed packages",
            dest="installed",
        )

        group.add_argument(
            "-e",
            "--exclude-installed",
            action="store_true",
            help="list all available packages in the marketplace, excluding locally installed packages",
            dest="exclude_installed",
        )

        group.add_argument(
            "-c",
            "--categories",
            action="store_true",
            help="list all available package categories",
            dest="categories",
        )

        group.add_argument(
            "-g",
            "--gui-url",
            action="store_true",
            help="list the URL of the MMPM GUI",
            dest="gui_url",
        )

        group.add_argument(
            "--upgradable",
            action="store_true",
            help="list packages that have available upgrades",
            dest="upgradable",
        )

    def exec(self, args, extra):
        if not self.database.is_initialized():
            self.database.load()

        if args.installed:
            for package in self.database.packages:
                if package.is_installed:
                    package.display(title_only=args.title_only, hide_installed_indicator=True)

        elif args.all or args.exclude_installed:
            for package in self.database.packages:
                package.display(title_only=args.title_only, exclude_installed=args.exclude_installed)

        elif args.categories:
            self.database.display_categories(title_only=args.title_only)
        elif args.gui_url:
            print(self.gui.get_uri())
        elif args.upgradable:
            self.database.display_upgradable()
        else:
            logger.error(f"No arguments provided. See '{self.app_name} {self.name} --help'")
