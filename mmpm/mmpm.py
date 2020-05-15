#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
from mmpm import utils, colors, core, opts

__version__ = 1.13


def main(argv):
    ''' Main entry point for CLI '''

    args: object = opts.get_user_args()

    if args.version:
        print(colors.B_CYAN + "MMPM Version: " + colors.B_WHITE + "{}".format(__version__))
        sys.exit(0)

    current_snapshot, next_snapshot = utils.calc_snapshot_timestamps()
    is_expired = utils.should_refresh_modules(current_snapshot, next_snapshot)

    if args.force_refresh:
        modules = core.load_modules(force_refresh=args.force_refresh)

    else:
        modules = core.load_modules(force_refresh=is_expired)

    if not modules:
        utils.error_msg('Fatal. No modules found.')
        sys.exit(1)

    if args.all:
        core.display_modules(modules)

    elif args.categories:
        core.display_modules(modules, list_categories=True)

    elif args.search:
        core.display_modules(core.search_modules(modules, args.search[0]))

    elif args.install:
        core.install_modules(modules, [utils.sanitize_name(module) for module in args.install])

    elif args.install_magicmirror:
        core.install_magicmirror(args.GUI)

    elif args.remove:
        if args.ext_module_src:
            core.remove_external_module_source([utils.sanitize_name(module) for module in args.remove])
        else:
            core.remove_modules(modules, [utils.sanitize_name(module) for module in args.remove])

    elif args.list_installed:
        installed_modules = core.get_installed_modules(modules)

        if not installed_modules:
            utils.error_msg("No modules are currently installed")
            sys.exit(1)

        core.display_modules(installed_modules)

    elif args.snapshot_details:
        core.snapshot_details(modules)

    elif args.update:
        core.enhance_modules(modules, update=True)

    elif args.upgrade:
        core.enhance_modules(modules, upgrade=True, modules_to_upgrade=args.upgrade[0])

    elif args.enhance_mmpm or args.force_refresh or is_expired:
        if args.force_refresh or is_expired:
            message = " Automated check for MMPM updates as part of snapshot refresh ... "
        else:
            message = " Checking for MMPM updates ... "

        utils.plain_print(utils.green_plus() + message)
        core.check_for_mmpm_enhancements(assume_yes=args.yes, gui=args.GUI)

    elif args.add_ext_module:
        core.add_external_module()

    elif args.magicmirror_config:
        core.edit_magicmirror_config()

    elif args.active_modules:
        core.get_active_modules()

    elif args.web_url:
        print(f'The MMPM web interface is live at: {core.get_web_interface_url()}')


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        utils.error_msg("Caught keyboard interrupt. Exiting")
