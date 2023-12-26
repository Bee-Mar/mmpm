#!/usr/bin/env python3
""" Command line options for 'upgrade' subcommand """
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

logger = MMPMLogFactory.get_logger(__name__)


class Upgrade(SubCmd):
    """
    The 'Upgrade' subcommand retrieves available updates for packages and MagicMirror and attempts to install their dependencies

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
        magicmirror (MagicMirror): An instance of the MagicMirror object (similar to a MagicMirrorPackage)
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "upgrade"
        self.help = "Upgrade packages, MMPM, and/or MagicMirror"
        self.usage = f"{self.app_name} {self.name} <package(s)> [--yes]"
        self.database = MagicMirrorDatabase()
        self.magicmirror = MagicMirror()
        self.env = MMPMEnv()

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
        packages_to_upgrade: List[MagicMirrorPackage] = []

        if args.force:
            for package in filter(lambda pkg: pkg.is_installed, self.database.packages):
                package.upgrade(force=True)

            upgradable["packages"] = {}

        elif not any(upgradable.values()):
            logger.info("All packages and applications are up to date.\n ")
            return

        if upgradable["packages"]:
            packages = {MagicMirrorPackage(**package) for package in upgradable["packages"]}
            packages_to_upgrade.extend(filter(lambda pkg: pkg.upgrade(), packages))
            upgradable["packages"] = [package.serialize() for package in (packages - set(packages_to_upgrade))]

        upgradable["MagicMirror"] = upgradable["MagicMirror"] and self.magicmirror.upgrade()

        if upgradable["mmpm"]:
            if self.env.MMPM_IS_DOCKER_IMAGE.get():
                logger.warning("Cannot perform self-upgrade because MMPM is a Docker image. Stop MMPM and run `docker pull karsten13/mmpm:latest`")
            else:
                upgradable["mmpm"] = utils.upgrade()

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="w", encoding="utf-8") as upgrade_file:
            json.dump(upgradable, upgrade_file)
