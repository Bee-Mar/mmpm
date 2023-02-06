#!/usr/bin/env python3
# pylint: disable=unused-argument
# pylint: disable=unused-import
from gevent import monkey
monkey.patch_all() # do not move these

import sys
import os
import mmpm.utils
import mmpm.core
import mmpm.opts
import mmpm.consts
from typing import List, Dict
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.controller import MagicMirrorController
from mmpm.gui import MMPMGui
from mmpm.logger import MMPMLogger
from mmpm.models import MagicMirrorPackage
from mmpm.env import MMPMEnv


__version__ = 3.0

logger = MMPMLogger.get_logger(__name__)
logger.setLevel(MMPMEnv.mmpm_log_level.get())

def main(argv):
    ''' Main entry point for CLI '''

    parser = mmpm.opts.get_user_args()
    args, additional_args = parser.parse_known_args()

    if args.version:
        print(f'{__version__}')
        sys.exit(0)

    mmpm.utils.assert_required_defaults_exist() # TODO: FIXME

    if args.guided_setup:
        mmpm.core.guided_setup() # TODO: FIXME
        sys.exit(0)

    if args.subcmd in mmpm.opts.SINGLE_OPTION_ARGS and not mmpm.utils.assert_one_option_selected(args): # TODO: FIXME
        mmpm.utils.fatal_too_many_options(args)

    should_refresh = True if args.subcmd == mmpm.opts.DATABASE and args.refresh else MagicMirrorDatabase.expired()

    MagicMirrorDatabase.load(refresh=should_refresh)

    if MagicMirrorDatabase.expired() and args.subcmd != mmpm.opts.UPDATE and MagicMirrorDatabase.update(automated=True):
        print('Upgrade available for MMPM. Execute `pip3 install --upgrade --user mmpm` to perform the upgrade now')

    if not MagicMirrorDatabase.packages:
        mmpm.utils.fatal_msg('Unable to retrieve packages. Please check your internet connection.')

    if args.subcmd == mmpm.opts.LIST:
        if args.installed:
            for package in MagicMirrorDatabase.packages:
                if package.is_installed:
                    package.display(title_only=args.title_only, show_path=True)

        elif args.all or args.exclude_local:
            for package in MagicMirrorDatabase.packages:
                package.display(title_only=args.title_only)

            #MagicMirrorDatabase.display_packages(title_only=args.title_only, exclude_local=args.exclude_local)
        elif args.categories:
            MagicMirrorDatabase.display_categories(title_only=args.title_only)
        elif args.gui_url:
            print(MMPMGui.get_uri())
        elif args.upgradable:
            MagicMirrorDatabase.display_available_upgrades()
        else:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

    elif args.subcmd == mmpm.opts.SHOW:
        if not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

        if args.remote:
            health: dict = mmpm.utils.get_remote_repo_api_health() # TODO: FIXME

            for status in health.values():
                if status[mmpm.consts.ERROR]:
                    mmpm.utils.fatal_msg(status[mmpm.consts.ERROR])
                elif status[mmpm.consts.WARNING]:
                    mmpm.utils.warning_msg(status[mmpm.consts.WARNING])

        for query in additional_args:
            for package in MagicMirrorDatabase.search(query, by_title_only=True):
                package.display(remote=args.remote, detailed=True)

    elif args.subcmd == mmpm.opts.OPEN:
        import webbrowser

        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd) # TODO: FIXME
        elif args.config:
            mmpm.utils.open_default_editor(str(Path(MMPMEnv.mmpm_root.get() / "config" / "config.js"))) # TODO: FIXME
        elif args.custom_css:
            mmpm.utils.open_default_editor(str(Path(MMPMEnv.mmpm_root / "css" / "custom.css"))) # TODO: FIXME
        elif args.magicmirror:
            webbrowser.open(MMPMEnv.mmpm_magicmirror_uri.get())
        elif args.gui:
            webbrowser.open(mmpm.core.get_web_interface_url())
        elif args.mm_wiki:
            webbrowser.open(mmpm.consts.MAGICMIRROR_WIKI_URL)
        elif args.mm_docs:
            webbrowser.open(mmpm.consts.MAGICMIRROR_DOCUMENTATION_URL)
        elif args.mmpm_wiki:
            webbrowser.open(mmpm.consts.MMPM_WIKI_URL)
        elif args.mmpm_env:
            mmpm.utils.open_default_editor(mmpm.consts.MMPM_ENV_FILE) # TODO: FIXME
        else:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd) # TODO: FIXME

    elif args.subcmd == mmpm.opts.ADD_EXT_PKG:
        if args.remove:
            MagicMirrorDatabase.remove_external_package_source(
                [mmpm.utils.sanitize_name(package) for package in args.remove],
                assume_yes=args.assume_yes
            )
        else:
            MagicMirrorDatabase.add_external_package(args.title, args.author, args.repo, args.desc)

    elif args.subcmd == mmpm.opts.UPDATE:
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)

        total = MagicMirrorDatabase.update()

        if not total:
            print('All packages are up to date')
        else:
            print(f'{total} upgrade(s) available. Run `mmpm list --upgradable` for details')

    elif args.subcmd == mmpm.opts.UPGRADE:
        mmpm.core.upgrade_available_packages_and_applications(args.assume_yes, additional_args)

    elif args.subcmd == mmpm.opts.INSTALL:
        if args.gui:
            MMPMGui.install()
        elif args.as_module:
            mmpm.core.install_mmpm_as_magicmirror_module()
        elif args.magicmirror:
            mmpm.core.install_magicmirror()
        elif args.autocomplete:
            mmpm.core.install_autocompletion(assume_yes=args.assume_yes)
        elif not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)
        else:
            packages = []

            for name in additional_args: # TODO: FIXME
                packages += MagicMirrorDatabase.search(name)

            MagicMirrorDatabase.install(packages=packages, assume_yes=args.assume_yes)
            #mmpm.core.install_packages(installation_candidates, assume_yes=args.assume_yes)

    elif args.subcmd == mmpm.opts.REMOVE:
        if args.gui:
            MMPMGui.remove_mmpm_gui()

        elif not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

        installed_packages = MagicMirrorDatabase.get_installed_packages()

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
            query_result = MagicMirrorDatabase.search(additional_args[0], case_sensitive=args.case_sensitive, exclude_installed=args.exclude_installed)
            query_result.display(title_only=args.title_only)

            for package in query_result:
                package.display(title_only=args.title_only)

    elif args.subcmd == mmpm.opts.MM_CTL:
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd) # TODO: FIXME
        elif args.status:
            MagicMirrorController.status()
        elif args.hide:
            MagicMirrorController.hide_modules(args.hide)
        elif args.show:
            MagicMirrorController.show_modules(args.show)
        elif args.start or args.stop or args.restart or args.rotate != None:
            if MMPMEnv.mmpm_is_docker_image.get():
                mmpm.utils.fatal_msg('Cannot execute this command within a docker image')
            elif args.start:
                MagicMirrorController.start()
            elif args.stop:
                MagicMirrorController.stop()
            elif args.restart:
                MagicMirrorController.restart()
        else:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd) # TODO: FIXME

    elif args.subcmd == mmpm.opts.DATABASE:
        if args.refresh:
            sys.exit(0)
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)
        elif args.details:
            MagicMirrorDatabase.details()
        elif args.dump:
            MagicMirrorDatabase.dump()
        else:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

    elif args.subcmd == mmpm.opts.LOG:
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)
        elif args.zip:
            MMPMLogger.zip_mmpm_log_files()
        elif not args.cli and not args.gui:
            # if the user doesn't provide arguments, just display everything, but consider the --tail arg
            MMPMLogger.display_log_files(True, True, args.tail)
        else:
            MMPMLogger.display_log_files(args.cli, args.gui, args.tail)

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
        logger.info('User killed process with keyboard interrupt')
        sys.exit(127)
