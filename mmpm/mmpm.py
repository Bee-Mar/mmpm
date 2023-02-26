#!/usr/bin/env python3
# pylint: disable=unused-argument,unused-import
from gevent import monkey
monkey.patch_all() # do not move these

import os
import sys
import json
import webbrowser
import mmpm.utils
import mmpm.core
import mmpm.consts
from argparse import Namespace
from mmpm.subcommands import options
from mmpm.constants import paths
from mmpm.env import MMPMEnv
from mmpm.gui import MMPMGui
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.package import RemotePackage, MagicMirrorPackage
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.controller import MagicMirrorController
from typing import List, Dict, Set
from socket import gethostbyname, gethostname
from pathlib import Path


__version__ = 3.0

logger = MMPMLogger.get_logger(__name__)
logger.setLevel(MMPMEnv.mmpm_log_level.get())

class MMPM:
    @classmethod
    def run(cls):
        ''' Main entry point for CLI '''

        parser = options.setup()

        if len(sys.argv) < 2:
            parser.print_help()
            sys.exit(127)

        args, additional_args = parser.parse_known_args()

        if args.subcmd in options.SINGLE_OPTION_ARGS and not mmpm.utils.assert_one_option_selected(args): # TODO: FIXME
            mmpm.utils.fatal_too_many_options(args)

        should_refresh = True if args.subcmd == options.DB and args.refresh else MagicMirrorDatabase.expired()

        MagicMirrorDatabase.load(refresh=should_refresh)

        if MagicMirrorDatabase.expired() and args.subcmd != mmpm.opts.UPDATE:
            MagicMirrorDatabase.update(automated=True)

        command: str = args.subcmd.lower().replace("-", "_")

        if hasattr(MMPM, command):
            getattr(MMPM, command)(args, additional_args)


    @classmethod
    def setup(cls):
        '''
        Runs at the start of each `mmpm` command executed to ensure all the default
        files exist, and if they do not, they are created.

        Parameters:
            None

        Returns:
            None
        '''

        paths.MMPM_CONFIG_DIR.mkdir(exist_ok=True)

        for data_file in paths.MMPM_REQUIRED_DATA_FILES:
            data_file.touch(exist_ok=True)

        current_env: dict = {}

        with open(paths.MMPM_ENV_FILE, 'r', encoding="utf-8") as env:
            try:
                current_env = json.load(env)
            except json.JSONDecodeError as error:
                logger.error(str(error))

        for key, value in mmpm.consts.MMPM_DEFAULT_ENV.items():
            if key not in current_env:
                current_env[key] = value

        with open(mmpm.consts.MMPM_ENV_FILE, 'w', encoding="utf-8") as env:
            json.dump(current_env, env, indent=2)



    @classmethod
    def version(cls, args, additional_args = None):
        print(f'{__version__}')


    @classmethod
    def list(cls, args, additional_args = None):
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

    @classmethod
    def show(cls, args, additional_args = None):
        if not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

        if args.remote:
            health: dict = RemotePackage.health()

            for status in health.values():
                if status[mmpm.consts.ERROR]:
                    logger.msg.fatal(status[mmpm.consts.ERROR])
                elif status[mmpm.consts.WARNING]:
                    logger.msg.warning(status[mmpm.consts.WARNING])

        for query in additional_args:
            for package in MagicMirrorDatabase.search(query, by_title_only=True):
                package.display(remote=args.remote, detailed=True)

    @classmethod
    def search(cls, args, additional_args = None):
        if not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

        if len(additional_args) > 1:
            logger.msg.fatal(f'Too many arguments. `mmpm {args.subcmd}` only accepts one search argument')
        else:
            query_result = MagicMirrorDatabase.search(additional_args[0], case_sensitive=args.case_sensitive, exclude_installed=args.exclude_installed)

            for package in query_result:
                package.display(title_only=args.title_only)

    @classmethod
    def mm_ctl(cls, args, additional_args = None):
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd) # TODO: FIXME
        elif args.status:
            MagicMirrorController.status()
        elif args.hide:
            MagicMirrorController.hide_modules(args.hide)
        elif args.show:
            MagicMirrorController.show_modules(args.show)
        elif args.start or args.stop or args.restart:
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

    @classmethod
    def log(cls, args, additional_args = None):
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)
        elif args.zip:
            MMPMLogger.zip()
        elif not args.cli and not args.gui:
            # if the user doesn't provide arguments, just display everything, but consider the --tail arg
            MMPMLogger.display(True, True, args.tail)
        else:
            MMPMLogger.display(args.cli, args.gui, args.tail)

    @classmethod
    def db(cls, args, additional_args = None):
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

    @classmethod
    def env(cls, args, additional_args = None):
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)
        else:
            MMPMEnv.display()


    @classmethod
    def update(cls, args, additional_args = None):
        if additional_args:
            mmpm.utils.fatal_invalid_additional_arguments(args.subcmd)

        total: int = int(MagicMirrorController.update()) + MagicMirrorDatabase.update()

        if not total:
            print('All packages and applications are up to date.')
        else:
            print(f'{total} upgrade(s) available. Run `mmpm list --upgradable` for details')

    @classmethod
    def upgrade(cls, args, additional_args = None):
        upgradable = MagicMirrorDatabase.get_upgradable()

        if not upgradable["mmpm"] and not upgradable["MagicMirror"] and not upgradable["packages"]:
            logger.msg.info("All packages and applications are up to date.\n ")

        if upgradable["packages"]:
            packages: Set[MagicMirrorPackage] = {MagicMirrorPackage(**package) for package in upgradable["packages"]}
            upgraded: Set[MagicMirrorPackage] = {}

            for package in packages:
                if package.upgrade():
                    upgraded.add(package)

            # whichever packages failed to upgrade, we'll hold onto those for future reference
            upgradable["packages"] = [package.serialize() for package in (packages - upgraded)]

        if upgradable["MagicMirror"]:
            success: bool = MagicMirrorController.upgrade()
            upgradable["MagicMirror"] = False if success else True

        if upgradable["mmpm"]:
            print("Run 'pip install --upgrade --no-cache-dir mmpm' to install the latest version of MMPM. Run 'mmpm update' after upgrading.")

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="w", encoding="utf-8") as upgrade_file:
            json.dump(upgradable, upgrade_file)


    @classmethod
    def install(cls, args, additional_args = None):
        if args.gui:
            MMPMGui.install()
        elif not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)
        else:
            results = []

            for name in additional_args:
                if name == "MagicMirror":
                    MagicMirrorController.install()
                elif name == "mmpm":
                    MagicMirrorController.install_mmpm_module(args.assume_yes)
                else:
                    results += MagicMirrorDatabase.search(name)

            for package in results:
                package.install(assume_yes=args.assume_yes)

            #MagicMirrorDatabase.install(packages=packages, assume_yes=args.assume_yes)
            #mmpm.core.install_packages(installation_candidates, assume_yes=args.assume_yes) # TODO: FIXME

    @classmethod
    def remove(cls, args, additional_args = None):
        if args.gui:
            MMPMGui.remove()

        elif not additional_args:
            mmpm.utils.fatal_no_arguments_provided(args.subcmd)

        for name in additional_args:
            if name == "MagicMirror":
                MagicMirrorController.remove()
            else:
                for package in MagicMirrorDatabase.search(name):
                    package.remove(assume_yes=args.assume_yes)

    @classmethod
    def open(cls, args, additional_args = None):
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

    @classmethod
    def add_ext_pkg(cls, args, additional_args = None):
        if args.remove:
            # TODO: FIXME
            MagicMirrorDatabase.remove_external_package_source(
                [mmpm.utils.sanitize_name(package) for package in args.remove],
                assume_yes=args.assume_yes
            )
        else:
            MagicMirrorDatabase.add_external_package(args.title, args.author, args.repo, args.desc)

    @classmethod
    def completion(cls, args, additional_args = None):
        '''
        Adds autocompletion configuration to a user's shell configuration file.
        Detects configuration files for bash, zsh, fish, and tcsh

        Parameters:
            assume_yes (bool): if True, assume yes for user response, and do not display prompt

        Returns:
            None
        '''

        if not mmpm.utils.prompt('Are you sure you want to install the autocompletion feature for the MMPM CLI?', assume_yes=args.assume_yes):
            logger.info('User cancelled installation of autocompletion for MMPM CLI')
            return

        logger.info('user attempting to install MMPM autocompletion')
        shell: str = os.environ['SHELL']

        logger.info(f'detected user shell to be {shell}')

        autocomplete_url: str = 'https://github.com/kislyuk/argcomplete#activating-global-completion'
        error_message: str = f'Please see {autocomplete_url} for help installing autocompletion'

        complete_message = lambda config: f'Autocompletion installed. Please source {config} for the changes to take effect' # pylint: disable=unnecessary-lambda-assignment
        failed_match_message = lambda shell, configs: f'Unable to locate {shell} configuration file (looked for {configs}). {error_message}' # pylint: disable=unnecessary-lambda-assignment

        def __match_shell_config__(configs: List[str]) -> str:
            logger.info(f'searching for one of the following shell configuration files {configs}')
            for config in configs:
                config = mmpm.consts.HOME_DIR / config
                if config.exists():
                    logger.info(f'found {str(config)} shell configuration file for {shell}')
                    return config
            return ''

        def __eval__(command: str) -> None:
            logger.info(f'executing {command} to install autocompletion')
            os.system(command)

        if 'bash' in shell:
            files = ['.bashrc', '.bash_profile', '.bash_login', '.profile']
            config = __match_shell_config__(files)

            logger.msg.info("Detected 'bash' shell.\n")

            if not config:
                logger.msg.fatal(failed_match_message('bash', files))

            __eval__(f'echo \'eval "$(register-python-argcomplete mmpm)"\' >> {config}')

            print(complete_message(config))

        elif 'zsh' in shell:
            files = ['.zshrc', '.zprofile', '.zshenv', '.zlogin', '.profile']
            config = __match_shell_config__(files)

            logger.msg.info("Detected 'zsh' shell.\n")

            if not config:
                logger.msg.fatal(failed_match_message('zsh', files))

            __eval__(f"echo 'autoload -U bashcompinit' >> {config}")
            __eval__(f"echo 'bashcompinit' >> {config}")
            __eval__(f'echo \'eval "$(register-python-argcomplete mmpm)"\' >> {config}')

            print(complete_message(config))

        elif 'tcsh' in shell:
            files = ['.tcshrc', '.cshrc', '.login']
            config = __match_shell_config__(files)

            logger.msg.info("Detected 'tcsh' shell.\n")

            if not config:
                logger.msg.fatal(failed_match_message('tcsh', files))

            __eval__(f"echo 'eval `register-python-argcomplete --shell tcsh mmpm`' >> {config}")

            print(complete_message(config))

        elif 'fish' in shell:
            files = ['.config/fish/config.fish']
            config = __match_shell_config__(files)

            logger.msg.info("Detected 'fish' shell.\n")

            if not config:
                logger.msg.fatal(failed_match_message('fish', files))

            __eval__(f"register-python-argcomplete --shell fish mmpm >> {config}")

            print(complete_message(config))

        else:
            logger.msg.fatal(f'Unable install autocompletion for ({shell}). Please see {autocomplete_url} for help installing autocomplete')


    @classmethod
    def guided_setup(cls, args, additional_args = None):
        '''
        Provides the user a guided configuration of the environment variables, and
        feature installation. This can be re-run as many times as necessary.

        Parameters:
            None

        Returns:
            None
        '''
        valid_input: Callable = mmpm.utils.assert_valid_input

        print(mmpm.color.bright_green("Welcome to MMPM's guided setup!\n"))
        print("I'll help you setup your environment variables, and install additional features.\n\n")
        print("Let's get started!\n")

        magicmirror_root: str = f"{Path.home()}/MagicMirror"
        magicmirror_uri: str = f'http://{mmpm.utils.get_host_ip()}:8080'
        magicmirror_pm2_proc: str = ''
        magicmirror_docker_compose_file: str = ''
        mmpm_is_docker_image: bool = False
        install_gui: bool = False
        install_autocomplete: bool = False
        install_as_module: bool = False

        magicmirror_root = valid_input(f'What is the absolute path to the root of your MagicMirror installation (ie. {Path.home()}/MagicMirror)? ')
        mmpm_is_docker_image = mmpm.utils.prompt('Is MMPM running as a Docker image? ')

        if not mmpm_is_docker_image and mmpm.utils.prompt('Did you install MagicMirror using docker-compose?'):
            magicmirror_docker_compose_file = valid_input(f'What is the absolute path to the MagicMirror docker-compose file (ie. {Path.home()}/docker-compose.yml)? ')

        if not mmpm_is_docker_image and not magicmirror_docker_compose_file and mmpm.utils.prompt('Are you using PM2 to start/stop MagicMirror?'):
            magicmirror_pm2_proc = valid_input('What is the name of the PM2 process for MagicMirror? ')

        if not mmpm.utils.prompt(f'Is {magicmirror_uri} the address used to open MagicMirror in your browser? '):
            magicmirror_uri = valid_input(f'What is the full address used to access MagicMirror? ')

        install_gui = not mmpm_is_docker_image and mmpm.utils.prompt('Would you like to install the MMPM GUI (web interface)?')
        install_as_module = mmpm.utils.prompt('Would you like to hide/show MagicMirror modules through MMPM?')
        install_autocomplete = mmpm.utils.prompt('Would you like to install tab-autocomplete for the MMPM CLI?')

        with open(mmpm.consts.MMPM_ENV_FILE, 'w', encoding="utf-8") as env:
            json.dump({
                MMPMEnv.mmpm_magicmirror_root.name: os.path.normpath(magicmirror_root),
                MMPMEnv.mmpm_magicmirror_uri.name: magicmirror_uri,
                MMPMEnv.mmpm_magicmirror_pm2_process_name.name: magicmirror_pm2_proc,
                MMPMEnv.mmpm_magicmirror_docker_compose_file.name: os.path.normpath(magicmirror_docker_compose_file),
                MMPMEnv.mmpm_is_docker_image.name: mmpm_is_docker_image
            }, env, indent=2)

        print('\nBased on your responses, your environment variables have been set as:')
        MMPMEnv.display()
        print("\n \nExecute the following commands to install the desired features:")

        if install_as_module:
            print(mmpm.color.bright_green("mmpm install mmpm"))
        if install_gui:
            print(mmpm.color.bright_green("mmpm install --gui"))
        if install_autocomplete:
            print(mmpm.color.bright_green("mmpm completion"))

        print()
