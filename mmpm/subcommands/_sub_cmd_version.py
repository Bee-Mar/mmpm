#!/usr/bin/env python3
""" Command line options for 'version' subcommand """

from mmpm.__version__ import version
from mmpm.log.factory import MMPMLogFactory
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogFactory.get_logger(__name__)


class Version(SubCmd):
    """
    The 'Version' subcommand displays the current version number of MMPM

    Custom Attributes:
        None
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "version"
        self.help = f"Display {self.app_name} application version"
        self.usage = f"{self.app_name} {self.name}"

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

    def exec(self, args, extra):
        if extra:
            logger.error(f"{self.name} does not take arguments")
        else:
            print(version)
