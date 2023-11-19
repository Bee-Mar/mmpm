#!/usr/bin/env python3
""" Command line options for 'update' subcommand """
import json
import urllib.request

from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.subcommands.sub_cmd import SubCmd
from pip._internal.operations.freeze import freeze

logger = MMPMLogger.get_logger(__name__)


class Update(SubCmd):
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
            logger.msg.extra_args(args.subcmd)
            return

        self.database.load(refresh=True)

        url = "https://pypi.org/pypi/mmpm/json"
        logger.msg.retrieving("https://pypi.org/pypi/mmpm", "mmpm")
        current_version = ""

        for requirement in freeze(local_only=False):
            info = requirement.split("==")

            if info[0] == "mmpm":
                current_version = info[1]

        contents = urllib.request.urlopen(url).read()
        latest_version = json.loads(contents)["info"]["version"]

        can_upgrade_mmpm = latest_version == current_version
        can_upgrade_magicmirror = self.magicmirror.update()

        available_upgrades = self.database.update(can_upgrade_mmpm=can_upgrade_mmpm, can_upgrade_magicmirror=can_upgrade_magicmirror)

        if not available_upgrades:
            print("All packages and applications are up to date.")
            return

        print(f"{available_upgrades} upgrade(s) available. Run `mmpm list --upgradable` for details")
