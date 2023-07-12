#!/usr/bin/env python3
""" Command line options for 'db' subcommand """
from argparse import _SubParsersAction

def setup(subparser: _SubParsersAction):
    parser = subparser.add_parser(
        "db",
        usage='\n  mmpm db [--refresh] [--details]',
        help='refresh or display basic details about the database'
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '-r',
        '--refresh',
        action='store_true',
        help='forces a refresh of the packages database',
        dest='refresh',
    )

    group.add_argument(
        '-i',
        '--info',
        action='store_true',
        help='display information about the MagicMirror packages database',
        dest='info',
    )

    group.add_argument(
        '-d',
        '--dump',
        action='store_true',
        help='dump the database contents to stdout as JSON',
        dest='dump',
    )
