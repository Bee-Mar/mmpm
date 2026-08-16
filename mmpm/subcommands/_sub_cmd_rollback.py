"""Command line options for 'rollback' subcommand"""

import string
from typing import Optional

from mmpm import utils
from mmpm.constants import color
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.lockfile import Lockfile
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogFactory.get_logger(__name__)


class Rollback(SubCmd):
    """
    The 'Rollback' subcommand restores a package to a version the user previously
    had installed. With no options it rolls back to the most recently replaced
    commit recorded in mmpm.lock; --select opens an interactive picker over the
    package's full commit history. The chosen commit is recorded in mmpm.lock,
    where it stays until the user upgrades the package again.

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "rollback"
        self.help = "Roll back an installed package to the previously installed version (recorded in mmpm.lock)"
        self.usage = f"{self.app_name} {self.name} <package> [--commit <sha>] [--select] [--history]"
        self.database = MagicMirrorDatabase()
        self.lockfile = Lockfile()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-c",
            "--commit",
            type=str,
            default="",
            help="an exact commit sha to roll back to",
            dest="commit",
        )

        self.parser.add_argument(
            "-s",
            "--select",
            action="store_true",
            default=False,
            help="interactively select a version from the package's commit history",
            dest="select",
        )

        self.parser.add_argument(
            "--history",
            action="store_true",
            default=False,
            help="only display the package's version history",
            dest="history",
        )

        self.parser.add_argument(
            "-n",
            "--count",
            type=int,
            default=15,
            help="number of commits to display in the version history (default: 15)",
            dest="count",
        )

    def exec(self, args, extra):
        if not extra:
            logger.error(f"No package provided. See '{self.app_name} {self.name} --help'")
            return

        if not self.database.is_initialized():
            self.database.load()

        query = " ".join(extra)
        results = [pkg for pkg in self.database.search(query, title_only=True) if pkg.is_installed]

        if not results:
            logger.error(f"No installed package found matching '{query}'")
            return

        package = results[0]

        if args.commit:
            self.__rollback__(package, args.commit)
            return

        if not args.select and not args.history:
            # Default: roll back to the version that was installed before the
            # lock last moved — the precise "undo my last upgrade" case.
            previous = self.lockfile.previous(package.directory.name)

            if previous:
                print(f"Rolling back {color.n_green(package.title)} to previously installed version {previous[:8]}")
                self.__rollback__(package, previous)
            else:
                logger.error(
                    f"No previously installed version of {package.title} is recorded in mmpm.lock. "
                    f"Use '{self.app_name} {self.name} {package.title} --select' to choose a commit from its history."
                )

            return

        history = package.version_history(count=args.count)

        if not history:
            logger.error(f"Unable to retrieve version history for {package.title}")
            return

        for index, commit in enumerate(history):
            marker = color.n_green(" (current)") if commit["is_current"] else ""

            if commit.get("was_installed"):
                marker += color.n_yellow(f" (installed until {commit.get('replaced', 'unknown')})")

            print(f"  [{index}] {commit['sha'][:8]}  {commit['date']}  {commit['subject']}{marker}")

        if args.history:
            return

        def valid_selection(value: str) -> Optional[str]:
            if not value:
                return None  # blank cancels the rollback

            if value.isdigit():
                return None if int(value) < len(history) else f"Index {value} is out of range (0-{len(history) - 1})"

            if len(value) >= 4 and all(character in string.hexdigits for character in value):
                return None

            return f"'{value}' is not a valid index or commit sha"

        selection = utils.prompt("Select a version to roll back to (index or sha, blank to cancel): ", validate=valid_selection)

        if not selection:
            logger.info("Rollback cancelled")
            return

        sha = history[int(selection)]["sha"] if selection.isdigit() else selection

        self.__rollback__(package, sha)

    def __rollback__(self, package, sha: str) -> None:
        success, error = package.rollback(sha)

        if success:
            print(
                f"Rolled back {color.n_green(package.title)} to {sha[:8]} and locked it in mmpm.lock. "
                f"Run '{self.app_name} upgrade' to move it back to the latest version."
            )
        else:
            logger.error(f"Failed to roll back {package.title}: {error}")
