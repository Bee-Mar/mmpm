"""Command line options for 'sync' subcommand"""

from mmpm.constants import color
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.lockfile import Lockfile
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogFactory.get_logger(__name__)


class Sync(SubCmd):
    """
    The 'Sync' subcommand reads mmpm.lock and makes the installed packages match
    it: missing packages are cloned, and every package is checked out at its
    locked commit with dependencies installed. Useful for reproducing a setup on
    new hardware or repairing one that has drifted.
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "sync"
        self.lockfile = Lockfile()
        self.help = "Clone, checkout, and install packages to match the versions recorded in mmpm.lock"
        self.usage = f"{self.app_name} {self.name}"

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

    def exec(self, args, extra):
        entries = self.lockfile.load()

        if not entries:
            logger.info("The lock file is empty; nothing to sync. Packages are recorded as they are installed or upgraded.")
            return

        failures = 0

        for directory, entry in entries.items():
            package = MagicMirrorPackage(
                title=directory,
                repository=entry.get("repository", ""),
                directory=directory,
            )

            success, error = package.sync(entry.get("sha", ""))

            if success:
                print(f"{color.n_green(directory)}@{entry.get('sha', '')[:8]} ✓")
            else:
                failures += 1
                logger.error(f"Failed to sync {directory}: {error}")

        if failures:
            logger.error(f"{failures} of {len(entries)} package(s) failed to sync. See logs for details.")
        else:
            print(f"All {len(entries)} package(s) match mmpm.lock")
