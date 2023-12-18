#!/usr/bin/env python3
from argparse import Namespace, _SubParsersAction
from typing import List

from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)


class SubCmd:
    """
    Base subcommand class used to define all future subcommands

    Args:
        app_name (str): The name of the application.
    Attributes:
        app_name (str): The name of the application.
        name (str): The name of the subcommand.
        help (str): A brief description of the subcommand's purpose.
        usage (str): The usage information for the subcommand.
        parser (argparse._SubParsersAction): the subparser options/commands are appended to
        [Method] register(self, subparser): see method docs
        [Method] exec(self, args, extra): see method docs
    """

    def __init__(self, app_name: str = ""):
        self.app_name = app_name
        self.name: str = ""
        self.help: str = ""
        self.usage: str = ""
        self.parser = None

        if not self.name or not self.help or not self.usage or not self.parser:
            message = "name, help, and usage must be defined"
            logger.critical(message)
            raise NameError(message)

    def register(self, subparser: _SubParsersAction) -> None:  # pylint: disable=unused-argument
        """
        Implementation is required. Configure all subcommand options here. This
        method is called at application startup to register the subcommand's
        options with the main parser object.

        Args:
            subparser: the subparser object provided by the main method to register this subcommand with

        Returns:
            None
        """

        message = "The register method must be implemented"
        logger.critical(message)
        raise NameError(message)

    def exec(self, args: Namespace, extra: List[str]) -> None:  # pylint: disable=unused-argument
        """
        Implementation is required. Self-contained logic of the subcommand (ie. the subcommand's 'main' method).

        Args:
            args: default & user-supplied responses to all configured options
            extra: arguments provided by the user which may or may not correspond to configured options

        Returns:
            None
        """

        message = "The exec method must be implemented"
        logger.critical(message)
        raise NameError(message)
