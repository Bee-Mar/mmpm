#!/usr/bin/env python3
import argparse
from sys import argv


def get_user_args():
    arg_parser = argparse.ArgumentParser(prog='mmpm',
                                         epilog='Detailed usage found at https://github.com/Bee-Mar/mmpm',
                                         description='''
                                                    The MagicMirror Package
                                                    Manager is a CLI designed
                                                    to simplify the
                                                    installation, removal, and
                                                    maintenance of MagicMirror
                                                    modules.
                                                    '''
                                        )

    arg_parser.add_argument('-u',
                            '--update',
                            action='store_true',
                            help='''
                                Check for updates for each of the currently
                                installed modules.
                                '''
                            )

    arg_parser.add_argument('-U',
                            '--upgrade',
                            action='append',
                            nargs='*',
                            help='''
                                 Upgrades currently installed modules. If no
                                 module name is supplied, all modules will be
                                 upgraded. To upgrade specific modules, supply
                                 one or more module name, space delimited.
                                 '''
                            )

    arg_parser.add_argument('-e',
                            '--enhance-mmpm',
                            action='store_true',
                            help='''
                                Checks if enhancements are available for MMPM.
                                User will be prompted if an upgrade is
                                available.
                                '''
                            )

    arg_parser.add_argument('-a',
                            '--all',
                            action='store_true',
                            help='Lists all currently available modules.'
                            )

    arg_parser.add_argument('-f',
                            '--force-refresh',
                            action='store_true',
                            help='Forces a refresh of the modules snapshot.'
                            )

    arg_parser.add_argument('-c',
                            '--categories',
                            action='store_true',
                            help='Lists names of all module categories.'
                            )

    arg_parser.add_argument('-s',
                            '--search',
                            nargs=1,
                            help='''
                                List all modules whose information matches the
                                search term(s). Attempts to match the search
                                string to the category name, followed by
                                attempting to match substrings within the
                                title, description, or author. For any searches
                                containing more than one word, surround the
                                search in quotations. Searching for module
                                names is case-sensitive. When searches for
                                category names fail, the search automatically
                                becomes non-case-sensitive.
                                '''
                            )

    arg_parser.add_argument('-d',
                            '--snapshot-details',
                            action='store_true',
                            help='''
                                Display details about the most recent snapshot
                                of the MagicMirror 3rd Party Modules taken.
                                '''
                            )

    arg_parser.add_argument('-M',
                            '--magicmirror',
                            action='store_true',
                            help='''
                                Installs the most recent version of MagicMirror
                                based on instructions from the MagicMirror
                                GitHub repo. First, your system will be checked
                                for a an existing installation of MagicMirror,
                                and if one is found, it will check for updates.
                                Otherwise, it will perform a new installation.
                                '''
                            )

    arg_parser.add_argument('-i',
                            '--install',
                            nargs='+',
                            help='''
                                Installs module(s) with given name(s) separated
                                by spaces. Installation candidate names are
                                case-sensitive.
                                '''
                            )

    arg_parser.add_argument('-r',
                            '--remove',
                            nargs='+',
                            help='''
                                Removes module(s) with given name(s) separated
                                by spaces. Removal candidate names are
                                case-sensitive.
                                '''
                            )

    arg_parser.add_argument('-l',
                            '--list-installed',
                            action='store_true',
                            help='Lists all currently installed modules.'
                            )

    arg_parser.add_argument('-v',
                            '--version',
                            action='store_true',
                            help='Displays MMPM version.'
                            )

    if len(argv) < 2:
        arg_parser.print_help()
        exit(0)

    return arg_parser.parse_args()
