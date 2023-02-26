#!/usr/bin/env python3
import argparse
import argcomplete

def setup(subparser):
    # UPGRADE SUBCOMMANDS
    upgrade_parser = subparser.add_parser(
        "upgrade",
        usage='\n  mmpm upgrade [--yes]\n  mmpm upgrade <package(s)> <application(s)> [--yes]',
        help='upgrade packages, MMPM, and/or MagicMirror, if available'
    )

    upgrade_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes'
    )
