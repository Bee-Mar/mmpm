#!/usr/bin/env python3
""" Command line options for 'list' subcommand """
import argparse

def setup(subparser):
   # LIST SUBCOMMANDS
    parser = subparser.add_parser(
        "list",
        usage='\n  mmpm list [--all] [--exclude-local] [--categories] [--gui-url]',
        help='list items such as installed packages, packages available, available upgrades, etc'
    )

    parser.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='list all available packages in the marketplace',
        dest='all'
    )

    parser.add_argument(
        '-e',
        '--exclude-installed',
        action='store_true',
        help='list all available packages in the marketplace, excluding locally installed packages',
        dest='exclude_installed'
    )

    parser.add_argument(
        '-i',
        '--installed',
        action='store_true',
        help='list all locally installed packages',
        dest='installed'
    )

    parser.add_argument(
        '-c',
        '--categories',
        action='store_true',
        help='list all available package categories',
        dest='categories'
    )

    parser.add_argument(
        '-t',
        '--title-only',
        action='store_true',
        help='display the title only of packages (used with -c, -a, -e, or -i)',
        dest='title_only'
    )

    parser.add_argument(
        '-g',
        '--gui-url',
        action='store_true',
        help='list the URL of the MMPM GUI',
        dest='gui_url'
    )

    parser.add_argument(
        '--upgradable',
        action='store_true',
        help='list packages that have available upgrades',
        dest='upgradable'
    )
