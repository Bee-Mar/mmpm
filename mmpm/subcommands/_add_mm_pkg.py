#!/usr/bin/env python3
""" Command line options for 'add-mm-pkg' subcommand """
import argparse


def setup(subparser: argparse._SubParsersAction):
    parser = subparser.add_parser(
        "add-mm-pkg",
        usage='\n  mmpm add-mm-package [--title=<title>] [--author=<author>] [--repo=<repo>] [--desc=<description>]\n  mmpm add-ext-package --remove <package> [--yes]',
        help='manually add MagicMirror packages to your local database'
    )

    parser.add_argument(
        '-t',
        '--title',
        type=str,
        help='title of MagicMirror package (will be prompted if not provided)',
        dest='title'
    )

    parser.add_argument(
        '-a',
        '--author',
        type=str,
        help='author of MagicMirror package (will be prompted if not provided)',
        dest='author'
    )

    parser.add_argument(
        '-r',
        '--repo',
        type=str,
        help='repo URL of MagicMirror package (will be prompted if not provided)',
        dest='repo'
    )

    parser.add_argument(
        '-d',
        '--desc',
        type=str,
        help='description of MagicMirror package (will be prompted if not provided)',
        dest='desc'
    )

    parser.add_argument(
        '--remove',
        nargs='+',
        help='remove MagicMirror package (similar to `add-apt-repository` --remove)',
        dest='remove'
    )

    parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt (used with --remove)',
        dest='assume_yes'
    )
