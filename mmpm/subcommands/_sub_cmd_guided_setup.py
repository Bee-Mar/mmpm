#!/usr/bin/env python3
""" Command line options for 'guided-setup' subcommand """
from argparse import _SubParsersAction

def setup(subparser: _SubParsersAction):
    subparser.add_parser(
        "guided-setup",
        usage='\n  mmpm guided-setup',
        help='run the guided setup/installation of the GUI, environment variables, and other features',
    )

