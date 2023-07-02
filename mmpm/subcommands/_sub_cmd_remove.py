#!/usr/bin/env python3
""" Command line options for 'remove' subcommand """
from argparse import _SubParsersAction

def setup(subparser: _SubParsersAction):
    parser = subparser.add_parser(
            "remove",
            usage='\n  mmpm remove <package(s)> [--yes]',
            help='remove locally installed packages'
            )

    parser.add_argument(
            '--magicmirror',
            action='store_true',
            default=False,
            help='install MagicMirror, if not already installed',
            dest='magicmirror'
            )

    parser.add_argument(
            '-y',
            '--yes',
            action='store_true',
            default=False,
            help='assume yes for user response and do not show prompt',
            dest='assume_yes'
            )

    parser.add_argument(
            '--gui',
            action='store_true',
            default=False,
            help='remove the MMPM GUI. Asks for sudo permissions',
            dest='gui'
            )
