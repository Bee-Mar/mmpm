#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys

import mmpm.utils
import mmpm.core
import mmpm.opts
import mmpm.consts
import mmpm.models
import os

from typing import List, Dict


MagicMirrorPackage = mmpm.models.MagicMirrorPackage
get_env = mmpm.utils.get_env

__version__ = 2.0


def main(argv):
    ''' Main entry point for CLI '''

    parser = mmpm.opts.get_user_args()
    args, additional_args = parser.parse_known_args()

    if args.version:
        print(f'{__version__}')
        sys.exit(0)

    if args.migrate:
        mmpm.core.migrate()
        sys.exit(0)

    mmpm.utils.assert_required_defaults_exist()

    if args.subcmd in mmpm.opts.SINGLE_OPTION_ARGS and not mmpm.utils.assert_one_option_selected(args):
        mmpm.utils.fatal_too_many_options(args)

    creation_date, expiration_date = mmpm.utils.calculation_expiration_date_of_database()
    databased_expired: bool = mmpm.utils.should_refresh_database(creation_date, expiration_date)
    should_refresh: bool = True if args.subcmd == mmpm.opts.DATABASE and args.refresh else databased_expired

    packages: Dict[str, List[MagicMirrorPackage]] = mmpm.core.load_packages(force_refresh=should_refresh)

    if databased_expired and args.subcmd != mmpm.opts.UPDATE and mmpm.core.check_for_mmpm_updates(automated=True):
        print('Upgrade available for MMPM. Execute `mmpm upgrade` to perform the upgrade now')

    if not packages:
        mmpm.utils.fatal_msg('Unable to retrieve packages. Please check your internet connection.')

    if args.subcmd == mmpm.opts.LIST:
        if args.installed:
            installed_packages = mmpm.core.get_installed_packages(packages)

            if not installed_packages:
                mmpm.utils.fatal_msg('No packages are currently installed')

            mmpm.core.display_packages(installed_packages, title_only=args.title_only, include_path=True)

        elif args.all:
            mmpm.core.display_packages(packages, title_only=args.title_only)
        elif args.exclude_local:
            excluded = mmpm.utils.get_difference_of_packages(packages, mmpm.core.get_installed_packages(packages))
            mmpm.core.display_packages(excluded, title_only=args.title_only)
        elif args.categories:
            mmpm.core.display_categories(packages, title_only=args.title_only)
        elif args.gui_url:
            print(f'{mmpm.core.get_web_interface_url()}')
        elif args.upgradeable:
            mmpm.core.display_available_upgrades()
        else:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

    elif args.subcmd == mmpm.opts.SHOW:
        if not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

        if args.verbose:
            health: dict = mmpm.utils.get_remote_repo_api_health()

            for api in health:
                if health[api][mmpm.consts.ERROR]:
                    mmpm.utils.fatal_msg(health[api][mmpm.consts.ERROR])
                elif health[api][mmpm.consts.WARNING]:
                    mmpm.utils.warning_msg(health[api][mmpm.consts.WARNING])

        for query in additional_args:
            result = mmpm.core.search_packages(packages, query, by_title_only=True)

            if not result:
                mmpm.utils.fatal_msg(f'Unable to match {query} to a package title')

            mmpm.core.show_package_details(result, args.verbose)

    elif args.subcmd == mmpm.opts.OPEN:
        import webbrowser

        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)
        elif args.config:
            mmpm.utils.open_default_editor(os.path.join(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV), 'config', 'config.js'))
        elif args.custom_css:
            mmpm.utils.open_default_editor(os.path.join(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV), 'custom', 'custom.css'))
        elif args.magicmirror:
            webbrowser.open(get_env(mmpm.consts.MMPM_MAGICMIRROR_URI_ENV))
        elif args.gui:
            webbrowser.open(mmpm.core.get_web_interface_url())
        elif args.mm_wiki:
            webbrowser.open(mmpm.consts.MAGICMIRROR_WIKI_URL)
        elif args.mm_docs:
            webbrowser.open(mmpm.consts.MAGICMIRROR_DOCUMENTATION_URL)
        elif args.mmpm_wiki:
            webbrowser.open(mmpm.consts.MMPM_WIKI_URL)
        elif args.mmpm_env:
            mmpm.utils.open_default_editor(mmpm.consts.MMPM_ENV_FILE)
        else:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

    elif args.subcmd == mmpm.opts.ADD_EXT_PKG:
        if args.remove:
            mmpm.core.remove_external_package_source(
                [mmpm.utils.sanitize_name(package) for package in args.remove],
                assume_yes=args.assume_yes
            )
        else:
            mmpm.core.add_external_package(args.title, args.author, args.repo, args.desc)

    elif args.subcmd == mmpm.opts.UPDATE:
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)

        package_upgrades: List[MagicMirrorPackage] = mmpm.core.check_for_package_updates(packages)
        magicmirror_upgrade: bool = mmpm.core.check_for_magicmirror_updates()
        mmpm_upgrade: bool = mmpm.core.check_for_mmpm_updates()
        total = len(package_upgrades) + int(mmpm_upgrade) + int(magicmirror_upgrade)

        if not total:
            print('All packages are up to date')
        else:
            message: str = f"{total} {'upgrade' if total == 1 else 'upgrades'} {'is' if total == 1 else 'are'} available"
            print(f'{message}. Run `mmpm list --upgradable` for details')

    elif args.subcmd == mmpm.opts.UPGRADE:
        mmpm.core.upgrade_available(args.assume_yes, additional_args)

    elif args.subcmd == mmpm.opts.INSTALL:
        if args.magicmirror:
            mmpm.core.install_magicmirror()
        elif args.autocomplete:
            mmpm.core.install_autocompletion(assume_yes=args.assume_yes)
        elif not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)
        else:
            installation_candidates = mmpm.core.get_installation_candidates(
                packages,
                [mmpm.utils.sanitize_name(package) for package in additional_args]
            )

            mmpm.core.install_packages(installation_candidates, assume_yes=args.assume_yes)

    elif args.subcmd == mmpm.opts.REMOVE:
        if not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

        installed_packages = mmpm.core.get_installed_packages(packages)

        if not installed_packages:
            mmpm.utils.fatal_msg("No packages are currently installed")

        mmpm.core.remove_packages(
            installed_packages,
            [mmpm.utils.sanitize_name(package) for package in additional_args],
            assume_yes=args.assume_yes
        )

    elif args.subcmd == mmpm.opts.SEARCH:
        if not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

        if len(additional_args) > 1:
            mmpm.utils.fatal_msg(f'Too many arguments. `mmpm {args.subcmd}` only accepts one search argument')
        else:
            if args.exclude_local:
                packages = mmpm.utils.get_difference_of_packages(packages, mmpm.core.get_installed_packages(packages))

            mmpm.core.display_packages(
                mmpm.core.search_packages(packages, additional_args[0], case_sensitive=args.case_sensitive),
                title_only=args.title_only
            )

    elif args.subcmd == mmpm.opts.MM_CTL:
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)
        elif args.status:
            mmpm.core.display_magicmirror_modules_status()
        elif args.hide:
            mmpm.core.hide_magicmirror_modules(args.hide)
        elif args.show:
            mmpm.core.show_magicmirror_modules(args.show)
        elif args.start or args.stop or args.restart or args.rotate:
            MMPM_IS_DOCKER_IMAGE: str = mmpm.utils.get_env('MMPM_IS_DOCKER_IMAGE')
            if bool(MMPM_IS_DOCKER_IMAGE.title()) == True:
                mmpm.utils.fatal_msg('Cannot execute this command within a docker image')
            elif args.start:
                mmpm.core.start_magicmirror()
            elif args.stop:
                mmpm.core.stop_magicmirror()
            elif args.restart:
                mmpm.core.restart_magicmirror()
            elif args.rotate:
                mmpm.core.rotate_raspberrypi_screen(args.rotate)
        else:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

    elif args.subcmd == mmpm.opts.DATABASE:
        if args.refresh:
            sys.exit(0)
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)
        elif args.details:
            mmpm.core.database_details(packages)
        elif args.dump:
            mmpm.core.dump_database()
        else:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

    elif args.subcmd == mmpm.opts.LOG:
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)
        elif not args.cli and not args.gui:
            # if the user doesn't provide arguments, just display everything, but consider the --tail arg
            mmpm.core.display_log_files(True, True, args.tail)
        else:
            mmpm.core.display_log_files(args.cli, args.gui, args.tail)

    elif args.subcmd == mmpm.opts.ENV:
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)
        else:
            mmpm.core.display_mmpm_env_vars()

    else:
        mmpm.utils.error_msg('Unknown argument\n')
        parser.print_help()


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print()
        mmpm.utils.log.info('User killed process with keyboard interrupt')
        sys.exit(127)
