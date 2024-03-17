#!/usr/bin/env python3
""" Command line options for 'db' subcommand """


from shutil import which
from time import sleep

from mmpm.constants import urls
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.ui import MMPMui
from mmpm.utils import confirm

logger = MMPMLogFactory.get_logger(__name__)


class Ui(SubCmd):
    """
    The 'Ui' subcommand allows users to interact with the MMPM user interface (UI), which includes
    displaying the UI URL, checking its status, installing, or removing it.

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
        ui (MMPMui): An instance of the MMPMui class for managing the MMPM user interface.
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "ui"
        self.help = f"Interact with the {self.app_name} UI "
        self.usage = f"{self.app_name} {self.name} [--url] [--status] <install/remove>"
        self.database = MagicMirrorDatabase()
        self.ui = MMPMui()
        self.env = MMPMEnv()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-u",
            "--url",
            action="store_true",
            help=f"display the url of the {self.app_name} {self.name}",
            dest="url",
        )

        self.parser.add_argument(
            "--status",
            action="store_true",
            help=f"display the status of the {self.app_name} {self.name}",
            dest="status",
        )

        self.parser.add_argument(
            "--start",
            action="store_true",
            help=f"Start the {self.app_name} {self.name}",
            dest="start",
        )

        self.parser.add_argument(
            "--restart",
            action="store_true",
            help=f"Restart the {self.app_name} {self.name}",
            dest="restart",
        )

        self.parser.add_argument(
            "--stop",
            action="store_true",
            help=f"Stop the {self.app_name} {self.name}",
            dest="stop",
        )

        subparsers = self.parser.add_subparsers(
            dest="command",
            description=f"use `{self.app_name} {self.name} <subcommand> --help` to see more details",
            title=f"{self.app_name} {self.name} subcommands",
            metavar="",
        )

        install_parser = subparsers.add_parser("install", help=f"Install the {self.app_name} {self.name}")

        install_parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            help="assume yes",
            dest="assume_yes",
        )

        remove_parser = subparsers.add_parser("remove", help=f"Remove the {self.app_name} {self.name}")

        remove_parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            help="assume yes",
            dest="assume_yes",
        )

        reinstall_parser = subparsers.add_parser("reinstall", help=f"Reinstall the {self.app_name} {self.name}")

        reinstall_parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            help="assume yes",
            dest="assume_yes",
        )

    def exec(self, args, extra):
        if not which("pm2"):
            logger.fatal("pm2 is not in your PATH. Please run `npm install -g pm2`, and run the UI installation again.")
            return

        if not self.database.is_initialized():
            self.database.load()

        if self.env.MMPM_IS_DOCKER_IMAGE.get():
            logger.error("MMPM is a Docker image. Unable to interact with MMPM UI from CLI.")
            return

        if extra:
            logger.error(f"Extra arguments are not accepted. See '{self.app_name} {self.name} --help'")
            return

        if args.url:
            print(f"http://{urls.HOST}:{urls.MMPM_UI_PORT}")

        elif args.status:
            self.ui.status()

        elif args.start:
            self.ui.start()

        elif args.stop:
            self.ui.stop()

        elif args.restart:
            self.ui.stop()
            sleep(1)
            self.ui.start()

        elif args.command == "install":
            if not args.assume_yes and not confirm("Are you sure you want to install the MMPM UI?"):
                return

            if not self.ui.install():
                logger.error("Failed to install MMPM UI")
                self.ui.delete()
            else:
                logger.info("Installed MMPM-UI")
                print("Run `mmpm ui --url` to display the UI address, or execute `mmpm open --ui` to open it.")

        elif args.command == "reinstall":
            if not args.assume_yes and not confirm("Are you sure you want to reinstall the MMPM UI?"):
                return

            if not self.ui.remove():
                logger.error("Failed to remove MMPM UI")
                self.ui.delete()

            sleep(2)

            if not self.ui.install():
                logger.error("Failed to install MMPM UI")
                self.ui.delete()
            else:
                logger.info("Reinstalled MMPM-UI")
                print("Run `mmpm ui --url` to display the UI address, or execute `mmpm open --ui` to open it.")

        elif args.command == "remove":
            if not args.assume_yes and not confirm("Are you sure you want to remove the MMPM UI?"):
                return

            if not self.ui.remove():
                logger.error("Failed to remove MMPM UI")
                self.ui.delete()
        else:
            logger.error(f"No arguments provided. See '{self.app_name} {self.name} --help'")
