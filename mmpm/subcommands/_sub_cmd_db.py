#!/usr/bin/env python3
""" Command line options for 'db' subcommand """
import argparse

def setup(subparser: argparse._SubParsersAction):
    database_parser = subparser.add_parser(
        "db",
        usage='\n  mmpm db [--refresh] [--details]',
        help='refresh or display basic details about the database'
    )

    database_parser.add_argument(
        '-r',
        '--refresh',
        action='store_true',
        help='forces a refresh of the packages database',
        dest='refresh'
    )

    database_parser.add_argument(
        '-d',
        '--details',
        action='store_true',
        help='display details about the most recent MagicMirror packages database',
        dest='details'
    )

    database_parser.add_argument(
        '--dump',
        action='store_true',
        help='dump the database JSON contents to stdout',
        dest='dump'
    )
