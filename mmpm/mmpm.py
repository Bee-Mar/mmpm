#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
from mmpm import utils, core, opts

__version__ = 1.25


def main(argv):
    ''' Main entry point for CLI '''

    parser = opts.get_user_args()
    args, additional_args = parser.parse_known_args()

    if args.version:
        print(f'{__version__}')
        sys.exit(0)

    current_snapshot, next_snapshot = utils.calc_snapshot_timestamps()
    should_refresh = True if args.subcommand == opts.DATABASE and args.refresh else utils.should_refresh_packages(current_snapshot, next_snapshot)

    packages = core.load_packages(force_refresh=should_refresh)

    if not packages:
        utils.fatal_msg('Unable to retrieve packages.')

    if args.subcommand == opts.LIST:
        if args.installed:
            installed_modules = core.get_installed_packages(packages)

            if not installed_modules:
                utils.fatal_msg('No modules are currently installed')

            core.display_packages(installed_modules, table_formatted=args.table_formatted, include_path=True)

        elif args.categories:
            core.display_categories(packages, table_formatted=args.table_formatted)
        elif args.all:
            core.display_packages(packages, table_formatted=args.table_formatted)
        elif args.gui_url:
            print(f'{core.get_web_interface_url()}')
        else:
            utils.no_arguments_provided(args.subcommand)

    elif args.subcommand == opts.SHOW:
        if not additional_args:
            utils.no_arguments_provided(args.subcommand)

        for query in additional_args:
            result = core.search_packages(packages, query, show=True)

            if not result:
                utils.fatal_msg(f'Unable to match {query} to a module title')

            core.show_package_details(result)

    elif args.subcommand == opts.OPEN:
        if additional_args:
            utils.invalid_additional_arguments(args.subcommand)
        elif args.config:
            core.open_magicmirror_config()
        elif args.gui:
            core.open_mmpm_gui()
        elif args.magicmirror_wiki:
            core.open_magicmirror_wiki()
        else:
            utils.no_arguments_provided(args.subcommand)

    elif args.subcommand == opts.ADD_EXT_MODULE:
        if args.remove:
            core.remove_external_package_source([utils.sanitize_name(module) for module in args.remove], assume_yes=args.assume_yes)
        else:
            core.add_external_package(args.title, args.author, args.repo, args.desc)

    elif args.subcommand == opts.UPDATE:
        if additional_args:
            utils.invalid_additional_arguments(args.subcommand)
        elif args.full:
            core.check_for_package_updates(packages, args.assume_yes)
            core.check_for_magicmirror_updates(args.assume_yes)
            core.check_for_mmpm_updates(args.assume_yes)
        elif args.mmpm:
            core.check_for_mmpm_updates(args.assume_yes)
        elif args.magicmirror:
            core.check_for_magicmirror_updates(args.assume_yes)
        else:
            core.check_for_package_updates(packages, args.assume_yes)

    elif args.subcommand == opts.INSTALL:
        if not additional_args:
            utils.no_arguments_provided(args.subcommand)
        elif args.magicmirror:
            core.install_magicmirror(args.GUI)
        elif args.autocomplete:
            core.install_autocompletion(assume_yes=args.assume_yes)
        else:
            installation_candidates = core.get_installation_candidates(
                packages,
                [utils.sanitize_name(module) for module in additional_args],
            )

            core.install_packages(installation_candidates, assume_yes=args.assume_yes)

    elif args.subcommand == opts.REMOVE:
        if not additional_args:
            utils.no_arguments_provided(args.subcommand)

        installed_packages = core.get_installed_packages(packages)

        if not installed_packages:
            utils.fatal_msg("No modules are currently installed")

        core.remove_packages(
            installed_packages,
            [utils.sanitize_name(module) for module in additional_args],
            assume_yes=args.assume_yes
        )

    elif args.subcommand == opts.SEARCH:
        if not additional_args:
            utils.no_arguments_provided(args.subcommand)
        elif len(additional_args) > 1:
            utils.fatal_msg(f'Too many arguments. `mmpm {args.subcommand}` only accepts one search argument')
        else:
            core.display_packages(
                core.search_packages(packages, additional_args[0], case_sensitive=args.case_sensitive),
                table_formatted=args.table_formatted
            )

    elif args.subcommand == opts.MM_CTL:
        if additional_args:
            utils.invalid_additional_arguments(args.subcommand)
        elif args.status:
            core.get_active_packages(table_formatted=args.table_formatted)
        elif args.start:
            core.start_magicmirror()
        elif args.stop:
            core.stop_magicmirror()
        elif args.restart:
            core.restart_magicmirror()
        else:
            utils.no_arguments_provided(args.subcommand)

    elif args.subcommand == opts.DATABASE:
        if args.refresh:
            sys.exit(0)
        if additional_args:
            utils.invalid_additional_arguments(args.subcommand)
        elif args.details:
            core.snapshot_details(packages)
        else:
            utils.no_arguments_provided(args.subcommand)

    elif args.subcommand == opts.LOG:
        if additional_args:
            utils.invalid_additional_arguments(args.subcommand)
        elif not args.cli and not args.gui:
            # if the user doesn't provide arguments, just display everything, but consider the --tail arg
            core.display_log_files(True, True, args.tail)
        else:
            core.display_log_files(args.cli, args.gui, args.tail)

    elif args.subcommand == opts.ENV:
        if additional_args:
            utils.invalid_additional_arguments(args.subcommand)
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
