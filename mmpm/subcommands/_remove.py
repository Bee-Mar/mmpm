#!/usr/bin/env python3
import argparse

def setup(subparser):
    # REMOVE PARSER
    remove_parser = subparser.add_parser(
        "remove",
        usage='\n  mmpm remove <package(s)> [--yes]',
        help='remove locally installed packages'
    )

    remove_parser.add_argument(
        '--magicmirror',
        action='store_true',
        default=False,
        help='install MagicMirror, if not already installed',
        dest='magicmirror'
    )

    remove_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes'
    )

    remove_parser.add_argument(
        '--gui',
        action='store_true',
        default=False,
        help='remove the MMPM GUI. Asks for sudo permissions',
        dest='gui'
    )
