#!/usr/bin/env python3
import os
import sys
import json
import shutil
import pathlib
import subprocess
import datetime
import requests
import mmpm.color
import mmpm.utils
import mmpm.consts
import getpass
import mmpm.mmpm
from mmpm.logger import MMPMLogger
from re import findall
from pathlib import Path, PosixPath
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.env import MMPMEnv
from mmpm.gui import MMPMGui
from bs4 import NavigableString, Tag, BeautifulSoup
from collections import defaultdict
from socket import gethostname, gethostbyname
from typing import List, Dict, Callable
from textwrap import fill, indent

logger = MMPMLogger.get_logger(__name__)

# TODO: delete this whole file


def check_for_mmpm_updates(automated=False) -> bool:
    '''
    Scrapes the main file of MMPM off the github repo, and compares the current
    version, versus the one available in the master branch. If there is a newer
    version, the user is prompted for an upgrade.

    Parameters:
        automated (bool): if True, an extra notification is printed to the screen for the user to see

    Returns:
        bool: True on success, False on failure
    '''

    cyan_application: str = f"{mmpm.color.normal_cyan('application')}"
    logger.info(f'Checking for newer version of MMPM. Current version: {mmpm.mmpm.__version__}')

    if automated:
        message: str = f"Checking {mmpm.color.normal_green('MMPM')} [{cyan_application}] ({mmpm.color.normal_magenta('automated')}) for updates"
    else:
        message = f"Checking {mmpm.color.normal_green('MMPM')} [{cyan_application}] for updates"

    logger.msg.info(message)

    try:
        # just to keep the console output the same as all other update commands
        error_code, contents, _ = mmpm.utils.run_cmd(['curl', mmpm.consts.MMPM_FILE_URL])
    except KeyboardInterrupt:
        logger.info("User killed process with CTRL-C")
        sys.exit(127)

    if error_code:
        logger.msg.fatal('Failed to retrieve MMPM version number')

    version_number: float = float(findall(r"\d+\.\d+", findall(r"__version__ = \d+\.\d+", contents)[0])[0])
    print(mmpm.consts.GREEN_CHECK_MARK)

    if not version_number:
        logger.msg.fatal('No version number found on MMPM repository')

    can_upgrade: bool = version_number > mmpm.mmpm.__version__

    if can_upgrade:
        logger.info(f'Found newer version of MMPM: {version_number}')
    else:
        logger.info(f'No newer version of MMPM found > {version_number} available. The current version is the latest')

    upgrades = get_available_upgrades()

    with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w', encoding="utf-8") as available_upgrades:
        upgrades[mmpm.consts.MMPM] = can_upgrade
        json.dump(upgrades, available_upgrades, default=lambda pkg: pkg.serialize())

    return can_upgrade


def upgrade_available_packages_and_applications(assume_yes: bool = False, selection: List[str] = []) -> None:
    '''
    Wrapper method to handle upgrade process of all available packages and/or
    applications (MMPM and MagicMirror). A user may supply specific
    packages/applications to upgrade, or upgrade all available by supplying no
    arguments. No result is returned. All sub-functions responsible for
    upgrading packages handle errors, and the execution does not need to halt
    do to errors in this wrapper method

    Parameters:
        assume_yes (bool): if True, the user prompt is skipped
        selection (List[str]): the specific list of packaes/application names provided by the user. This is optional

    Returns:
        None
    '''
    confirmed: dict = {mmpm.consts.PACKAGES: [], mmpm.consts.MMPM: False, mmpm.consts.MAGICMIRROR: False}
    MMPM_MAGICMIRROR_ROOT: str = os.path.normpath(MMPMEnv.mmpm_magicmirror_root.get())
    upgrades = get_available_upgrades()
    upgraded: bool = False

    has_upgrades: bool = False
    mmpm_selected: bool = False
    magicmirror_selected: bool = False
    user_selections: bool = bool(selection)

    for key in upgrades[MMPM_MAGICMIRROR_ROOT]:
        if upgrades[MMPM_MAGICMIRROR_ROOT][key]:
            has_upgrades = True
            break

    if not has_upgrades and not upgrades[mmpm.consts.MMPM]:
        print(f'No upgrades available {mmpm.consts.YELLOW_X}')

    if mmpm.consts.MMPM in selection and upgrades[mmpm.consts.MMPM]:
        mmpm_selected = True
        selection.remove(mmpm.consts.MMPM)

    if upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES]:
        if selection:
            print(selection)
            valid_pkgs: List[MagicMirrorPackage] = [pkg for pkg in upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES] if pkg.title in selection]

            for pkg in upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES]:
                if pkg.title in selection:
                    valid_pkgs.append(pkg)
                    selection.remove(pkg.title)

            if mmpm.consts.MAGICMIRROR in selection and upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.MAGICMIRROR]:
                magicmirror_selected = True
                selection.remove(mmpm.consts.MAGICMIRROR)

            if selection: # the left overs that weren't matched
                logger.msg.error(f'Unable to match {selection} to a package/application with available upgrades')

            for package in valid_pkgs:
                if package.title in selection and mmpm.utils.prompt(f'Upgrade {mmpm.color.normal_green(package.title)} ({package.repository}) now?', assume_yes=assume_yes):
                    confirmed[mmpm.consts.PACKAGES].append(package)
        else:
            for package in upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES]:
                if mmpm.utils.prompt(f'Upgrade {mmpm.color.normal_green(package.title)} ({package.repository}) now?', assume_yes=assume_yes):
                    confirmed[mmpm.consts.PACKAGES].append(package)

    if upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.MAGICMIRROR] and (magicmirror_selected or not user_selections):
        confirmed[mmpm.consts.MAGICMIRROR] = mmpm.utils.prompt(f"Upgrade {mmpm.color.normal_green('MagicMirror')} now?", assume_yes=assume_yes)

    if upgrades[mmpm.consts.MMPM] and (mmpm_selected or not user_selections):
        if MMPMEnv.mmpm_is_docker_image.get():
            logger.msg.error('Sorry, MMPM you will have upgrade MMPM by retrieving the latest Docker image when it is ready')
        else:
            logger.msg.warning('Please upgrade MMPM using `pip3 install --user --upgrade mmpm`, followed by `mmpm install --gui`')

    for pkg in confirmed[mmpm.consts.PACKAGES]:
        error = pkg.upgrade()

        if error:
            logger.msg.error(error)
            continue

        upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES].remove(pkg)
        upgraded = True

    if confirmed[mmpm.consts.MAGICMIRROR]:
        error = upgrade_magicmirror()

        if error:
            logger.msg.error(error)
        else:
            upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.MAGICMIRROR] = False
            upgraded = True

    upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES] = [pkg.serialize_full() for pkg in upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES]]

    with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w', encoding="utf-8") as available_upgrades:
        json.dump(upgrades, available_upgrades, default=lambda pkg: pkg.serialize())

    if upgraded and mmpm.utils.is_magicmirror_running():
        print('Restart MagicMirror for the changes to take effect')





