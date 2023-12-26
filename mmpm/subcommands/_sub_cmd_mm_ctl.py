#!/usr/bin/env python3
""" Command line options for 'mm-ctl' subcommand """
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.controller import MagicMirrorController
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.utils import confirm

logger = MMPMLogFactory.get_logger(__name__)


class MmCtl(SubCmd):
    """
    The 'MmCtl' subcommand allows users to interact with the MagicMirror itself
    by hiding/showing modules, getting information about which are visible,
    even starting/stopping/restarting MagicMirror itself.

    Custom Attributes:
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
        controller (MagicMirrorController): An instance of the MagicMirrorController for interacting with MagicMirror
        env (MMPMEnv): A singleton of MMPMEnv which contains environment variables
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "mm-ctl"
        self.help = "Commands to interact with/control MagicMirror"
        self.usage = f"{self.app_name} {self.name} [--<option>]"
        self.controller = MagicMirrorController()
        self.magicmirror = MagicMirror()
        self.env = MMPMEnv()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        subparsers = self.parser.add_subparsers(
            dest="command",
            description=f"use `{self.app_name} {self.name} <add/remove> --help` to see more details",
            title=f"{self.app_name} {self.name} subcommands",
            metavar="",
        )

        install_parser = subparsers.add_parser(
            "install",
            help="Install MagicMirror",
            usage=f"{self.app_name} {self.name} install [--yes]",
        )

        install_parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            help="assume yes for user response and do not show prompt",
            dest="assume_yes",
        )

        remove_parser = subparsers.add_parser(
            "remove",
            help="Remove MagicMirror",
            usage=f"{self.app_name} {self.name} remove [--yes]",
        )

        remove_parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            help="assume yes for user response and do not show prompt",
            dest="assume_yes",
        )

        self.parser.add_argument(
            "--status",
            action="store_true",
            help="show the hidden/visible status and key(s) of module(s) on your MagicMirror",
            dest="status",
        )

        self.parser.add_argument(
            "--hide",
            nargs="+",
            help="hide module(s) on your MagicMirror via provided key(s)",
            dest="hide",
        )

        self.parser.add_argument(
            "--show",
            nargs="+",
            help="show module(s) on your MagicMirror via provided key(s)",
            dest="show",
        )

        self.parser.add_argument(
            "--start",
            action="store_true",
            help="start MagicMirror; works with pm2 and docker-compose",
            dest="start",
        )

        self.parser.add_argument(
            "--stop",
            action="store_true",
            help="stop MagicMirror; works with pm2 and docker-compose",
            dest="stop",
        )

        self.parser.add_argument(
            "--restart",
            action="store_true",
            help="restart MagicMirror; works with pm2 and docker-compose",
            dest="restart",
        )

    def exec(self, args, extra):
        if extra:
            logger.error(f"Extra arguments are not accepted. See '{self.app_name} {self.name} --help'")
        elif args.command == "install":
            if confirm("Are your sure you want to install MagicMirror?"):
                self.magicmirror.install()
        elif args.command == "remove":
            if confirm("Are your sure you want to remove MagicMirror?"):
                self.magicmirror.remove()
        elif args.status:
            self.controller.status()
        elif args.hide:
            self.controller.hide(args.hide)
        elif args.show:
            self.controller.show(args.show)
        elif args.start:
            if self.env.MMPM_IS_DOCKER_IMAGE.get():
                logger.fatal("Cannot execute this command within a docker image")
            else:
                self.controller.start()
        elif args.stop:
            if self.env.MMPM_IS_DOCKER_IMAGE.get():
                logger.fatal("Cannot execute this command within a docker image")
            else:
                self.controller.stop()
        elif args.restart:
            if self.env.MMPM_IS_DOCKER_IMAGE.get():
                logger.fatal("Cannot execute this command within a docker image")
            else:
                self.controller.restart()
        else:
            logger.error(f"No arguments provided. See '{self.app_name} {self.name} --help'")
