#!/usr/bin/env python3
import argparse

def setup(subparser):
    parser = subparser.add_parser(
        "search",
        usage='\n  mmpm search <query> [--case-sensitive] [--exclude-installed]',
        help='search for MagicMirror packages'
    )

    parser.add_argument(
        '-t',
        '--title-only',
        action='store_true',
        help='only show the title of the packages matching the search results',
        dest='title_only'
    )

    parser.add_argument(
        '-c',
        '--case-sensitive',
        action='store_true',
        help='search for packages using a case-sensitive query',
        dest='case_sensitive'
    )

    parser.add_argument(
        '-e',
        '--exclude-installed',
        action='store_true',
        help='exclude installed packages from search results',
        dest='exclude_installed'
    )


