"""Command line options for 'upgrade' subcommand"""

import json
from typing import List

from mmpm import utils
from mmpm.constants import paths
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.utils import confirm

logger = MMPMLogFactory.get_logger(__name__)


class Upgrade(SubCmd):
    """
    The 'Upgrade' subcommand retrieves available updates for packages and MagicMirror and attempts to install their dependencies

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
        magicmirror (MagicMirror): An instance of the MagicMirror object (similar to a MagicMirrorPackage)
    """

    env: MMPMEnv = MMPMEnv()

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "upgrade"
        self.help = "Upgrade packages, MMPM, and/or MagicMirror"
        self.usage = f"{self.app_name} {self.name} [package(s)] [--yes] [--force]"
        self.database = MagicMirrorDatabase()
        self.magicmirror = MagicMirror()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            default=False,
            help="assume yes for user response and do not show prompt",
            dest="assume_yes",
        )

        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            default=False,
            help="force an attempted upgrade regardless if the package isn't 'upgradable'",
            dest="force",
        )

    def exec(self, args, extra):
        if not self.database.is_initialized():
            self.database.load()

        upgradable = self.database.upgradable()
        requested = set(extra)

        upgradable_packages = {MagicMirrorPackage(**package) for package in upgradable["packages"]}

        if args.force:
            candidates = {package for package in self.database.packages if package.is_installed}
        else:
            candidates = upgradable_packages

        upgrade_magicmirror = upgradable["MagicMirror"]
        upgrade_mmpm = upgradable["mmpm"]

        if requested:
            upgrade_magicmirror = upgrade_magicmirror and "MagicMirror" in requested
            upgrade_mmpm = upgrade_mmpm and self.app_name in requested

            candidates = {package for package in candidates if package.title in requested}

            installed_titles = {package.title for package in self.database.packages if package.is_installed}

            for name in requested - {package.title for package in candidates} - {"MagicMirror", self.app_name}:
                if name not in installed_titles:
                    logger.error(f"'{name}' is not an installed package")
                else:
                    logger.error(f"No upgrade available for '{name}'. Use `{self.app_name} {self.name} --force {name}` to force an upgrade.")

        if not candidates and not upgrade_magicmirror and not upgrade_mmpm:
            if not requested:
                logger.info("All packages and applications are up to date.")
            return

        upgraded: List[MagicMirrorPackage] = []

        for package in candidates:
            if not args.assume_yes and not confirm(f"Upgrade {package.title}?"):
                continue

            success, error = package.upgrade(force=args.force)

            if success:
                upgraded.append(package)
            else:
                logger.error(f"Failed to upgrade {package.title}: {error}")

        upgradable["packages"] = [package.serialize() for package in (upgradable_packages - set(upgraded))]

        if upgrade_magicmirror and (args.assume_yes or confirm("Upgrade MagicMirror?")):
            # magicmirror.upgrade() returns stderr (a truthy str) on some failures, so compare against True exactly
            upgradable["MagicMirror"] = self.magicmirror.upgrade() is not True

        if upgrade_mmpm:
            if self.env.MMPM_IS_DOCKER_IMAGE.get():
                logger.warning("Cannot perform self-upgrade because MMPM is a Docker image. Stop MMPM and run `docker pull karsten13/mmpm:latest`")
            elif args.assume_yes or confirm(f"Upgrade {self.app_name}?"):
                upgradable["mmpm"] = not utils.upgrade()

        if not requested and not args.force and upgradable["packages"]:
            logger.info(f"Some packages were not upgraded. Run `{self.app_name} list --upgradable` to see what remains.")

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="w", encoding="utf-8") as upgrade_file:
            json.dump(upgradable, upgrade_file)
