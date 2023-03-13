#!/usr/bin/env python3
""" Command line options for 'completion' subcommand """
import argparse

def setup(subparser: argparse._SubParsersAction):
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

