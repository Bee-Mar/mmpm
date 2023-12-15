#!/usr/bin/env python3
""" Command line options for 'log' subcommand """

from mmpm.log.logger import MMPMLogger
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)


class Logs(SubCmd):
    """
    The 'Logs' subcommand allows users to view all or specific log files and create an archive of them

    Custom Attributes:
        None
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "logs"
        self.help = f"Display, tail, or zip the {self.app_name} log files"
        self.usage = f"{self.app_name} {self.name} [--<option(s)>]"

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-t",
            "--tail",
            action="store_true",
            help=f"Tail {self.app_name} log file(s)",
            dest="tail",
        )

        self.parser.add_argument(
            "-c",
            "--cli",
            action="store_true",
            help=f"Display {self.app_name} CLI log file(s)",
            dest="cli",
        )

        self.parser.add_argument(
            "-u",
            "--ui",
            action="store_true",
            help=f"Display {self.app_name} UI log file(s)",
            dest="ui",
        )

        self.parser.add_argument(
            "-z",
            "--zip",
            action="store_true",
            help=f"Zip {self.app_name} CLI and/or UI log file(s)",
            dest="zip",
        )

    def exec(self, args, extra):
        if extra:
            logger.error(f"Extra arguments are not accepted. See '{self.app_name} {self.name} --help'")
        elif args.zip:
            MMPMLogger.zip()
        elif not args.cli and not args.ui:
            # if the user doesn't provide arguments, just display everything, but consider the --tail arg
            MMPMLogger.display(cli_logs=True, ui_logs=True, tail=args.tail)
        else:
            MMPMLogger.display(args.cli, args.ui, args.tail)
