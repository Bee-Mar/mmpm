#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
import webbrowser
import mmpm.utils as utils
import mmpm.core as core
import mmpm.opts as opts
import mmpm.consts as consts
import mmpm.models as models
from typing import List, Dict

MagicMirrorPackage = models.MagicMirrorPackage

__version__ = 1.25


def main(argv):
    ''' Main entry point for CLI '''

    parser = opts.get_user_args()
    args, additional_args = parser.parse_known_args()

    if args.version:
        print(f'{__version__}')
        sys.exit(0)

    current_snapshot, next_snapshot = utils.calc_snapshot_timestamps()
    snapshot_expired: bool = utils.should_refresh_packages(current_snapshot, next_snapshot)
    should_refresh: bool = True if args.subcmd == opts.DATABASE and args.refresh else snapshot_expired

    packages: Dict[str, List[MagicMirrorPackage]] = core.load_packages(force_refresh=should_refresh)

    if (snapshot_expired and args.subcmd != opts.DATABASE) or (snapshot_expired and args.subcmd == opts.DATABASE and not args.refresh):
        core.check_for_mmpm_updates() # automated check for updates to MMPM

    if not packages:
        utils.fatal_msg('Unable to retrieve packages.')

    if args.subcmd == opts.LIST:
        if args.installed:
            installed_packages = core.get_installed_packages(packages)

            if not installed_packages:
                utils.fatal_msg('No packages are currently installed')

            core.display_packages(installed_packages, table_formatted=args.table_formatted, include_path=True)

        elif args.categories:
            core.display_categories(packages, table_formatted=args.table_formatted)
        elif args.all:
            core.display_packages(packages, table_formatted=args.table_formatted)
        elif args.gui_url:
            print(f'{core.get_web_interface_url()}')
        else:
            utils.no_arguments_provided(args.subcmd)

    elif args.subcmd == opts.SHOW:
        if not additional_args:
            utils.no_arguments_provided(args.subcmd)

        for query in additional_args:
            result = core.search_packages(packages, query, by_title_only=True)

            if not result:
                utils.fatal_msg(f'Unable to match {query} to a package title')

            core.show_package_details(result)

    elif args.subcmd == opts.OPEN:
        if additional_args:
            utils.invalid_additional_arguments(args.subcmd)
        elif args.config:
            utils.open_default_editor(consts.MAGICMIRROR_CONFIG_FILE)
        elif args.custom_css:
            utils.open_default_editor(consts.MAGICMIRROR_CUSTOM_CSS_FILE)
        elif args.gui:
            webbrowser.open(core.get_web_interface_url())
        elif args.mm_wiki:
            webbrowser.open(consts.MAGICMIRROR_WIKI_URL)
        elif args.mmpm_wiki:
            webbrowser.open(consts.MMPM_WIKI_URL)
        else:
            utils.no_arguments_provided(args.subcmd)

    elif args.subcmd == opts.ADD_EXT_PKG:
        if args.remove:
            core.remove_external_package_source([utils.sanitize_name(package) for package in args.remove], assume_yes=args.assume_yes)
        else:
            core.add_external_package(args.title, args.author, args.repo, args.desc)

    elif args.subcmd == opts.UPDATE:
        if additional_args:
            utils.invalid_additional_arguments(args.subcmd)
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

    elif args.subcmd == opts.INSTALL:
        if not additional_args:
            utils.no_arguments_provided(args.subcmd)
        elif args.magicmirror:
            core.install_magicmirror()
        elif args.autocomplete:
            core.install_autocompletion(assume_yes=args.assume_yes)
        else:
            installation_candidates = core.get_installation_candidates(
                packages,
                [utils.sanitize_name(package) for package in additional_args],
            )

            core.install_packages(installation_candidates, assume_yes=args.assume_yes)

    elif args.subcmd == opts.REMOVE:
        if not additional_args:
            utils.no_arguments_provided(args.subcmd)

        installed_packages = core.get_installed_packages(packages)

        if not installed_packages:
            utils.fatal_msg("No packages are currently installed")

        core.remove_packages(
            installed_packages,
            [utils.sanitize_name(package) for package in additional_args],
            assume_yes=args.assume_yes
        )

    elif args.subcmd == opts.SEARCH:
        if not additional_args:
            utils.no_arguments_provided(args.subcmd)
        elif len(additional_args) > 1:
            utils.fatal_msg(f'Too many arguments. `mmpm {args.subcmd}` only accepts one search argument')
        else:
            core.display_packages(
                core.search_packages(packages, additional_args[0], case_sensitive=args.case_sensitive),
                table_formatted=args.table_formatted
            )

    elif args.subcmd == opts.MM_CTL:
        if additional_args:
            utils.invalid_additional_arguments(args.subcmd)
        elif args.status:
            core.display_active_packages(table_formatted=args.table_formatted)
        elif args.start:
            core.start_magicmirror()
        elif args.stop:
            core.stop_magicmirror()
        elif args.restart:
            core.restart_magicmirror()
        else:
            utils.no_arguments_provided(args.subcmd)

    elif args.subcmd == opts.DATABASE:
        if args.refresh:
            sys.exit(0)
        if additional_args:
            utils.invalid_additional_arguments(args.subcmd)
        elif args.details:
            core.snapshot_details(packages)
        else:
            utils.no_arguments_provided(args.subcmd)

    elif args.subcmd == opts.LOG:
        if additional_args:
            utils.invalid_additional_arguments(args.subcmd)
        elif not args.cli and not args.gui:
            # if the user doesn't provide arguments, just display everything, but consider the --tail arg
            core.display_log_files(True, True, args.tail)
        else:
            core.display_log_files(args.cli, args.gui, args.tail)

    elif args.subcmd == opts.ENV:
        if additional_args:
            utils.invalid_additional_arguments(args.subcmd)
        else:
            core.display_mmpm_env_vars()

    else:
        utils.error_msg('Unknown argument\n')
        parser.print_help()


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print()
        utils.log.info('User killed process with keyboard interrupt')
        sys.exit(127)
