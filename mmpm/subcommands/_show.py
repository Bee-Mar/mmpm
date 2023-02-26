#!/usr/bin/env python3
import argparse

def setup(subparser):
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


