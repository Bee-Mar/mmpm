#!/usr/bin/env python3
""" Command line options for 'env' subcommand """
import argparse

def setup(subparser):
    subparser.add_parser(
        "env",
        usage='\n  mmpm env',
        help='display the MMPM environment variables and their value(s)'
    )
