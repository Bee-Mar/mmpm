#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
from mmpm import utils, colors, core, opts

__version__ = 1.25


def main(argv):
    ''' Main entry point for CLI '''

    parser = opts.get_user_args()
    args, additional_args = parser.parse_known_args()

    if args.version:
        print(f'{__version__}')
        sys.exit(0)

    current_snapshot, next_snapshot = utils.calc_snapshot_timestamps()
    should_refresh = True if args.subcommand == opts.DATABASE and args.refresh else utils.should_refresh_modules(current_snapshot, next_snapshot)

    modules = core.load_modules(force_refresh=should_refresh)

    if not modules:
        utils.error_msg('Fatal. Unable to retrieve modules.')
        sys.exit(1)

    if args.subcommand == opts.LIST:
        if args.installed:
            installed_modules = core.get_installed_modules(modules)

            if not installed_modules:
                utils.error_msg("No modules are currently installed")
                sys.exit(1)

            core.display_modules(installed_modules, table_formatted=args.table_formatted)

        elif args.categories:
            core.display_modules(modules, list_categories=True, table_formatted=args.table_formatted)
        elif args.all:
            core.display_modules(modules, table_formatted=args.table_formatted)
        elif args.gui_url:
            print(f'{core.get_web_interface_url()}')

    elif args.subcommand == opts.SHOW:
        if not additional_args:
            utils.error_msg('No module(s) provided')
            sys.exit(1)

        results = [core.search_modules(modules, search, case_sensitive=True, by_title_only=True) for search in additional_args]

        if not results[0]:
            utils.error_msg('Unable to match query to module name(s). This search is case-sensitive')
        else:
            core.show_module_details(results[0])

    elif args.subcommand == opts.OPEN:
        if args.config:
            core.open_magicmirror_config()
        elif args.gui:
            core.open_mmpm_gui()
        else:
            utils.error_msg('No options provided. See `mmpm open --help`')

    elif args.subcommand == opts.ADD_EXT_MODULE:
        if args.remove:
            core.remove_external_module_source([utils.sanitize_name(module) for module in args.remove])
        else:
            core.add_external_module(args.title, args.author, args.repo, args.desc)

    elif args.subcommand == opts.UPDATE:
        if args.full:
            pass
        elif args.mmpm:
            pass
        elif args.magicmirror:
            core.check_for_magicmirror_updates()
        else:
            core.check_for_module_updates(modules)

    elif args.subcommand == opts.UPGRADE:
        if args.all:
            pass
        else:
            core.upgrade_modules(
                modules,
                modules_to_upgrade=additional_args[0] if additional_args else [],
                assume_yes=args.assume_yes
            )

    elif args.subcommand == opts.INSTALL:
        installation_candidates = core.get_installation_candidates(
            modules,
            [utils.sanitize_name(module) for module in additional_args],
        )

        core.install_modules(installation_candidates, assume_yes=args.assume_yes)

    elif args.subcommand == opts.REMOVE:
        if not additional_args:
            utils.error_msg('No module names provided')
        else:
            core.remove_modules(
                modules,
                [utils.sanitize_name(module) for module in additional_args],
                assume_yes=args.assume_yes
            )

    elif args.subcommand == opts.SEARCH:
        core.display_modules(
            core.search_modules(modules, additional_args[0], case_sensitive=args.case_sensitive),
            table_formatted=args.table_formatted
        )

    elif args.subcommand == opts.UPGRADE:
        if args.upgrade_full:
            pass
        if args.upgrade_modules:
            pass

    elif args.subcommand == opts.MM_CTL:
        if args.install:
            core.install_magicmirror(args.GUI)
        elif args.update:
            pass
        elif args.upgrade:
            pass
        elif args.status:
            core.get_active_modules(table_formatted=args.table_formatted)
        elif args.start:
            core.start_magicmirror()
        elif args.stop:
            core.stop_magicmirror()
        elif args.restart:
            core.restart_magicmirror()

    elif args.subcommand == opts.DATABASE:
        if args.details:
            core.snapshot_details(modules)
        elif args.refresh:
            pass

    elif args.subcommand == opts.LOGS:
        if not args.cli and not args.gui:
            # if the user doesn't provide arguments, just display everything, but consider the --tail arg
            core.display_log_files(True, True, args.tail)
        else:
            core.display_log_files(args.cli, args.gui, args.tail)

    elif args.subcommand == opts.UPDATE:
        if should_refresh:
            message = " Automated check for MMPM updates as part of snapshot refresh ... "

        if args.mmpm:
            message = " Checking for MMPM updates ... "
        elif args.magicmirror:
            message = " Checking for MagicMirror updates ... "
        elif args.full:
            pass

        utils.plain_print(utils.green_plus() + message)
        core.check_for_mmpm_enhancements(assume_yes=args.assume_yes, gui=args.GUI)

    elif args.subcommand == opts.ENV:
        if additional_args:
            utils.error_msg('`mmpm env` does not accept any additional arguments')
        else:
            core.display_mmpm_env_vars()

    else:
        utils.error_msg('Unknown argument\n')
        parser.print_help()

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        utils.error_msg("Caught keyboard interrupt. Exiting")
