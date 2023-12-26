#!/usr/bin/env python3
""" Command line options for 'completion' subcommand """
from typing import Dict

from mmpm.log.factory import MMPMLogFactory
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogFactory.get_logger(__name__)


class Completion(SubCmd):
    """
    The 'Completion' subcommand generates the necessary commands a user should copy/paste into their
    shell configuration file to register autocompletion for MMPM.

    Custom Attributes:
        shells (Dict[str, str]): a dictionary of shell names and associated commands for autocompletion registration
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "completion"
        self.help = f"Generate commands to enable autocompletion for {self.app_name}"
        self.usage = f"{self.app_name} {self.name} --shell=[type]"

        self.shells: Dict[str, str] = {
            "bash": f'eval "$(register-python-argcomplete {self.app_name})"',
            "zsh": f'autoload -U bashcompinit\nbashcompinit\neval "$(register-python-argcomplete {self.app_name})"',
            "tcsh": f"`register-python-argcomplete --shell tcsh {self.app_name}`",
            "fish": f"register-python-argcomplete --shell fish {self.app_name}",
        }

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-s",
            "--shell",
            choices=self.shells.keys(),
            help="The shell type to generate completion commands for",
            dest="shell",
        )

    def exec(self, args, extra):
        """
        Adds autocompletion configuration to a user's shell configuration file.
        Detects configuration files for bash, zsh, fish, and tcsh

        Parameters:
            assume_yes (bool): if True, assume yes for user response, and do not display prompt

        Returns:
            None
        """

        if not args.shell or args.shell is None:
            logger.error(f"No shell type provided. See `{self.app_name} {self.name} --help`")
            return

        if args.shell not in self.shells:
            logger.error(f"Invalid shell type. See `{self.app_name} {self.name} --help`")
            return

        logger.debug(f"Outputting commands to enable cli completion for {args.shell}")

        print(f"# enables {self.app_name} tab-completion for subcommands")
        print(self.shells.get(args.shell))
