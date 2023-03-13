#!/usr/bin/env python3
""" Command line options for 'upgrade' subcommand """
import argparse

def setup(subparser: argparse._SubParsersAction):
    parser = subparser.add_parser(
        "upgrade",
        usage='\n  mmpm upgrade [--yes]\n  mmpm upgrade <package(s)> <application(s)> [--yes]',
        help='upgrade packages, MMPM, and/or MagicMirror, if available'
    )

    parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes'
    )
