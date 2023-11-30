#!/usr/bin/env python3
""" Command line options for 'add-mm-pkg' subcommand """
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)


class MmPkg(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "mm-pkg"
        self.help = "Manually add/remove MagicMirror packages in your local database (similar to add-apt-repository)"
        self.usage = f"{self.app_name} {self.name} <add/remove> [options]"
        self.database = MagicMirrorDatabase()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)
        subparsers = self.parser.add_subparsers(
            dest="command",
            description=f"use `{self.app_name} {self.name} <subcommand> --help` to see more details",
            title=f"{self.app_name} {self.name} subcommands",
            metavar="",
        )

        install_parser = subparsers.add_parser("add", help="Add a custom MagicMirror package to the local database")

        install_parser.add_argument(
            "-t",
            "--title",
            type=str,
            help="title of MagicMirror package",
            dest="title",
        )

        install_parser.add_argument(
            "-a",
            "--author",
            type=str,
            help="author of MagicMirror package",
            dest="author",
        )

        install_parser.add_argument(
            "-r",
            "--repo",
            type=str,
            help="repo URL of MagicMirror package",
            dest="repo",
        )

        install_parser.add_argument(
            "-d",
            "--desc",
            type=str,
            help="description of MagicMirror package",
            dest="desc",
        )

        remove_parser = subparsers.add_parser("remove", help="Remove a custom MagicMirror package from the local database")

        remove_parser.add_argument(
            "pkg_name",
            nargs="+",
            help="name(s) of the MagicMirror package(s) to remove",
        )
        remove_parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            default=False,
            help="assume yes for user response and do not show prompt",
            dest="assume_yes",
        )

    def exec(self, args, extra):
        if not self.database.is_initialized():
            self.database.load()

        if args.command == "install":
            self.database.add_mm_pkg(args.title, args.author, args.repo, args.desc)
        elif args.command == "remove":
            self.database.remove_mm_pkg(args.pkg_name, assume_yes=args.assume_yes)
