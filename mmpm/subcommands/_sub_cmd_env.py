#!/usr/bin/env python3
""" Command line options for 'env' subcommand """
from argparse import _SubParsersAction

def setup(subparser: _SubParsersAction):
    subparser.add_parser(
            "env",
            usage='\n  mmpm env',
            help='display the MMPM environment variables and their value(s)'
            )
