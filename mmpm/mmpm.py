#!/usr/bin/env python3

import sys
import argparse
from mmpm import utils, colors, core

__version__ = 0.36

def main(argv):
    arg_parser = argparse.ArgumentParser(prog="mmpm",
                                         epilog='''
                                                Detailed usage found at
                                                https://github.com/Bee-Mar/mmpm
                                                ''',
                                         description='''
                                                    The MagicMirror Package
                                                    Manager is a CLI designed
                                                    to simplify the
                                                    installation, removal, and
                                                    maintenance of MagicMirror
                                                    modules.
                                                    ''')

    arg_parser.add_argument("-u",
                            "--update",
                            action="store_true",
                            help='''
                                Check for updates for each of the currently
                                installed modules.
                                ''')

    arg_parser.add_argument("-U",
                            "--upgrade",
                            action="append",
                            nargs="*",
                            help='''
                                 Upgrades currently installed modules. If no
                                 module name is supplied, all modules will be
                                 upgraded. To upgrade specific modules, supply
                                 one or more module name, space delimited.
                                 ''')

    arg_parser.add_argument("-e",
                            "--enhance-mmpm",
                            action="store_true",
                            help='''
                                Checks if enhancements are available for MMPM.
                                User will be prompted if an upgrade is
                                available.
                                ''')

    arg_parser.add_argument("-a",
                            "--all",
                            action="store_true",
                            help="Lists all currently available modules.")

    arg_parser.add_argument("-f",
                            "--force-refresh",
                            action="store_true",
                            help='''
                                Forces a refresh of the modules database
                                snapshot.
                                ''')

    arg_parser.add_argument("-c",
                            "--categories",
                            action="store_true",
                            help='''
                                Lists names of all module categories, ie.
                                Finance, Weather, etc.
                                ''')

    arg_parser.add_argument("-s",
                            "--search",
                            nargs=1,
                            help='''
                                Lists all modules whose information contains
                                the matching string as a category name or
                                substring of the title, author, or description.
                                First, attempts to match the string to the
                                category name is made. If the search fails,
                                attempts to match substrings in the title,
                                description, or author are made. For any
                                searches containing more than one word,
                                surround the search in quotations.
                                Additionally, when searching for modules based
                                on category names, the query is case-sensitive.
                                When searches do not match category names for
                                the query, the search automatically becomes
                                non-case-sensitive. When searching for a
                                category with a lengthy name, it is best to
                                copy and paste the exact name from the results
                                produced by 'mmpm -c' (or the equivalent 'mmpm
                                    --categories'), and surround the name in
                                quotations.
                                ''')

    arg_parser.add_argument("-d",
                            "--snapshot-details",
                            action="store_true",
                            help='''
                                Display details about the most recent snapshot
                                of the MagicMirror 3rd Party Modules taken.
                                '''
                            )

    arg_parser.add_argument("-M",
                            "--magicmirror",
                            action="store_true",
                            help='''
                                Installs the most recent version of MagicMirror
                                based on instructions from the MagicMirror
                                GitHub repo. First, your system will be checked
                                for a an existing installation of MagicMirror,
                                and if one is found, it will check for updates.
                                Otherwise, it will perform a new installation.
                                '''
                            )

    arg_parser.add_argument("-i",
                            "--install",
                            nargs="+",
                            help='''
                                Installs module(s) with given name(s) separated
                                by spaces. Installation candidate names are
                                case-sensitive.
                                '''
                            )

    arg_parser.add_argument("-r",
                            "--remove",
                            nargs="+",
                            help='''
                                Removes module(s) with given name(s) separated
                                by spaces. Removal candidate names are
                                case-sensitive.
                                '''
                            )

    arg_parser.add_argument("-l",
                            "--list-installed",
                            action="store_true",
                            help='''
                                Lists all currently installed modules.
                                '''
                            )

    arg_parser.add_argument("-v",
                            "--version",
                            action="store_true",
                            help='''
                                Displays MMPM version.
                                '''
                            )

    if len(argv) < 2:
        arg_parser.print_help()
        exit(0)

    args = arg_parser.parse_args()

    modules_table = {}

    snapshot_file = utils.HOME_DIR + "/.magic_mirror_modules_snapshot.json"

    modules_table, curr_snap, next_snap, checked_enhancements = core.load_modules(snapshot_file, args.force_refresh)

    if args.all:
        core.display_modules(modules_table, list_all=True, list_categories=False)

    elif args.categories:
        core.display_modules(modules_table, list_all=False, list_categories=True)

    elif args.search:
        core.display_modules(core.search_modules(modules_table, args.search), list_all=True, list_categories=False)

    elif args.install:
        core.install_modules(modules_table, args.install)

    elif args.magicmirror:
        core.install_magicmirror()

    elif args.remove:
        installed_modules = core.get_installed_modules(modules_table)
        core.remove_modules(installed_modules, args.remove)

    elif args.list_installed:
        installed_modules = core.get_installed_modules(modules_table)

        if not installed_modules:
            utils.error_msg("No modules are currently installed")

        print(colors.BRIGHT_CYAN + "Module(s) Installed:\n" + colors.NORMAL_WHITE)

        for module in installed_modules:
            print(module)

    elif args.snapshot_details or args.force_refresh:
        core.snapshot_details(modules_table, curr_snap, next_snap)

    elif args.update:
        core.enhance_modules(modules_table, update=True, upgrade=False, modules_to_upgrade=None)

    elif args.upgrade:
        core.enhance_modules(modules_table, update=False, upgrade=True, modules_to_upgrade=args.upgrade[0])

    elif args.enhance_mmpm and not checked_enhancements:
        core.check_for_mmpm_enhancements()

    elif args.version:
        print(colors.BRIGHT_CYAN + "MMPM Version: " + colors.BRIGHT_WHITE + "{}".format(__version__))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        utils.error_msg("Caught keyboard interrupt. Exiting")
