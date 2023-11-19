#!/usr/bin/env python3
""" Command line options for 'upgrade' subcommand """
import json

from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)


class Upgrade(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "upgrade"
        self.help = "Upgrade packages, MMPM, and/or MagicMirror"
        self.usage = f"{self.app_name} {self.name} <package(s)> [--yes]"
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

    def exec(self, args, extra):
        upgradable = self.database.upgradable()

        if not upgradable["mmpm"] and not upgradable["MagicMirror"] and not upgradable["packages"]:
            logger.msg.info("All packages and applications are up to date.\n ")

        if upgradable["packages"]:
            packages: Set[MagicMirrorPackage] = {MagicMirrorPackage(**package) for package in upgradable["packages"]}
            upgraded: Set[MagicMirrorPackage] = {package for package in packages if package.upgrade()}

            # whichever packages failed to upgrade, we'll hold onto those for future reference
            upgradable["packages"] = [package.serialize() for package in (packages - upgraded)]

        if upgradable["MagicMirror"]:
            upgradable["MagicMirror"] = not self.magicmirror.upgrade()

        if upgradable["mmpm"]:
            print("Run 'pip install --upgrade --no-cache-dir mmpm' to install the latest version of MMPM. Run 'mmpm update' after upgrading.")

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="w", encoding="utf-8") as upgrade_file:
            json.dump(upgradable, upgrade_file)
