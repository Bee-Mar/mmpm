#!/usr/bin/env python3
import sys
from mmpm import utils, colors, core, opts

__version__ = 0.39


def main(argv):
    ''' Main entry point for CLI '''

    args = opts.get_user_args()

    modules_table = {}

    snapshot_file = utils.HOME_DIR + "/.magic_mirror_modules_snapshot.json"

    modules_table, curr_snap, next_snap, checked_enhancements = core.load_modules(
        snapshot_file, args.force_refresh)

    if args.all:
        core.display_modules(modules_table, list_all=True)

    elif args.categories:
        core.display_modules(modules_table, list_categories=True)

    elif args.search:
        core.display_modules(core.search_modules(
            modules_table, args.search), list_all=True)

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

        print(colors.B_CYAN + "Module(s) Installed:\n" + colors.N_WHITE)

        for module in installed_modules:
            print(module)

    elif args.snapshot_details or args.force_refresh:
        core.snapshot_details(modules_table, curr_snap, next_snap)

    elif args.update:
        core.enhance_modules(modules_table, update=True)

    elif args.upgrade:
        core.enhance_modules(modules_table,
                             upgrade=True,
                             modules_to_upgrade=args.upgrade[0])

    elif args.enhance_mmpm and not checked_enhancements:
        core.check_for_mmpm_enhancements()

    elif args.version:
        print(colors.B_CYAN + "MMPM Version: " + colors.B_WHITE + f"{__version__}")


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        utils.error_msg("Caught keyboard interrupt. Exiting")
