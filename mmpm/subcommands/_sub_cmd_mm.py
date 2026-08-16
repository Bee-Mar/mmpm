"""Command line options for 'mm' subcommand"""

from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.controller import MagicMirrorController
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.subcommands.sub_cmd import SubCmd
from mmpm.utils import confirm

logger = MMPMLogFactory.get_logger(__name__)


class Mm(SubCmd):
    """
    The 'Mm' subcommand allows users to interact with the MagicMirror itself
    by hiding/showing modules, getting information about which are visible,
    even starting/stopping/restarting MagicMirror itself.

    Custom Attributes:
        controller (MagicMirrorController): An instance of the MagicMirrorController for interacting with MagicMirror
        magicmirror (MagicMirror): An instance of the MagicMirror class for installing/removing MagicMirror
        env (MMPMEnv): A singleton of MMPMEnv which contains environment variables
    """

    env: MMPMEnv = MMPMEnv()

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "mm"
        self.aliases = ["magicmirror"]
        self.help = "Commands to interact with/control MagicMirror"
        self.usage = f"{self.app_name} {self.name} <status/hide/show/start/stop/restart/install/remove>"
        self.controller = MagicMirrorController()
        self.magicmirror = MagicMirror()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, aliases=self.aliases, usage=self.usage, help=self.help)

        subparsers = self.parser.add_subparsers(
            dest="command",
            description=f"use `{self.app_name} {self.name} <subcommand> --help` to see more details",
            title=f"{self.app_name} {self.name} subcommands",
            metavar="",
        )

        subparsers.add_parser("status", help="show the hidden/visible status and key(s) of module(s) on your MagicMirror")

        hide_parser = subparsers.add_parser("hide", help="hide module(s) on your MagicMirror via provided key(s)")
        hide_parser.add_argument("keys", nargs="+", help="key(s) of the module(s) to hide")

        show_parser = subparsers.add_parser("show", help="show module(s) on your MagicMirror via provided key(s)")
        show_parser.add_argument("keys", nargs="+", help="key(s) of the module(s) to show")

        subparsers.add_parser("start", help="start MagicMirror; works with pm2 and docker-compose")
        subparsers.add_parser("stop", help="stop MagicMirror; works with pm2 and docker-compose")
        subparsers.add_parser("restart", help="restart MagicMirror; works with pm2 and docker-compose")

        for command in ("install", "remove"):
            parser = subparsers.add_parser(
                command,
                help=f"{command.capitalize()} MagicMirror",
                usage=f"{self.app_name} {self.name} {command} [--yes]",
            )

            parser.add_argument(
                "-y",
                "--yes",
                action="store_true",
                help="assume yes for user response and do not show prompt",
                dest="assume_yes",
            )

    def exec(self, args, extra):
        if extra:
            logger.error(f"Extra arguments are not accepted. See '{self.app_name} {self.name} --help'")
        elif args.command == "install":
            if args.assume_yes or confirm("Are you sure you want to install MagicMirror?"):
                self.magicmirror.install()
        elif args.command == "remove":
            if args.assume_yes or confirm("Are you sure you want to remove MagicMirror?"):
                self.magicmirror.remove()
        elif args.command == "status":
            self.controller.status()
        elif args.command == "hide":
            self.controller.hide(args.keys)
        elif args.command == "show":
            self.controller.show(args.keys)
        elif args.command in {"start", "stop", "restart"}:
            if self.env.MMPM_IS_DOCKER_IMAGE.get():
                logger.fatal("Cannot execute this command within a docker image")
            else:
                getattr(self.controller, args.command)()
        else:
            logger.error(f"No arguments provided. See '{self.app_name} {self.name} --help'")
