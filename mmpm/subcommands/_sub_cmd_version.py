#!/usr/bin/env python3
""" Command line options for 'version' subcommand """
from argparse import _SubParsersAction

def setup(subparser: _SubParsersAction):
    subparser.add_parser(
            "version",
            usage='\n  mmpm version',
            help='display MMPM version number',
            )
