#!/usr/bin/env python3
# pylint: disable=unused-argument,unused-import
from gevent import monkey
monkey.patch_all()  # do not move these

from mmpm.env import MMPMEnv
from mmpm.gui import MMPMGui
from mmpm.constants import paths, urls, color
from mmpm.logger import MMPMLogger
from mmpm.subcommands import options
from mmpm.singleton import Singleton
from mmpm.__version__ import version as mmpm_version
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.controller import MagicMirrorController
from mmpm.magicmirror.package import RemotePackage, MagicMirrorPackage
from mmpm.utils import run_cmd, edit, prompt, validate_input, get_host_ip

import os
import sys
import json
import shutil
import webbrowser
import urllib.request
from argparse import Namespace
from typing import List, Dict, Set, Callable
from socket import gethostbyname, gethostname
from pathlib import Path
from pathlib import PosixPath
from pip._internal.operations.freeze import freeze

# this global will get removed after a few minor versions
__version__ = 4.0

logger = MMPMLogger.get_logger(__name__)


class MMPM(Singleton):
    def __init__(self):
        self.env = MMPMEnv()
        self.database = MagicMirrorDatabase()
        self.controller = MagicMirrorController()
        self.magicmirror: MagicMirror = MagicMirror()
        self.gui = MMPMGui()

    def run(self):
        """Main entry point for CLI"""
        parser = options.setup()

        if len(sys.argv) < 2:
            parser.print_help()
            sys.exit(127)

        args, additional_args = parser.parse_known_args()

        if args.subcmd is None:
            logger.msg.fatal("Invalid argument. See 'mmpm --help'")
            sys.exit(127)

        command: str = f'cmd_{args.subcmd.lower().replace("-", "_")}'

        if command != "cmd_version":
            should_refresh = True if args.subcmd == "db" and args.refresh else self.database.is_expired()
            self.database.load(refresh=should_refresh)

            if self.database.is_expired() and args.subcmd != mmpm.opts.UPDATE:
                self.database.update()

        if hasattr(self, command):
            getattr(self, command)(args, additional_args)


    def cmd_version(self, args, additional_args=None):
        print(f"{mmpm_version}")


    def cmd_list(self, args, additional_args=None):
        if args.installed:
            for package in self.database.packages:
                if package.is_installed:
                    package.display(title_only=args.title_only, show_path=True, hide_installed_indicator=True)

        elif args.all or args.exclude_installed:
            for package in self.database.packages:
                package.display(title_only=args.title_only, exclude_installed=args.exclude_installed)

        elif args.categories:
            self.database.display_categories(title_only=args.title_only)
        elif args.gui_url:
            print(self.gui.get_uri())
        elif args.upgradable:
            self.database.display_upgradable()
        else:
            logger.msg.no_args(args.subcmd)


    def cmd_show(self, args, additional_args=None):
        if not additional_args:
            logger.msg.no_args(args.subcmd)

        if args.remote:
            health = RemotePackage.health()

            for status in health.values():
                if status['error']:
                    logger.msg.fatal(status['error'])
                elif status['warning']:
                    logger.msg.warning(status['warning'])

        for query in additional_args:
            for package in self.database.search(query, by_title_only=True):
                package.display(remote=args.remote, detailed=True)


    def cmd_search(self, args, additional_args=None):
        if not additional_args:
            logger.msg.no_args(args.subcmd)
            return

        if len(additional_args) > 1:
            logger.msg.fatal(f"Too many arguments. `mmpm {args.subcmd}` only accepts one search argument")
            return

        query_result = self.database.search(additional_args[0], case_sensitive=args.case_sensitive)

        for package in query_result:
            package.display(title_only=args.title_only)


    def cmd_mm_ctl(self, args, additional_args=None):
        if additional_args:
            logger.msg.extra_args(args.subcmd)
        elif args.status:
            self.controller.status()
        elif args.hide:
            self.controller.hide_modules(args.hide)
        elif args.show:
            self.controller.show_modules(args.show)
        elif args.start:
            if self.env.mmpm_is_docker_image.get():
                logger.msg.fatal("Cannot execute this command within a docker image")
            else:
                self.controller.start()
        elif args.stop:
            if self.env.mmpm_is_docker_image.get():
                logger.msg.fatal("Cannot execute this command within a docker image")
            else:
                self.controller.stop()
        elif args.restart:
            if self.env.mmpm_is_docker_image.get():
                logger.msg.fatal("Cannot execute this command within a docker image")
            else:
                self.controller.restart()
        else:
            logger.msg.no_args(args.subcmd)


    def cmd_log(self, args, additional_args=None):
        if additional_args:
            logger.msg.extra_args(args.subcmd)
        elif args.zip:
            MMPMLogger.zip()
        elif not args.cli and not args.gui:
            # if the user doesn't provide arguments, just display everything, but consider the --tail arg
            MMPMLogger.display(True, True, args.tail)
        else:
            MMPMLogger.display(args.cli, args.gui, args.tail)


    def cmd_db(self, args, additional_args=None):
        if args.refresh:
            sys.exit(0)
        if additional_args:
            logger.msg.extra_args(args.subcmd)
        elif args.info:
            self.database.info()
        elif args.dump:
            self.database.dump()
        else:
            logger.msg.no_args(args.subcmd)


    def cmd_env(self, args, additional_args=None):
        if additional_args:
            logger.msg.extra_args(args.subcmd)
            return

        self.env.display()
        print("Run `mmpm open --env` to edit the variable values")


    def cmd_update(self, args, additional_args=None):
        if additional_args:
            logger.msg.extra_args(args.subcmd)

        url = "https://pypi.org/pypi/mmpm/json"
        logger.msg.retrieving("https://pypi.org/pypi/mmpm", "mmpm")
        current_version = ""

        for requirement in freeze(local_only=False):
            info = requirement.split("==")

            if info[0] == "mmpm":
                current_version = info[1]

        contents = urllib.request.urlopen(url).read()
        latest_version = json.loads(contents)["info"]["version"]

        can_upgrade_mmpm = latest_version == current_version
        can_upgrade_magicmirror = self.magicmirror.update()

        available_upgrades = self.database.update(
            can_upgrade_mmpm=can_upgrade_mmpm,
            can_upgrade_magicmirror=can_upgrade_magicmirror
        )

        if not available_upgrades:
            print("All packages and applications are up to date.")
            return

        print(f"{available_upgrades} upgrade(s) available. Run `mmpm list --upgradable` for details")


    def cmd_upgrade(self, args, additional_args=None):
        upgradable = self.database.upgradable()

        if not upgradable["mmpm"] and not upgradable["MagicMirror"] and not upgradable["packages"]:
            logger.msg.info("All packages and applications are up to date.\n ")

        if upgradable["packages"]:
            packages: Set[MagicMirrorPackage] = {MagicMirrorPackage(**package) for package in upgradable["packages"]}
            upgraded: Set[MagicMirrorPackage] = {package for package in packages if package.upgrade()}

            # whichever packages failed to upgrade, we'll hold onto those for future reference
            upgradable["packages"] = [package.serialize() for package in (packages - upgraded)]

        if upgradable["MagicMirror"]:
            upgradable["MagicMirror"] = not self.magicmirror.upgrade()

        if upgradable["mmpm"]:
            print("Run 'pip install --upgrade --no-cache-dir mmpm' to install the latest version of MMPM. Run 'mmpm update' after upgrading.")

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="w", encoding="utf-8") as upgrade_file:
            json.dump(upgradable, upgrade_file)


    def cmd_install(self, args, additional_args=None):
        if not additional_args:
            logger.msg.no_args(args.subcmd)
            return

        results: List[MagicMirrorPackage] = []

        for name in additional_args:
            if name == "MagicMirror":
                self.magicmirror.install()
            elif name == "mmpm-gui":
                self.gui.install(args.assume_yes)
            else:
                results.extend(filter(lambda pkg : name == pkg.title, self.database.packages))

                if not results:
                    logger.msg.error("Unable to locate package(s) based on query.")

        for package in results:
            package.install(assume_yes=args.assume_yes)


    def cmd_remove(self, args, additional_args=None):
        if not additional_args:
            logger.msg.no_args(args.subcmd)
            return

        for name in additional_args:
            if name == "MagicMirror":
                self.magicmirror.remove()
            elif name == "mmpm-gui":
                self.gui.remove(args.assume_yes)
            else:
                for package in filter(lambda pkg : name == pkg.title, self.database.packages):
                    package.remove(assume_yes=args.assume_yes)


    def cmd_open(self, args, additional_args=None):
        if additional_args:
            logger.msg.extra_args(args.subcmd)
        elif args.config:
            root = self.env.mmpm_magicmirror_root.get() / "config"
            config_js = root / "config.js"
            config_js_sample = root / "config.js.sample"

            if not config_js.stat().st_size and config_js_sample.exists():
                shutil.copyfile(config_js_sample, config_js)

            edit(config_js)

        elif args.custom_css:
            edit(self.env.mmpm_magicmirror_root.get() / "css" / "custom.css")
        elif args.magicmirror:
            run_cmd(["xdg-open", self.env.mmpm_magicmirror_uri.get()], background=True)
        elif args.gui:
            run_cmd(["xdg-open", self.gui.get_uri()], background=True)
        elif args.mm_wiki:
            run_cmd(["xdg-open", urls.MAGICMIRROR_WIKI_URL], background=True)
        elif args.mm_docs:
            run_cmd(["xdg-open", urls.MAGICMIRROR_DOCUMENTATION_URL], background=True)
        elif args.mmpm_wiki:
            run_cmd(["xdg-open", urls.MMPM_WIKI_URL], background=True)
        elif args.mmpm_env:
            edit(paths.MMPM_ENV_FILE)
        else:
            logger.msg.no_args(args.subcmd)


    def cmd_add_mm_pkg(self, args, additional_args=None):
        if args.remove:
            self.database.remove_mm_pkg(args.remove, assume_yes=args.assume_yes)
        else:
            self.database.add_mm_pkg(args.title, args.author, args.repo, args.desc)


    def cmd_completion(self, args, additional_args=None):
        """
        Adds autocompletion configuration to a user's shell configuration file.
        Detects configuration files for bash, zsh, fish, and tcsh

        Parameters:
            assume_yes (bool): if True, assume yes for user response, and do not display prompt

        Returns:
            None
        """

        if args.assume_yes and not prompt("Are you sure you want to install the autocompletion feature for the MMPM CLI?"):
            logger.info("User cancelled installation of autocompletion for MMPM CLI")
            return

        logger.info("User attempting to install MMPM autocompletion")
        shell: str = str(Path(os.environ["SHELL"]).stem).lower()
        logger.info(f"Detected user shell to be {shell}")

        autocomplete_url = "https://github.com/kislyuk/argcomplete#activating-global-completion"
        error_message = f"Please see {autocomplete_url} for help installing autocompletion"

        complete_message = lambda config: f"Autocompletion installed. Please source {config} for the changes to take effect"
        failed_match_message = lambda sh, configs: f"Unable to locate {sh} configuration file (looked for {configs}). {error_message}"

        def match_shell_config(shell_profiles):
            logger.info(f"Searching for one of the following shell configuration files {shell_profiles}")

            for shell_profile in shell_profiles:
                file: PosixPath = paths.HOME_DIR / shell_profile

                if file.exists():
                    logger.info(f"Found {file} shell configuration file for {shell}")
                    return file

            return None

        def cmd(command: str):
            logger.info(f"Executing {command} to install autocompletion")
            os.system(command)

        shell_configs = {
                "bash": {
                    "files": [".bashrc", ".bash_profile", ".bash_login", ".profile"],
                    "commands": [
                        "echo 'eval \"$(register-python-argcomplete mmpm)\"' >> {config}"
                        ],
                    },
                "zsh": {
                    "files": [".zshrc", ".zprofile", ".zshenv", ".zlogin", ".profile"],
                    "commands": [
                        "echo 'autoload -U bashcompinit' >> {config}",
                        "echo 'bashcompinit' >> {config}",
                        "echo 'eval \"$(register-python-argcomplete mmpm)\"' >> {config}",
                        ],
                    },
                "tcsh": {
                    "files": [".tcshrc", ".cshrc", ".login"],
                    "commands": [
                        "echo 'eval `register-python-argcomplete --shell tcsh mmpm`' >> {config}"
                        ],
                    },
                "fish": {
                    "files": [".config/fish/config.fish"],
                    "commands": [
                        "register-python-argcomplete --shell fish mmpm >> {config}"
                        ],
                    },
                }

        if shell in shell_configs:
            config_info = shell_configs[shell]
            commands = config_info["commands"]
            file = match_shell_config(config_info["files"])
            logger.msg.info(f"Detected '{shell}' shell.\n")

            if file is None:
                logger.msg.fatal(failed_match_message(shell, config_info["files"]))

            for command in commands:
                cmd(command.format(config=file))

            print(complete_message(file))
        else:
            logger.msg.fatal( f"Unable to install autocompletion for ({shell}). Please see {autocomplete_url} for help installing autocompletion")


    def cmd_guided_setup(self, args, additional_args=None):
        """
        Provides the user a guided configuration of the environment variables, and
        feature installation. This can be re-run as many times as necessary.

        Parameters:
            None

        Returns:
            None
        """
        print(color.b_green("Welcome to MMPM's guided setup!\n"))
        print("I'll help you setup your environment variables and additional features. Let's get started!\n")

        magicmirror_root: str = f"{Path.home()}/MagicMirror"
        magicmirror_uri: str = f"http://{get_host_ip()}:8080"
        magicmirror_pm2_proc: str = ""
        magicmirror_docker_compose_file: str = ""
        mmpm_is_docker_image: bool = False
        install_gui: bool = False
        install_autocomplete: bool = False
        install_as_module: bool = False

        magicmirror_root = validate_input(f"What is the absolute path to your MagicMirror installation (ie. {Path.home()}/MagicMirror)?")
        mmpm_is_docker_image = prompt("Is MMPM running as a Docker image?")

        if not mmpm_is_docker_image and prompt("Did you install MagicMirror using docker-compose?"):
            magicmirror_docker_compose_file = validate_input(f"What is the absolute path to the MagicMirror docker-compose file (ie. {Path.home()}/docker-compose.yml)?")

        if not mmpm_is_docker_image and not magicmirror_docker_compose_file and prompt("Are you using PM2 to start/stop MagicMirror?"):
            magicmirror_pm2_proc = validate_input( "What is the name of the PM2 process for MagicMirror?")

        if not prompt(f"Is {magicmirror_uri} the address used to open MagicMirror in your browser?"):
            magicmirror_uri = validate_input("Enter the address and port used to access MagicMirror:")

        install_gui = not mmpm_is_docker_image and prompt("Would you like to install the MMPM GUI (web interface)?")
        install_as_module = prompt("Would you like to hide/show MagicMirror modules through MMPM?")
        install_autocomplete = prompt("Would you like to install tab-autocomplete for the MMPM CLI?")

        with open(paths.MMPM_ENV_FILE, "w", encoding="utf-8") as env:
            json.dump(
                {
                    self.env.mmpm_magicmirror_root.name: os.path.normpath(magicmirror_root),
                    self.env.mmpm_magicmirror_uri.name: magicmirror_uri,
                    self.env.mmpm_magicmirror_pm2_process_name.name: magicmirror_pm2_proc,
                    self.env.mmpm_magicmirror_docker_compose_file.name: os.path.normpath(magicmirror_docker_compose_file),
                    self.env.mmpm_is_docker_image.name: mmpm_is_docker_image,
                },
                env,
                indent=2,
            )

        message = "Based on your responses, your environment variables have been set as:"
        line_break = color.b_green("-" * len(message))

        print("\n" + line_break)
        print("\nBased on your responses, your environment variables have been set as:")
        self.env.display()

        print("Execute the following commands to install the desired features:")

        if install_as_module:
            print(color.b_green("mmpm install MMM-mmpm"))
        if install_gui:
            print(color.b_green("mmpm install --gui"))
        if install_autocomplete:
            print(color.b_green("mmpm completion"))

        print()
