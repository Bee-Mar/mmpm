#!/usr/bin/env python3
""" Command line options for 'completion' subcommand """
from argparse import _SubParsersAction

def setup(subparser: _SubParsersAction):
    parser = subparser.add_parser(
            "completion",
            usage='\n  mmpm completion',
            help='install autocompletion for the MMPM CLI',
            )

    parser.add_argument(
            '-y',
            '--yes',
            action='store_true',
            default=False,
            help='assume yes for user response and do not show prompt',
            dest='assume_yes'
            )

