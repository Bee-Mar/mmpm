#!/usr/bin/env python3
""" Command line options for 'update' subcommand """
import argparse

def setup(subparser: argparse._SubParsersAction):
    subparser.add_parser(
        "update",
        usage='\n  mmpm update',
        help='check for updates for installed packages, MMPM, and MagicMirror'
    )

