#!/usr/bin/env python3
""" Command line options for 'install' subcommand """
from argparse import _SubParsersAction

def setup(subparser: _SubParsersAction):
    parser = subparser.add_parser(
            "install",
            usage='\n  mmpm install <package(s)> [--yes]\n  mmpm install [--completion] [--gui]',
            help='install MagicMirror packages',
            )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
            '-y',
            '--yes',
            action='store_true',
            default=False,
            help='assume yes for user response and do not show prompt',
            dest='assume_yes',
            )
