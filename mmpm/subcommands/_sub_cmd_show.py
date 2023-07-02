#!/usr/bin/env python3
""" Command line options for 'show' subcommand """
from argparse import _SubParsersAction

def setup(subparser: _SubParsersAction):
    show_parser = subparser.add_parser(
            "show",
            usage='\n  mmpm show <package(s)> [--verbose]',
            help='show details about one or more packages'
            )

    show_parser.add_argument(
            '-r',
            '--remote',
            action='store_true',
            help='display remote detail for package(s) from GitHub/GitLab/Bitbucket APIs',
            dest='remote'
            )


