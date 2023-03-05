#!/usr/bin/env python3
""" Command line options for 'install' subcommand """
import argparse

def setup(subparser: argparse._SubParsersAction):
    parser = subparser.add_parser(
        "install",
        usage='\n  mmpm install <package(s)> [--yes]\n  mmpm install [--completion] [--gui]',
        help='install MagicMirror packages',
    )

    parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes',
    )
