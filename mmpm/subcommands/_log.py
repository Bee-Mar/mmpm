#!/usr/bin/env python3
""" Command line options for 'log' subcommand """
import argparse

def setup(subparser: argparse._SubParsersAction):
    parser = subparser.add_parser(
        "log",
        usage='\n  mmpm log [--cli] [--web] [--tail]',
        help='display, tail, or zip the MMPM log files'
    )

    parser.add_argument(
        '-c',
        '--cli',
        action='store_true',
        help='cat the MMPM CLI log files',
        dest='cli'
    )

    parser.add_argument(
        '-g',
        '--gui',
        action='store_true',
        help='cat the MMPM GUI (Gunicorn) log files',
        dest='gui'
    )

    parser.add_argument(
        '-t',
        '--tail',
        action='store_true',
        help='tail the log file(s) in real time',
        dest='tail'
    )

    parser.add_argument(
        '--zip',
        action='store_true',
        help='compress the MMPM log file(s), and save them in your current directory',
        dest='zip'
    )

