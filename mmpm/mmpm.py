#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
from mmpm import utils, colors, core, opts

__version__ = 0.99


def main(argv):
    ''' Main entry point for CLI '''

    args: object = opts.get_user_args()

    if args.version:
        print(colors.B_CYAN + "MMPM Version: " + colors.B_WHITE + "{}".format(__version__))
        sys.exit(0)

    modules, curr_snap, next_snap, checked_enhancements = core.load_modules(args.force_refresh)

    if not modules:
        utils.error_msg('Fatal. No modules found.')
        sys.exit(1)

    if args.all:
        core.display_modules(modules)

    elif args.categories:
        core.display_modules(modules, list_categories=True)

    elif args.search:
        core.display_modules(core.search_modules(modules, args.search))

    elif args.install:
        core.install_modules(modules, args.install)

    elif args.install_magicmirror:
        core.install_magicmirror()

    elif args.remove and args.ext_module_src:
        core.remove_external_module_source(args.remove)

    elif args.remove and not args.ext_module_src:
        core.remove_modules(modules, args.remove)

    elif args.list_installed:
        installed_modules = core.get_installed_modules(modules)

        if not installed_modules:
            utils.error_msg("No modules are currently installed")
            sys.exit(1)

        core.display_modules(installed_modules)

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

    elif args.magicmirror_config:
        core.edit_magicmirror_config()


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        utils.error_msg("Caught keyboard interrupt. Exiting")
