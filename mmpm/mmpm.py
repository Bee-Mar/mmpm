#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
from mmpm import utils, colors, core, opts

__version__ = 1.13


def main(argv):
    ''' Main entry point for CLI '''

    args: object = opts.get_user_args()

    if args.version:
        print(f'{__version__}')
        sys.exit(0)

    current_snapshot, next_snapshot = utils.calc_snapshot_timestamps()
    should_refresh = True if args.subcommand == opts.SNAPSHOT and args.refresh else utils.should_refresh_modules(current_snapshot, next_snapshot)

    modules = core.load_modules(force_refresh=should_refresh)

    if not modules:
        utils.error_msg('Fatal. Unable to retrieve modules.')
        sys.exit(1)

    if args.subcommand == opts.SHOW:
        if args.installed:
            installed_modules = core.get_installed_modules(modules)

            if not installed_modules:
                utils.error_msg("No modules are currently installed")
                sys.exit(1)

            core.display_modules(installed_modules)

        elif args.categories:
            core.display_modules(modules, list_categories=True)
        elif args.all:
            core.display_modules(modules)
        elif args.gui_url:
            print(f'The MMPM web interface is live at: {core.get_web_interface_url()}')

    elif args.subcommand == opts.MODULE:
        if args.install:
            core.install_modules(modules, [utils.sanitize_name(module) for module in args.install])
        elif args.remove:
            core.remove_modules(modules, [utils.sanitize_name(module) for module in args.remove])
        elif args.search:
            core.display_modules(core.search_modules(modules, args.search[0]))
        elif args.update:
            core.enhance_modules(modules, update=True)
        elif args.upgrade:
            core.enhance_modules(modules, upgrade=True, modules_to_upgrade=args.upgrade[0])

    elif args.subcommand == opts.OPEN:
        if args.config:
            core.open_magicmirror_config()
        elif args.gui:
            core.open_mmpm_gui()

    elif args.subcommand == opts.ADD_EXT_MODULE:
        if args.remove:
            core.remove_external_module_source([utils.sanitize_name(module) for module in args.remove])
        else:
            core.add_external_module(args.title, args.author, args.repo, args.description)

    elif args.subcommand == opts.MAGICMIRROR:
        if args.install:
            core.install_magicmirror(args.GUI)
        elif args.update:
            pass
        elif args.upgrade:
            pass
        elif args.status:
            core.get_active_modules()
        elif args.start:
            core.start_magicmirror()
        elif args.stop:
            core.stop_magicmirror()
        elif args.restart:
            core.restart_magicmirror()

    elif args.subcommand == opts.SNAPSHOT:
        if args.details:
            core.snapshot_details(modules)

    elif args.subcommand == opts.TAIL:
        if args.mmpm:
            pass
        elif args.gunicorn:
            pass

    elif args.mmpm_update or args.snapshot_refresh or should_refresh:
        if args.force_refresh or should_refresh:
            message = " Automated check for MMPM updates as part of snapshot refresh ... "
        else:
            message = " Checking for MMPM updates ... "

        utils.plain_print(utils.green_plus() + message)
        core.check_for_mmpm_enhancements(assume_yes=args.yes, gui=args.GUI)


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        utils.error_msg("Caught keyboard interrupt. Exiting")
