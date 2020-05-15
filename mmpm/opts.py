#!/usr/bin/env python3
# pylint: disable=unused-argument
import argparse
import sys
from mmpm.utils import MMPM_WIKI_URL


def get_user_args() -> object:
    '''
    Wrapper method around ArgumentParser.parse_args()

    Parameters:
        None

    Returns:
        ArgumentParser objects
    '''

    arg_parser = argparse.ArgumentParser(
        prog='mmpm',
        epilog=f'More details at {MMPM_WIKI_URL}',
        description='''
            The MagicMirror Package Manager is a CLI designed to simplify the
            installation, removal, and maintenance of MagicMirror modules.
            '''
    )

    arg_parser.add_argument(
        '-u',
        '--update',
        action='store_true',
        help='''
            Check for updates for each of the currently installed modules.
            '''
    )

    arg_parser.add_argument(
        '-U',
        '--upgrade',
        action='append',
        nargs='*',
        help='''
            Upgrade currently installed modules. If no module name is provided,
            all modules will be upgraded. To upgrade specific modules, supply
            one or more module name, space delimited.
            '''
    )

    arg_parser.add_argument(
        '-e',
        '--enhance-mmpm',
        action='store_true',
        help='''
            Checks if enhancements are available for MMPM.  User will be
            prompted if an upgrade is available.
            '''
    )

    arg_parser.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='Lists all currently available modules.'
    )

    arg_parser.add_argument(
        '-f',
        '--force-refresh',
        action='store_true',
        help='Forces a refresh of the modules snapshot.'
    )

    arg_parser.add_argument(
        '-c',
        '--categories',
        action='store_true',
        help='Lists names of all module categories.'
    )

    arg_parser.add_argument(
        '-s',
        '--search',
        nargs=1,
        help='''List all modules whose details match given search string'''
    )

    arg_parser.add_argument(
        '-d',
        '--snapshot-details',
        action='store_true',
        help='''
            Display details about the most recent snapshot of the MagicMirror
            3rd Party Modules taken.
            '''
    )

    arg_parser.add_argument(
        '-M',
        '--install-magicmirror',
        action='store_true',
        help='''Installs the most recent version of MagicMirror'''
    )

    arg_parser.add_argument(
        '-i',
        '--install',
        nargs='+',
        help='''
            Install module(s) with given case-sensitive name(s) separated by
            spaces
            '''
    )

    arg_parser.add_argument(
        '-r',
        '--remove',
        nargs='+',
        help='''
            Remove module(s) with given case-sensitive name(s) separated by
            spaces
            '''
    )

    arg_parser.add_argument(
        '-l',
        '--list-installed',
        action='store_true',
        help='List all currently installed modules'
    )

    arg_parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='Display MMPM version'
    )

    arg_parser.add_argument(
        '-X',
        '--add-ext-module',
        action='store_true',
        help='Register modules not found in the 3rd Party Wiki in the MMPM database'
    )

    arg_parser.add_argument(
        '-C',
        '--magicmirror-config',
        action='store_true',
        help='Open MagicMirror config file in your $EDITOR'
    )

    arg_parser.add_argument(
        '--ext-module',
        action='store_true',
        help='Used in conjuction with --remove to completely remove an external module source from your configuration'
    )

    arg_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='Assume yes for anything interactive'
    )

    arg_parser.add_argument(
        '--GUI',
        action='store_true',
        default=False,
        help=argparse.SUPPRESS
    )

    arg_parser.add_argument(
        '-A',
        '--active-modules',
        action='store_true',
        default=False,
        help="List the modules currently active/enabled in MagicMirror. This is based upon the modules 'disabled' status in the MagicMirror config"
    )

    arg_parser.add_argument(
        '-W',
        '--web-url',
        action='store_true',
        default=False,
        help='Display the URL of the MMPM web interface'
    )

    if len(sys.argv) < 2:
        arg_parser.print_help()
        sys.exit(0)

    return arg_parser.parse_args()
