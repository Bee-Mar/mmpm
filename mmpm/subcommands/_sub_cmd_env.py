#!/usr/bin/env python3
""" Command line options for 'env' subcommand """
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogFactory.get_logger(__name__)


class Env(SubCmd):
    """
    The 'Env' subcommand allows users to view the current environment variables set for MMPM

    Custom Attributes:
        env (MMPMEnv): A singleton of MMPMEnv which contains environment variables
    """

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
            logger.error(f"Extra arguments are not accepted. See '{self.app_name} {self.name} --help'")
            return

        logger.debug("Printing user environment to stdout")
        self.env.display()
        MMPMLogFactory.shutdown()
