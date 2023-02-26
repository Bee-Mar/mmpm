#!/usr/bin/env python3
import argparse

def setup(subparser):
    parser = subparser.add_parser(
        "guided-setup",
        usage='\n  mmpm guided-setup',
        help='run the guided setup/installation of the GUI, environment variables, and other features',
    )

