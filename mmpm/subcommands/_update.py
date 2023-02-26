#!/usr/bin/env python3
import argparse

def setup(subparser):
    # UPDATE PARSER
    subparser.add_parser(
        "update",
        usage='\n  mmpm update',
        help='check for updates for installed packages, MMPM, and MagicMirror'
    )

