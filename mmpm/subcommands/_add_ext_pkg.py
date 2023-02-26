#!/usr/bin/env python3
import argparse

def setup(subparser):
    # ADD EXTERNAL PACKAGE SUBCOMMANDS
    add_ext_package_parser = subparser.add_parser(
        "add-ext-pkg",
        usage='\n  mmpm add-ext-package [--title=<title>] [--author=<author>] [--repo=<repo>] [--desc=<description>]\n  mmpm add-ext-package --remove <package> [--yes]',
        help='manually add MagicMirror packages to your local database'
    )

    add_ext_package_parser.add_argument(
        '-t',
        '--title',
        type=str,
        help='title of external package (will be prompted if not provided)',
        dest='title'
    )

    add_ext_package_parser.add_argument(
        '-a',
        '--author',
        type=str,
        help='author of external package (will be prompted if not provided)',
        dest='author'
    )

    add_ext_package_parser.add_argument(
        '-r',
        '--repo',
        type=str,
        help='repo URL of external package (will be prompted if not provided)',
        dest='repo'
    )

    add_ext_package_parser.add_argument(
        '-d',
        '--desc',
        type=str,
        help='description of external package (will be prompted if not provided)',
        dest='desc'
    )

    add_ext_package_parser.add_argument(
        '--remove',
        nargs='+',
        help='remove external package (similar to `add-apt-repository` --remove)',
        dest='remove'
    )

    add_ext_package_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt (used with --remove)',
        dest='assume_yes'
    )
