#!/usr/bin/env python3
""" Command line options for 'list' subcommand """
import argparse

def setup(subparser):
   # LIST SUBCOMMANDS
    parser = subparser.add_parser(
        "list",
        usage='\n  mmpm list [-a] [-i] [-e] [-c] [-g] [--upgradable]',
        help='list items such as installed packages, packages available, available upgrades, etc'
    )

    # TODO: this is almost correct. --title-only shouldn't be allowed with --gui-url or --upgradable

    parser.add_argument(
        '-t',
        '--title-only',
        action='store_true',
        help='display the title only of packages (used with -c, -a, -e, or -i)',
        dest='title_only'
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='list all available packages in the marketplace',
        dest='all'
    )

    group.add_argument(
        '-i',
        '--installed',
        action='store_true',
        help='list all locally installed packages',
        dest='installed'
    )

    group.add_argument(
        '-e',
        '--exclude-installed',
        action='store_true',
        help='list all available packages in the marketplace, excluding locally installed packages',
        dest='exclude_installed'
    )

    group.add_argument(
        '-c',
        '--categories',
        action='store_true',
        help='list all available package categories',
        dest='categories'
    )

    group.add_argument(
        '-g',
        '--gui-url',
        action='store_true',
        help='list the URL of the MMPM GUI',
        dest='gui_url'
    )

    group.add_argument(
        '--upgradable',
        action='store_true',
        help='list packages that have available upgrades',
        dest='upgradable'
    )

