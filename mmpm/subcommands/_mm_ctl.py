#!/usr/bin/env python3
""" Command line options for 'mm-ctl' subcommand """
import argparse

def setup(subparser: argparse._SubParsersAction):
    parser = subparser.add_parser(
        "mm-ctl",
        usage='\n  mmpm mm-ctl [status] [restart] [start] [--stop]\n  mmpm mm-ctl [--rotate] {0, 90, 180, 270}\n  mmpm mm-ctl [--hide] [--show] <key(s)>',
        help='commands to control the MagicMirror'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='show the hidden/visible status and key(s) of module(s) on your MagicMirror',
        dest='status'
    )

    parser.add_argument(
        '--hide',
        nargs='+',
        help='hide module(s) on your MagicMirror via provided key(s)',
        dest='hide'
    )

    parser.add_argument(
        '--show',
        nargs='+',
        help='show module(s) on your MagicMirror via provided key(s)',
        dest='show'
    )

    parser.add_argument(
        '--start',
        action='store_true',
        help='start MagicMirror; works with pm2 and docker-compose',
        dest='start'
    )

    parser.add_argument(
        '--stop',
        action='store_true',
        help='stop MagicMirror; works with pm2 and docker-compose',
        dest='stop'
    )

    parser.add_argument(
        '--restart',
        action='store_true',
        help='restart MagicMirror; works with pm2 and docker-compose',
        dest='restart'
    )

