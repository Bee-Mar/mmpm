#!/usr/bin/env python3
import argparse

def setup(subparser):
    # LOGS SUBCOMMANDS
    log_parser = subparser.add_parser(
        "log",
        usage='\n  mmpm log [--cli] [--web] [--tail]',
        help='display, tail, or zip the MMPM log files'
    )

    log_parser.add_argument(
        '-c',
        '--cli',
        action='store_true',
        help='cat the MMPM CLI log files',
        dest='cli'
    )

    log_parser.add_argument(
        '-g',
        '--gui',
        action='store_true',
        help='cat the MMPM GUI (Gunicorn) log files',
        dest='gui'
    )

    log_parser.add_argument(
        '-t',
        '--tail',
        action='store_true',
        help='tail the log file(s) in real time',
        dest='tail'
    )

    log_parser.add_argument(
        '--zip',
        action='store_true',
        help='compress the MMPM log file(s), and save them in your current directory',
        dest='zip'
    )

