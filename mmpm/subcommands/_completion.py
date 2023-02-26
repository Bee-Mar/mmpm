#!/usr/bin/env python3
import argparse

def setup(subparser):
    # VERSION SUBCOMMANDS
    completion_parser = subparser.add_parser(
        "completion",
        usage='\n  mmpm completion',
        help='install autocompletion for the MMPM CLI',
    )

    completion_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes'
    )

