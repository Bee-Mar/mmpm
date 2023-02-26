#!/usr/bin/env python3
import argparse

def setup(subparser):
    # VERSION SUBCOMMANDS
    subparser.add_parser(
        "version",
        usage='\n  mmpm version',
        help='display MMPM version number',
    )
