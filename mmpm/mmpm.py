#!/usr/bin/env python3
import sys
from mmpm import utils, colors, core, opts

__version__ = 0.50


def main(argv):
    ''' Main entry point for CLI '''

    args = opts.get_user_args()

    if args.version:
        print(colors.B_CYAN + "MMPM Version: " + colors.B_WHITE + f"{__version__}")
        exit(0)

    modules, curr_snap, next_snap, checked_enhancements = core.load_modules(args.force_refresh)

    if args.all:
        core.display_modules(modules, list_all=True)

    elif args.categories:
        core.display_modules(modules, list_categories=True)

    elif args.search:
        core.display_modules(core.search_modules(modules, args.search), list_all=True)

    elif args.install:
        core.install_modules(modules, args.install)

    elif args.magicmirror:
        core.install_magicmirror()

    elif args.remove:
        core.remove_modules(core.get_installed_modules(modules), args.remove)

    elif args.list_installed:
        installed_modules = core.get_installed_modules(modules)

        if not installed_modules:
            utils.error_msg("No modules are currently installed")

        print(colors.B_CYAN + "Module(s) Installed:\n" + colors.RESET)

        for module in installed_modules:
            print(module)

    elif args.snapshot_details or args.force_refresh:
        core.snapshot_details(modules, curr_snap, next_snap)

    elif args.update:
        core.enhance_modules(modules, update=True)

    elif args.upgrade:
        core.enhance_modules(modules, upgrade=True, modules_to_upgrade=args.upgrade[0])

    elif args.enhance_mmpm and not checked_enhancements:
        core.check_for_mmpm_enhancements()

    elif args.add_ext_module_src:
        core.add_external_module_source()


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        utils.error_msg("Caught keyboard interrupt. Exiting")
