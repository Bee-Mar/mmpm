#!/usr/bin/env python3
# pylint: disable=unused-argument
# pylint: disable=unused-import
from gevent import monkey
monkey.patch_all() # do not move these

import sys
import os
import webbrowser
import mmpm.utils
import mmpm.core
import mmpm.opts
import mmpm.consts
from mmpm.env import MMPMEnv
from mmpm.gui import MMPMGui
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.package import RemotePackage
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.controller import MagicMirrorController
from typing import List, Dict


__version__ = 3.0

logger = MMPMLogger.get_logger(__name__)
logger.setLevel(MMPMEnv.mmpm_log_level.get())

class MMPM:
    @classmethod
    def run(self):
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

            elif args.all or args.exclude_installed:
                for package in MagicMirrorDatabase.packages:
                    package.display(title_only=args.title_only, exclude_installed=args.exclude_installed)

            elif args.categories:
                MagicMirrorDatabase.display_categories(title_only=args.title_only)
            elif args.gui_url:
                print(MMPMGui.get_uri())
            elif args.upgradable:
                MagicMirrorDatabase.display_upgradable()
            else:
                mmpm.utils.fatal_no_arguments_provided(args.subcmd)

        elif args.subcmd == mmpm.opts.SHOW:
            if not additional_args:
                mmpm.utils.fatal_no_arguments_provided(args.subcmd)

            if args.remote:
                health: dict = RemotePackage.health()

                for status in health.values():
                    if status[mmpm.consts.ERROR]:
                        mmpm.utils.fatal_msg(status[mmpm.consts.ERROR])
                    elif status[mmpm.consts.WARNING]:
                        mmpm.utils.warning_msg(status[mmpm.consts.WARNING])

            for query in additional_args:
                for package in MagicMirrorDatabase.search(query, by_title_only=True):
                    package.display(remote=args.remote, detailed=True)

        elif args.subcmd == mmpm.opts.OPEN:
            if additional_args:
                mmpm.utils.fatal_invalid_additional_arguments(args.subcmd) # TODO: FIXME
            elif args.config:
                mmpm.utils.open_default_editor(str(Path(MMPMEnv.mmpm_magicmirror_root.get() / "config" / "config.js"))) # TODO: FIXME
            elif args.custom_css:
                mmpm.utils.open_default_editor(str(Path(MMPMEnv.mmpm_magicmirror_root.get() / "css" / "custom.css"))) # TODO: FIXME
            elif args.magicmirror:
                mmpm.utils.run_cmd(['xdg-open', MMPMEnv.mmpm_magicmirror_uri.get()], background=True) # TODO: move these into a class?
            elif args.gui:
                mmpm.utils.run_cmd(['xdg-open', MMPMGui.get_uri()], background=True)
            elif args.mm_wiki:
                mmpm.utils.run_cmd(['xdg-open', mmpm.consts.MAGICMIRROR_WIKI_URL], background=True)
            elif args.mm_docs:
                mmpm.utils.run_cmd(['xdg-open', mmpm.consts.MAGICMIRROR_DOCUMENTATION_URL], background=True)
            elif args.mmpm_wiki:
                mmpm.utils.run_cmd(['xdg-open', mmpm.consts.MMPM_WIKI_URL], background=True)
            elif args.mmpm_env:
                mmpm.utils.open_default_editor(mmpm.consts.MMPM_ENV_FILE) # TODO: FIXME
            else:
                mmpm.utils.fatal_no_arguments_provided(args.subcmd) # TODO: FIXME

        elif args.subcmd == mmpm.opts.ADD_EXT_PKG:
            if args.remove:
                # TODO: FIXME
                MagicMirrorDatabase.remove_external_package_source(
                    [mmpm.utils.sanitize_name(package) for package in args.remove],
                    assume_yes=args.assume_yes
                )
            else:
                MagicMirrorDatabase.add_external_package(args.title, args.author, args.repo, args.desc)

        elif args.subcmd == mmpm.opts.UPDATE:
            if additional_args:
                mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)

            total: int = MagicMirrorDatabase.update() + int(MagicMirrorController.update())

            if not total:
                print('All packages are up to date')
            else:
                print(f'{total} upgrade(s) available. Run `mmpm list --upgradable` for details')

        elif args.subcmd == mmpm.opts.UPGRADE:
            upgradable = MagicMirrorDatabase.get_upgradable()

            for package in upgradable["packages"]:
                MagicMirrorPackage(**package).upgrade()

            if upgradable["MagicMirror"]:
                MagicMirrorController.upgrade()

            if upgradable["mmpm"]:
                print("Run 'pip install --upgrade --no-cache-dir mmpm' to install the latest version of MMPM.")

        elif args.subcmd == mmpm.opts.INSTALL:
            if args.gui:
                MMPMGui.install()
            elif args.as_module:
                MagicMirrorController.install_mmpm_module()
            elif args.magicmirror:
                MagicMirrorController.install()
            elif args.autocomplete:
                mmpm.core.install_autocompletion(assume_yes=args.assume_yes)
            elif not additional_args:
                mmpm.utils.fatal_no_arguments_provided(args.subcmd)
            else:
                results = []

                for name in additional_args:
                    results += MagicMirrorDatabase.search(name)

                for package in results:
                    package.install(assume_yes=args.assume_yes)

                #MagicMirrorDatabase.install(packages=packages, assume_yes=args.assume_yes)
                #mmpm.core.install_packages(installation_candidates, assume_yes=args.assume_yes) # TODO: FIXME

        elif args.subcmd == mmpm.opts.REMOVE:
            if args.gui:
                MMPMGui.remove()

            if args.magicmirror:
                MagicMirrorController.remove()

            elif not additional_args:
                mmpm.utils.fatal_no_arguments_provided(args.subcmd)

            for arg in additional_args:
                for package in MagicMirrorDatabase.search(arg):
                    package.remove(assume_yes=args.assume_yes)

        elif args.subcmd == mmpm.opts.SEARCH:
            if not additional_args:
                mmpm.utils.fatal_no_arguments_provided(args.subcmd)

            if len(additional_args) > 1:
                mmpm.utils.fatal_msg(f'Too many arguments. `mmpm {args.subcmd}` only accepts one search argument')
            else:
                query_result = MagicMirrorDatabase.search(additional_args[0], case_sensitive=args.case_sensitive, exclude_installed=args.exclude_installed)

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
                    logger.msg.fatal('Cannot execute this command within a docker image')
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
                MMPMLogger.zip()
            elif not args.cli and not args.gui:
                # if the user doesn't provide arguments, just display everything, but consider the --tail arg
                MMPMLogger.display(True, True, args.tail)
            else:
                MMPMLogger.display(args.cli, args.gui, args.tail)

        elif args.subcmd == mmpm.opts.ENV:
            if additional_args:
                mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)
            else:
                MMPMEnv.display()

        else:
            parser.print_help()

