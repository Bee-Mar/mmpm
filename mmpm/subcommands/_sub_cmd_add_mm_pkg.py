#!/usr/bin/env python3
""" Command line options for 'add-mm-pkg' subcommand """
from mmpm.logger import MMPMLogger
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)


class AddMmPkg(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "add-mm-pkg"
        self.help = "Manually add MagicMirror packages to your local database (similar to add-apt-repository)"
        self.usage = f"{self.app_name} {self.name} [--title=<title>] [--author=<author>] [--repo=<repo>] [--desc=<description>]"

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-t",
            "--title",
            type=str,
            help="title of MagicMirror package (will be prompted if not provided)",
            dest="title",
        )

        self.parser.add_argument(
            "-a",
            "--author",
            type=str,
            help="author of MagicMirror package (will be prompted if not provided)",
            dest="author",
        )

        self.parser.add_argument(
            "-r",
            "--repo",
            type=str,
            help="repo URL of MagicMirror package (will be prompted if not provided)",
            dest="repo",
        )

        self.parser.add_argument(
            "-d",
            "--desc",
            type=str,
            help="description of MagicMirror package (will be prompted if not provided)",
            dest="desc",
        )

        self.parser.add_argument(
            "--remove",
            nargs="+",
            help="remove MagicMirror package (similar to `add-apt-repository` --remove)",
            dest="remove",
        )

        self.parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            default=False,
            help="assume yes for user response and do not show prompt (used with --remove)",
            dest="assume_yes",
        )

    def exec(self, args, extra):
        if args.remove:
            self.database.remove_mm_pkg(args.remove, assume_yes=args.assume_yes)
        else:
            self.database.add_mm_pkg(args.title, args.author, args.repo, args.desc)
