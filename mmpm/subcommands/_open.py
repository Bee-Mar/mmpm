#!/usr/bin/env python3
import argparse

def setup(subparser):
    # OPEN SUBCOMMANDS
    open_parser = subparser.add_parser(
        "open",
        usage='\n  mmpm open [--config] [--css] [--gui] [--mm-wiki] [--mmpm-wiki]',
        help='quickly open config files, documentation, wikis, and MagicMirror itself'
    )

    open_parser.add_argument(
        '--config',
        action='store_true',
        help='open MagicMirror config/config.js file in your $EDITOR',
        dest='config'
    )

    open_parser.add_argument(
        '--css',
        action='store_true',
        help='open MagicMirror css/custom.css file (if it exists) in your $EDITOR',
        dest='custom_css'
    )

    open_parser.add_argument(
        '--gui',
        action='store_true',
        help='open the MMPM GUI in your default browser',
        dest='gui'
    )

    open_parser.add_argument(
        '--magicmirror',
        action='store_true',
        help='open MagicMirror in your default browser (uses the MMPM_MAGICMIRROR_URI address)',
        dest='magicmirror'
    )

    open_parser.add_argument(
        '--mm-wiki',
        action='store_true',
        help='open the MagicMirror GitHub wiki in your default browser',
        dest='mm_wiki'
    )

    open_parser.add_argument(
        '--mm-docs',
        action='store_true',
        help='open the MagicMirror documentation in your default browser',
        dest='mm_docs'
    )

    open_parser.add_argument(
        '--mmpm-wiki',
        action='store_true',
        help='open the MMPM GitHub wiki in your default browser',
        dest='mmpm_wiki'
    )

    open_parser.add_argument(
        '--env',
        action='store_true',
        help='open the MMPM run-time environment variables JSON configuration file in your $EDITOR',
        dest='mmpm_env'
    )
