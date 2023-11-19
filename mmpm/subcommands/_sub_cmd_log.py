#!/usr/bin/env python3
""" Command line options for 'log' subcommand """
from mmpm.logger import MMPMLogger
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)

class Log(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "log"
        self.help = f"display, tail, or zip the {self.name} log files"
        self.usage = f"{self.app_name} {self.name} [--cli] [--gui] [--tail] [--zip]"

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

    def exec(self, args, extra):
        if extra:
            logger.msg.extra_args(args.subcmd)
        elif args.zip:
            MMPMLogger.zip()
        elif not args.cli and not args.gui:
            # if the user doesn't provide arguments, just display everything, but consider the --tail arg
            MMPMLogger.display(cli_logs=True, gui_logs=True, tail=args.tail)
        else:
            MMPMLogger.display(args.cli, args.gui, args.tail)

