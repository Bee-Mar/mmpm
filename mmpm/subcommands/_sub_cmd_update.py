#!/usr/bin/env python3
""" Command line options for 'update' subcommand """

import mmpm.utils
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogFactory.get_logger(__name__)


class Update(SubCmd):
    """
    The 'Update' subcommand checks for available updates on all installed packages, MagicMirror and MMPM itself

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
        magicmirror (MagicMirror): An instance of the MagicMirror object (similar to a MagicMirrorPackage)
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "update"
        self.help = "Check for updates for installed packages, MMPM, and MagicMirror"
        self.usage = f"{self.app_name} {self.name}"
        self.magicmirror = MagicMirror()
        self.database = MagicMirrorDatabase()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

    def exec(self, args, extra):
        if extra:
            logger.error(f"Extra arguments are not accepted. See '{self.app_name} {self.name} --help'")
            return

        self.database.load(update=True)

        can_upgrade_mmpm = mmpm.utils.update_available()
        can_upgrade_magicmirror = self.magicmirror.update()
        available_upgrades = self.database.update(
            can_upgrade_mmpm=can_upgrade_mmpm,
            can_upgrade_magicmirror=can_upgrade_magicmirror,
        )

        if not available_upgrades:
            print("Everything is up to date.")
            return

        print(f"{available_upgrades} upgrade(s) available. Run `mmpm list --upgradable` for details")