def load_external_packages() -> Dict[str, List[MagicMirrorPackage]]:
    '''
    Extracts the external packages from the JSON files stored in
    ~/.config/mmpm/mmpm-external-packages.json

    If no data is found, an empty dictionary is returned

    Parameters:
        None

    Returns:
        external_packages (Dict[str, List[MagicMirrorPackage]]): the list of manually added MagicMirror packages
    '''
    external_packages: List[MagicMirrorPackage] = []

    if bool(os.stat(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE).st_size):
        try:
            with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'r', encoding="utf-8") as ext_pkgs:
                external_packages = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(json.load(ext_pkgs)[mmpm.consts.EXTERNAL_PACKAGES])
        except Exception:
            message = f'Failed to load data from {mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE}. Please examine the file, as it may be malformed and required manual corrective action.'
            mmpm.utils.warning_msg(message)
    else:
        with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, mode= 'w', encoding="utf-8") as ext_pkgs:
            json.dump({mmpm.consts.EXTERNAL_PACKAGES: external_packages}, ext_pkgs)

    return {mmpm.consts.EXTERNAL_PACKAGES: external_packages}



def install_autocompletion(assume_yes: bool = False) -> None:
    '''
    Adds autocompletion configuration to a user's shell configuration file.
    Detects configuration files for bash, zsh, fish, and tcsh

    Parameters:
        assume_yes (bool): if True, assume yes for user response, and do not display prompt

    Returns:
        None
    '''

    if not mmpm.utils.prompt('Are you sure you want to install the autocompletion feature for the MMPM CLI?', assume_yes=assume_yes):
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

    def __echo_and_eval__(command: str) -> None:
        logger.info(f'executing {command} to install autocompletion')
        print(f'{command}')
        os.system(command)

    if 'bash' in shell:
        files = ['.bashrc', '.bash_profile', '.bash_login', '.profile']
        config = __match_shell_config__(files)

        if not config:
            logger.msg.fatal(failed_match_message('bash', files))

        __echo_and_eval__(f'echo \'eval "$(register-python-argcomplete mmpm)"\' >> {config}')

        print(complete_message(config))

    elif 'zsh' in shell:
        files = ['.zshrc', '.zprofile', '.zshenv', '.zlogin', '.profile']
        config = __match_shell_config__(files)

        if not config:
            logger.msg.fatal(failed_match_message('zsh', files))

        __echo_and_eval__(f"echo 'autoload -U bashcompinit' >> {config}")
        __echo_and_eval__(f"echo 'bashcompinit' >> {config}")
        __echo_and_eval__(f'echo \'eval "$(register-python-argcomplete mmpm)"\' >> {config}')

        print(complete_message(config))

    elif 'tcsh' in shell:
        files = ['.tcshrc', '.cshrc', '.login']
        config = __match_shell_config__(files)

        if not config:
            logger.msg.fatal(failed_match_message('tcsh', files))

        __echo_and_eval__(f"echo 'eval `register-python-argcomplete --shell tcsh mmpm`' >> {config}")

        print(complete_message(config))

    elif 'fish' in shell:
        files = ['.config/fish/config.fish']
        config = __match_shell_config__(files)

        if not config:
            logger.msg.fatal(failed_match_message('fish', files))

        __echo_and_eval__(f"register-python-argcomplete --shell fish mmpm >> {config}")

        print(complete_message(config))

    else:
        logger.msg.fatal(f'Unable install autocompletion for ({shell}). Please see {autocomplete_url} for help installing autocomplete')



