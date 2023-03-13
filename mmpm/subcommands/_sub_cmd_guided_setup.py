#!/usr/bin/env python3
""" Command line options for 'guided-setup' subcommand """
import argparse

def setup(subparser: argparse._SubParsersAction):
    parser = subparser.add_parser(
        "guided-setup",
        usage='\n  mmpm guided-setup',
        help='run the guided setup/installation of the GUI, environment variables, and other features',
    )

