#!/usr/bin/env python3
""" Command line options for 'open' subcommand """
import argparse

def setup(subparser: argparse._SubParsersAction):
    parser = subparser.add_parser(
        "open",
        usage='\n  mmpm open [--config] [--css] [--gui] [--magicmirro] [--mm-wiki] [--mm-docs] [--mmpm-wiki] [--env]',
        help='quickly open config files, documentation, wikis, and MagicMirror itself'
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '--config',
        action='store_true',
        help='open MagicMirror config/config.js file in your $EDITOR',
        dest='config'
    )

    group.add_argument(
        '--css',
        action='store_true',
        help='open MagicMirror css/custom.css file (if it exists) in your $EDITOR',
        dest='custom_css'
    )

    group.add_argument(
        '--gui',
        action='store_true',
        help='open the MMPM GUI in your default browser',
        dest='gui'
    )

    group.add_argument(
        '--magicmirror',
        action='store_true',
        help='open MagicMirror in your default browser (uses the MMPM_MAGICMIRROR_URI address)',
        dest='magicmirror'
    )

    group.add_argument(
        '--mm-wiki',
        action='store_true',
        help='open the MagicMirror GitHub wiki in your default browser',
        dest='mm_wiki'
    )

    group.add_argument(
        '--mm-docs',
        action='store_true',
        help='open the MagicMirror documentation in your default browser',
        dest='mm_docs'
    )

    group.add_argument(
        '--mmpm-wiki',
        action='store_true',
        help='open the MMPM GitHub wiki in your default browser',
        dest='mmpm_wiki'
    )

    group.add_argument(
        '--env',
        action='store_true',
        help='open the MMPM run-time environment variables JSON configuration file in your $EDITOR',
        dest='mmpm_env'
    )
