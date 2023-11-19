#!/usr/bin/env python3
""" Command line options for 'env' subcommand """
from mmpm.env import MMPMEnv
from mmpm.logger import MMPMLogger
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogger.get_logger(__name__)


class Env(SubCmd):
    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "env"
        self.help = f"Display the {self.name} environment variables and their value(s)"
        self.usage = f"{self.app_name} {self.name}"
        self.env = MMPMEnv()

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

    def exec(self, args, extra):
        if extra:
            logger.msg.extra_args(args.subcmd)
            return

        self.env.display()
        print("Run `mmpm open --env` to edit the variable values")
