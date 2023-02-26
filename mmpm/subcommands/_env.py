#!/usr/bin/env python3
import argparse

def setup(subparser):
    # ENV SUBCOMMANDS
    subparser.add_parser(
        "env",
        usage='\n  mmpm env',
        help='display the MMPM environment variables and their value(s)'
    )
