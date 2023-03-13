#!/usr/bin/env python3
""" Command line options for 'version' subcommand """
import argparse

def setup(subparser: argparse._SubParsersAction):
     subparser.add_parser(
        "version",
        usage='\n  mmpm version',
        help='display MMPM version number',
    )
