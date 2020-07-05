#!/usr/bin/env python3
import re
import os
import pathlib
import json
import datetime
import shutil
import sys
import requests

from socket import gethostname, gethostbyname
from textwrap import fill, indent
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from collections import defaultdict
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple

import mmpm.color
import mmpm.utils
import mmpm.consts
import mmpm.models


MagicMirrorPackage = mmpm.models.MagicMirrorPackage


def snapshot_details(packages: Dict[str, List[MagicMirrorPackage]]) -> None:
    '''
    Displays information regarding the most recent 'snapshot_file', ie. when it
    was taken, when the next scheduled snapshot will be taken, how many module
    categories exist, and the total number of modules available. Additionally,
    tells user how to forcibly request a new snapshot be taken.

    Parameters:
        packages (Dict[str, List[MagicMirrorPackage]]): Dictionary of MagicMirror modules

    Returns:
        None
    '''

    num_categories: int = len(packages.keys())
    num_packages: int = 0

    current_snapshot, next_snapshot = mmpm.utils.calc_snapshot_timestamps()
    curr_snap_date = datetime.datetime.fromtimestamp(int(current_snapshot))
    next_snap_date = datetime.datetime.fromtimestamp(int(next_snapshot))

    for category in packages.values():
        num_packages += len(category)

    print(mmpm.color.normal_green('Last updated:'), f'{curr_snap_date}')
    print(mmpm.color.normal_green('Next scheduled update:'), f'{next_snap_date}')
    print(mmpm.color.normal_green('Package categories:'), f'{num_categories}')
    print(mmpm.color.normal_green('Packages available:'), f'{num_packages}')


def check_for_mmpm_updates(assume_yes=False, gui=False) -> bool:
    '''
    Scrapes the main file of MMPM off the github repo, and compares the current
    version, versus the one available in the master branch. If there is a newer
    version, the user is prompted for an upgrade.

    Parameters:
        None

    Returns:
        bool: True on success, False on failure
    '''
    import mmpm.mmpm

    try:
        cyan_application: str = f"{mmpm.color.normal_cyan('application')}"
        mmpm.utils.log.info(f'Checking for newer version of MMPM. Current version: {mmpm.mmpm.__version__}')
        mmpm.utils.plain_print(f"Checking {mmpm.color.normal_green('MMPM')} [{cyan_application}] for updates")

        try:
            # just to keep the console output the same as all other update commands
            error_code, contents, _ = mmpm.utils.run_cmd(['curl', mmpm.consts.MMPM_FILE_URL])
        except KeyboardInterrupt:
            mmpm.utils.keyboard_interrupt_log()

        if error_code:
            mmpm.utils.fatal_msg('Failed to retrieve MMPM version number')

    except (HTTPError, URLError) as error:
        print(mmpm.consts.RED_X)
        mmpm.utils.error_msg(str(error))
        return False

    version_number: float = float(re.findall(r"\d+\.\d+", re.findall(r"__version__ = \d+\.\d+", contents)[0])[0])
    print(mmpm.consts.GREEN_CHECK_MARK)

    if not version_number:
        mmpm.utils.fatal_msg('No version number found on MMPM repository')

    if mmpm.mmpm.__version__ >= version_number:
        mmpm.utils.log.info(f'No newer version of MMPM found > {version_number} available. The current version is the latest')
        return False

    mmpm.utils.log.info(f'Found newer version of MMPM: {version_number}')
    env: str = mmpm.consts.MMPM_MAGICMIRROR_ROOT
    upgrades, _ = get_available_upgrades()

    with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w') as available_upgrades:
        upgrades[mmpm.consts.MMPM] = True
        json.dump(upgrades, available_upgrades)

    if gui:
        mmpm.utils.log.info('A newer version of MMPM was detected via the GUI')
        print(f"A newer version of MMPM is available ({version_number}). Please upgrade via terminal using 'mmpm uprade --mmpm")
        return True

    return True


def upgrade_mmpm(assume_yes: bool = False) -> bool:

    mmpm.utils.log.info(f'User chose to update MMPM')

    print(f"{mmpm.consts.GREEN_DASHES} Upgrading {mmpm.color.normal_green('MMPM')}")
    os.system('rm -rf /tmp/mmpm')
    os.chdir(os.path.join('/', 'tmp'))

    error_code, _, stderr = mmpm.utils.clone('mmpm', mmpm.consts.MMPM_REPO_URL)

    if error_code:
        mmpm.utils.error_msg(stderr)
        return False

    os.chdir('/tmp/mmpm')

    # if the user needs to be prompted for their password, this can't be a subprocess
    os.system('make reinstall')
    return True


def upgrade_package(package: MagicMirrorPackage, assume_yes: bool = False) -> str:
    '''
    Depending on flags passed in as arguments:

    Checks for available package updates, and alerts the user. Or, pulls latest
    version of module(s) from the associated repos.

    If upgrading, a user can upgrade all modules that have available upgrades
    by ommitting additional arguments. Or, upgrade specific modules by
    supplying their case-sensitive name(s) as an addtional argument.

    Parameters:
        package (MagicMirrorPackage): the MagicMirror module being upgraded

    Returns:
        stderr (str): the resulting error message of the upgrade. If the message is zero length, it was successful
    '''

    os.chdir(package.directory)

    mmpm.utils.plain_print(f'{mmpm.consts.GREEN_DASHES} Performing upgrade for {mmpm.color.normal_green(package.title)}')
    error_code, _, stderr = mmpm.utils.run_cmd(["git", "pull"])

    if error_code:
        mmpm.utils.error_msg(f'Failed to upgrade MagicMirror {mmpm.consts.RED_X}')
        mmpm.utils.error_msg(stderr)
        return stderr

    else:
        print(mmpm.consts.GREEN_CHECK_MARK)

    stderr = mmpm.utils.install_dependencies(package.directory)

    if stderr:
        print(mmpm.consts.RED_X)
        mmpm.utils.error_msg(stderr)
        return stderr

    return ''


def upgrade_available(assume_yes: bool = False, selection: List[str] = []) -> bool:
    confirmed: dict = {mmpm.consts.PACKAGES: [], mmpm.consts.MMPM: False, mmpm.consts.MAGICMIRROR: False}
    env: str = mmpm.consts.MMPM_MAGICMIRROR_ROOT
    upgrades = get_available_upgrades()
    upgraded: bool = False

    has_upgrades: bool = False

    for key in upgrades[env].keys():
        if upgrades[env][key]:
            has_upgrades = True
            break

    if not has_upgrades and not upgrades[mmpm.consts.MMPM]:
        print(f'No upgrades available {mmpm.consts.YELLOW_X}')

    if upgrades[env][mmpm.consts.PACKAGES]:
        if selection:
            valid_pkgs: List[MagicMirrorPackage] = [pkg for pkg in upgrades[env][mmpm.consts.PACKAGES] if pkg.title in selection]

            if not valid_pkgs and not mmpm.consts.MMPM in selection or not mmpm.consts.MAGICMIRROR not in selection:
                mmpm.utils.error_msg(f'Unable to match {selection} to a package/application with available upgrades')

            for package in valid_pkgs:
                if package.title in selection and mmpm.utils.prompt_user(f'Upgrade {mmpm.color.normal_green(package.title)} ({package.repository}) now?', assume_yes=assume_yes):
                    confirmed[mmpm.consts.PACKAGES].append(package)
        else:
            for package in upgrades[env][mmpm.consts.PACKAGES]:
                if mmpm.utils.prompt_user(f'Upgrade {mmpm.color.normal_green(package.title)} ({package.repository}) now?', assume_yes=assume_yes):
                    confirmed[mmpm.consts.PACKAGES].append(package)

    if mmpm.consts.MAGICMIRROR in selection or not selection and upgrades[env][mmpm.consts.MAGICMIRROR]:
        confirmed[mmpm.consts.MAGICMIRROR] = mmpm.utils.prompt_user(f"Upgrade {mmpm.color.normal_green('MagicMirror')} now?", assume_yes=assume_yes)

    if mmpm.consts.MMPM in selection or not selection and upgrades[mmpm.consts.MMPM]:
        confirmed[mmpm.consts.MMPM] = mmpm.utils.prompt_user(f"Upgrade {mmpm.color.normal_green('MMPM')} now?", assume_yes=assume_yes)

    for pkg in confirmed[mmpm.consts.PACKAGES]:
        error = upgrade_package(pkg)

        if error:
            mmpm.utils.error_msg(error)
            continue

        upgrades[env][mmpm.consts.PACKAGES].remove(pkg)
        upgraded = True

    warning: str = 'The above error requires user correction. Please fix this, and re-run `mmpm update` to sync the database'

    if confirmed[mmpm.consts.MMPM]:
        if not upgrade_mmpm():
            mmpm.utils.warning_msg(warning)
        else:
            upgrades[mmpm.consts.MMPM] = False
            upgraded = True

    if confirmed[mmpm.consts.MAGICMIRROR]:
        if not upgrade_magicmirror():
            mmpm.utils.warning_msg(warning)
        else:
            upgrades[env][mmpm.consts.MAGICMIRROR] = False
            upgraded = True

    upgrades[env][mmpm.consts.PACKAGES] = [pkg.serialize_full() for pkg in upgrades[env][mmpm.consts.PACKAGES]]

    with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w') as available_upgrades:
        json.dump(upgrades, available_upgrades)

    if upgraded and mmpm.utils.is_magicmirror_running():
        print('Restart MagicMirror for the changes to take effect')

    return True


def check_for_package_updates(packages: Dict[str, List[MagicMirrorPackage]]) -> List[MagicMirrorPackage]:
    '''
    Depending on flags passed in as arguments:

    Checks for available module updates, and alerts the user. Or, pulls latest
    version of module(s) from the associated repos.

    If upgrading, a user can upgrade all modules that have available upgrades
    by ommitting additional arguments. Or, upgrade specific modules by
    supplying their case-sensitive name(s) as an addtional argument.

    Parameters:
        packages (Dict[str, List[MagicMirrorPackage]]): Dictionary of MagicMirror modules
        assume_yes (bool): if True, assume yes for user response, and do not display prompt

    Returns:
        None
    '''

    os.chdir(mmpm.consts.MAGICMIRROR_MODULES_DIR)
    installed_packages: Dict[str, List[MagicMirrorPackage]] = get_installed_packages(packages)
    any_installed: bool = False

    for category in installed_packages.keys():
        if installed_packages[category]:
            any_installed = True
            break

    if not any_installed:
        mmpm.utils.fatal_msg('No packages installed')

    upgradeable: List[MagicMirrorPackage] = []
    upgraded: bool = True
    cyan_package: str = f"{mmpm.color.normal_cyan('package')}"

    for _, _packages in installed_packages.items():
        for package in _packages:
            os.chdir(package.directory)

            mmpm.utils.plain_print(f'Checking {mmpm.color.normal_green(package.title)} [{cyan_package}] for updates')

            try:
                error_code, _, stdout = mmpm.utils.run_cmd(['git', 'fetch', '--dry-run'])

            except KeyboardInterrupt:
                print(mmpm.consts.RED_X)
                mmpm.utils.keyboard_interrupt_log()

            if error_code:
                print(mmpm.consts.RED_X)
                mmpm.utils.error_msg('Unable to communicate with git server')
                continue

            if stdout:
                upgradeable.append(package)

            print(mmpm.consts.GREEN_CHECK_MARK)

    upgrades: dict = {}
    env: str = mmpm.consts.MMPM_MAGICMIRROR_ROOT

    upgrades = get_available_upgrades()

    with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w') as available_upgrades:
        if env not in upgrades:
            upgrades[env] = {mmpm.consts.PACKAGES: [], mmpm.consts.MAGICMIRROR: False}

        upgrades[env][mmpm.consts.PACKAGES] = [pkg.serialize_full() for pkg in upgradeable]
        json.dump(upgrades, available_upgrades)

    return upgradeable


def search_packages(packages: Dict[str, List[MagicMirrorPackage]], query: str, case_sensitive: bool = False, by_title_only: bool = False) -> dict:
    '''
    Used to search the 'modules' for either a category, or keyword/phrase
    appearing within module descriptions. If the argument supplied is a
    category name, all modules from that category will be listed. Otherwise,
    all modules whose descriptions contain the keyword/phrase will be
    displayed.

    Parameters:
        packages (Dict[str, List[MagicMirrorPackage]]): Dictionary of MagicMirror modules
        query (str): user provided search string
        case_sensitive (bool): if True, the query's exact casing is used in search
        by_title_only (bool): if True, only the title is considered when matching packages to query

    Returns:
        dict
    '''

    # if the query matches one of the category names exactly, return everything in that category
    if query in packages:
        return {query: packages[query]}

    search_results: Dict[str, List[MagicMirrorPackage]] = defaultdict(list)

    if by_title_only:
        match = lambda query, pkg: query == pkg.title
    elif case_sensitive:
        match = lambda query, pkg: query in pkg.description or query in pkg.title or query in pkg.author
    else:
        query = query.lower()
        match = lambda query, pkg: query in pkg.description.lower() or query in pkg.title.lower() or query in pkg.author.lower()

    for category, _packages in packages.items():
        search_results[category] = [package for package in _packages if match(query, package)]

    return search_results


def show_package_details(packages: Dict[str, List[MagicMirrorPackage]], verbose: bool) -> None:
    '''
    Displays more detailed information that presented in normal search results.
    The output is formatted similarly to the output of the Debian/Ubunut 'apt' CLI

    Parameters:
        packages (List[defaultdict]): List of Categorized MagicMirror packages

    Returns:
        None
    '''

    def __show_package__(category: str, package: MagicMirrorPackage) -> None:
        print(mmpm.color.normal_green(package.title))
        print(f'  Category: {category}')
        print(f'  Repository: {package.repository}')
        print(f'  Author: {package.author}')

    if not verbose:
        def __show_details__(packages: dict) -> None:
            for category, _packages  in packages.items():
                for package in _packages:
                    __show_package__(category, package)
                    print(indent(fill(f'Description: {package.description}\n', width=80), prefix='  '),'\n')

    else:
        def __show_details__(packages: dict) -> None:
            for category, _packages  in packages.items():
                for package in _packages:
                    __show_package__(category, package)
                    for key, value in mmpm.utils.get_remote_package_details(package).items():
                        print(f"  {key}: {value}")
                    print(indent(fill(f'Description: {package.description}\n', width=80), prefix='  '),'\n')

    __show_details__(packages)


def get_installation_candidates(packages: Dict[str, List[MagicMirrorPackage]], packages_to_install: List[str]) -> List[MagicMirrorPackage]:
    '''
    Used to display more detailed information that presented in normal search results

    Parameters:
        packages (Dict[str, List[MagicMirrorPackage]]): MagicMirror modules database snapshot
        packages_to_install (List[str]): list of modules provided by user through command line arguments

    Returns:
        installation_candidates (List[MagicMirrorPackage]): list of modules whose module names match those of the modules_to_install
    '''

    installation_candidates: List[MagicMirrorPackage] = []

    if 'mmpm' in packages_to_install:
        mmpm.utils.warning_msg("Removing 'mmpm' as an installation candidate. It's obviously already installed " + u'\U0001F609')
        packages_to_install.remove('mmpm')

    for package_to_install in packages_to_install:
        found: bool = False
        for category in packages.values():
            for package in category:
                if package.title == package_to_install:
                    mmpm.utils.log.info(f'Matched {package.title} to installation candidate')
                    installation_candidates.append(package)
                    found = True
        if not found:
            mmpm.utils.error_msg(f"Unable to match package to query of '{package_to_install}'. Is there a typo?")

    return installation_candidates


def install_packages(installation_candidates: List[MagicMirrorPackage], assume_yes: bool = False) -> bool:
    '''
    Compares list of 'modules_to_install' to modules found within the
    'modules', clones the repository within the ~/MagicMirror/modules
    directory, and runs 'npm install' for each newly installed module.

    Parameters:
        installation_candidates (List[MagicMirrorPackage]): List of MagicMirrorPackages to install
        assume_yes (bool): if True, assume yes for user response, and do not display prompt

    Returns:
        bool: True upon success, False upon failure
    '''

    errors: List[dict] = []

    if not os.path.exists(mmpm.consts.MAGICMIRROR_MODULES_DIR):
        mmpm.utils.error_msg(f'MagicMirror directory not found. Please ensure the MMPM environment variables are set properly in your shell configuration')
        return False

    if not installation_candidates:
        mmpm.utils.error_msg('Unable to match query any to installation candidates')
        return False

    mmpm.utils.log.info(f'Changing into MagicMirror modules directory {mmpm.consts.MAGICMIRROR_MODULES_DIR}')
    os.chdir(mmpm.consts.MAGICMIRROR_MODULES_DIR)

    # a flag to check if any of the modules have been installed. Used for displaying a message later
    successes: int = 0
    match_count: int = len(installation_candidates)

    print(mmpm.color.normal_cyan(f"Matched query to {match_count} {'package' if match_count == 1 else 'packages'}"))

    for index, candidate in enumerate(installation_candidates):
        if not mmpm.utils.prompt_user(f'Install {mmpm.color.normal_green(candidate.title)} ({candidate.repository})?', assume_yes=assume_yes):
            mmpm.utils.log.info(f'User not chose to install {candidate.title}')
            installation_candidates[index] = MagicMirrorPackage()
        else:
            mmpm.utils.log.info(f'User chose to install {candidate.title} ({candidate.repository})')

    existing_module_dirs: List[str] = mmpm.utils.get_existing_package_directories()

    for package in installation_candidates:
        if package == None: # the module may be empty due to the above for loop
            continue

        package.directory = os.path.join(mmpm.consts.MAGICMIRROR_MODULES_DIR, package.title)

        # ideally, providiing alternative installation directories would be done, but it would require messing with file names within the renamed
        # module, which can cause a lot of problems when trying to update those repos
        if package.title in existing_module_dirs:
            mmpm.utils.log.error(f'Conflict encountered. Found a package named {package.title} already at {package.directory}')
            mmpm.utils.error_msg(f'A module named {package.title} is already installed in {package.directory}. Please remove {package.title} first.')
            continue

        try:
            success, _ = install_package(package, assume_yes=assume_yes)

            if success:
                existing_module_dirs.append(package.directory)
                successes += 1

        except KeyboardInterrupt:
            mmpm.utils.log.info(f'Cleaning up cancelled installation path of {package.directory} before exiting')
            os.chdir(mmpm.consts.HOME_DIR)
            os.system(f"rm -rf '{package.directory}'")
            mmpm.utils.keyboard_interrupt_log()

    if not successes:
        return False

    print(f'Run `mmpm open --config` to edit the configuration for newly installed modules')
    return True


def install_package(package: MagicMirrorPackage, assume_yes: bool = False) -> Tuple[bool, str]:
    '''
    Used to display more detailed information that presented in normal search results

    Parameters:
        package (MagicMirrorPackage): the MagicMirrorPackage to be installed
        assume_yes (bool): if True, all prompts are assumed to have a response of yes from the user

    Returns:
        installation_candidates (List[dict]): list of modules whose module names match those of the modules_to_install
    '''

    os.chdir(mmpm.consts.MAGICMIRROR_MODULES_DIR)

    print(f'{mmpm.consts.GREEN_DASHES} Installing {mmpm.color.normal_green(package.title)}')
    error_code, _, stderr = mmpm.utils.clone(
        package.title,
        package.repository,
        os.path.normpath(package.directory if package.directory else os.path.join(
                mmpm.consts.MAGICMIRROR_MODULES_DIR, package.title
            )
        )
    )

    if error_code:
        print(mmpm.consts.RED_X)
        mmpm.utils.error_msg(stderr)
        return False, stderr

    print(mmpm.consts.GREEN_CHECK_MARK)

    error: str = mmpm.utils.install_dependencies(package.directory)

    os.chdir(mmpm.consts.MAGICMIRROR_MODULES_DIR)

    if error:
        mmpm.utils.error_msg(error)
        message: str = f"Failed to install {package.title} at '{package.directory}'"
        mmpm.utils.log.error(message)

        yes = mmpm.utils.prompt_user(
            f"{mmpm.color.bright_red('ERROR:')} Failed to install {package.title} at '{package.directory}'. Remove the directory?",
            assume_yes=assume_yes
        )

        if yes:
            message = f"User chose to remove {package.title} at '{package.directory}'"
            # just to make sure there aren't any errors in removing the directory
            os.system(f"rm -rf '{package.directory}'")
            print(f"{mmpm.consts.GREEN_DASHES} Removing '{package.directory}' {mmpm.consts.GREEN_CHECK_MARK}")
        else:
            message = f"Keeping {package.title} at '{package.directory}'"
            print(f'\n{message}\n')
            mmpm.utils.log.info(message)

        return False, error

    return True, str()


def check_for_magicmirror_updates(assume_yes: bool = False) -> bool:
    '''
    Checks for updates available to the MagicMirror repository. Alerts user if an upgrade is available.

    Parameters:
        assume_yes (bool): if True, assume yes for user response, and do not display prompt

    Returns:
        bool: True upon success, False upon failure
    '''
    if not os.path.exists(mmpm.consts.MMPM_MAGICMIRROR_ROOT):
        mmpm.utils.error_msg(f'MagicMirror application directory not found. Please ensure the MMPM environment variables are set properly in your shell configuration')
        return False

    is_git: bool = True

    if not os.path.exists(os.path.join(mmpm.consts.MMPM_MAGICMIRROR_ROOT, '.git')):
        mmpm.utils.warning_msg('The MagicMirror root is not a git repo. If running MagicMirror as a Docker container, updates cannot be performed via mmpm.')
        is_git = False

    update_available: bool = False

    if is_git:
        os.chdir(mmpm.consts.MMPM_MAGICMIRROR_ROOT)
        cyan_application: str = f"{mmpm.color.normal_cyan('application')}"
        mmpm.utils.plain_print(f"Checking {mmpm.color.normal_green('MagicMirror')} [{cyan_application}] for updates")

        try:
            # stdout and stderr are flipped for git command output, because that totally makes sense
            # except now stdout doesn't even contain error messages...thanks git
            error_code, _, stdout = mmpm.utils.run_cmd(['git', 'fetch', '--dry-run'])
        except KeyboardInterrupt:
            print(mmpm.consts.RED_X)
            mmpm.utils.keyboard_interrupt_log()

        print(mmpm.consts.GREEN_CHECK_MARK)

        if error_code:
            mmpm.utils.error_msg('Unable to communicate with git server')

        if stdout:
            update_available = True

    upgrades: dict = {}

    env: str = mmpm.consts.MMPM_MAGICMIRROR_ROOT

    with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'r') as available_upgrades:
        try:
            upgrades = json.load(available_upgrades)
        except json.JSONDecodeError:
            upgrades = {
                mmpm.consts.MMPM: False,
                mmpm.consts.MMPM_MAGICMIRROR_ROOT: {
                    mmpm.consts.PACKAGES: [],
                    mmpm.consts.MAGICMIRROR: update_available
                }
            }

    with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w') as available_upgrades:
        if env not in upgrades:
            upgrades[env] = {mmpm.consts.PACKAGES: [], mmpm.consts.MAGICMIRROR: update_available}
        else:
            upgrades[env][mmpm.consts.MAGICMIRROR] = update_available

        json.dump(upgrades, available_upgrades)

    return update_available


def upgrade_magicmirror() -> bool:
    '''
    Handles upgrade processs of MagicMirror by pulling changes from MagicMirror
    repo, and installing dependencies.

    Parameters:
        None

    Returns:
        success (bool): True if success, False if failure

    '''
    print(f"{mmpm.consts.GREEN_DASHES} Upgrading {mmpm.color.normal_green('MagicMirror')}")

    os.chdir(mmpm.consts.MMPM_MAGICMIRROR_ROOT)
    error_code, _, stderr = mmpm.utils.run_cmd(['git', 'pull'], progress=False)

    if error_code:
        mmpm.utils.error_msg(f'Failed to upgrade MagicMirror {mmpm.consts.RED_X}')
        mmpm.utils.error_msg(stderr)
        return False

    error: str = mmpm.utils.install_dependencies(mmpm.consts.MMPM_MAGICMIRROR_ROOT)

    if error:
        mmpm.utils.error_msg(error)
        return False

    print(f'Restart MagicMirror for the changes to take effect')
    return True


def install_magicmirror() -> bool:
    '''
    Installs MagicMirror. First checks if a MagicMirror installation can be
    found, and if one is found, prompts user to update the MagicMirror.
    Otherwise, searches for current version of NodeJS on the system. If one is
    found, the MagicMirror is then installed. If an old version of NodeJS is
    found, a newer version is installed before installing MagicMirror.

    Parameters:
        None

    Returns:
        bool: True upon succcess, False upon failure
    '''

    if os.path.exists(mmpm.consts.MMPM_MAGICMIRROR_ROOT):
        mmpm.utils.fatal_msg('MagicMirror is installed already')

    if mmpm.utils.prompt_user(f"Use '{mmpm.consts.HOME_DIR}' as the parent directory of the MagicMirror installation?"):
        parent = mmpm.consts.HOME_DIR
    else:
        parent = os.path.abspath(input('Absolute path to MagicMirror parent directory: '))
        print(f'Please set the MMPM_MAGICMIRROR_ROOT env variable in your bashrc to {parent}/MagicMirror')

    if not shutil.which('curl'):
        mmpm.utils.fatal_msg("'curl' command not found. Please install 'curl', then re-run mmpm install --magicmirror")

    os.chdir(parent)
    print(mmpm.color.normal_cyan(f'Installing MagicMirror in {parent}/MagicMirror ...'))
    os.system('bash -c "$(curl -sL https://raw.githubusercontent.com/sdetweil/MagicMirror_scripts/master/raspberry.sh)"')
    return True


def remove_packages(installed_packages: Dict[str, List[MagicMirrorPackage]], packages_to_remove: List[str], assume_yes: bool = False) -> bool:
    '''
    Gathers list of modules currently installed in the ~/MagicMirror/modules
    directory, and removes each of the modules from the folder, if modules are
    currently installed. Otherwise, the user is shown an error message alerting
    them no modules are currently installed.

    Parameters:
        installed_packages (Dict[str, List[MagicMirrorPackage]]): List of dictionary of MagicMirror packages
        modules_to_remove (list): List of modules to remove
        assume_yes (bool): if True, all prompts are assumed to have a response of yes from the user

    Returns:
        bool: True upon success, False upon failure
    '''

    cancelled_removal: List[str] = []
    marked_for_removal: List[str] = []

    package_dirs: List[str] = os.listdir(mmpm.consts.MAGICMIRROR_MODULES_DIR)

    try:
        for _, packages in installed_packages.items():
            for package in packages:
                dir_name = os.path.basename(package.directory)
                if dir_name in package_dirs and dir_name in packages_to_remove:
                    prompt: str = f'Would you like to remove {mmpm.color.normal_green(package.title)} ({package.directory})?'
                    if mmpm.utils.prompt_user(prompt, assume_yes=assume_yes):
                        marked_for_removal.append(dir_name)
                        mmpm.utils.log.info(f'User marked {dir_name} for removal')
                    else:
                        cancelled_removal.append(dir_name)
                        mmpm.utils.log.info(f'User chose not to remove {dir_name}')
    except KeyboardInterrupt:
        mmpm.utils.keyboard_interrupt_log()

    for title in packages_to_remove:
        if title not in marked_for_removal and title not in cancelled_removal:
            mmpm.utils.error_msg(f"'{title}' is not installed")
            mmpm.utils.log.info(f"User attemped to remove {title}, but no module named '{title}' was found in {mmpm.consts.MAGICMIRROR_MODULES_DIR}")

    for dir_name in marked_for_removal:
        shutil.rmtree(dir_name)
        print(f'{mmpm.consts.GREEN_DASHES} Removed {mmpm.color.normal_green(dir_name)} {mmpm.consts.GREEN_CHECK_MARK}')
        mmpm.utils.log.info(f'Removed {dir_name}')

    if marked_for_removal:
        print(f'Run `mmpm open --config` to delete associated configurations of any removed modules')

    return True


def load_packages(force_refresh: bool = False) -> Dict[str, List[MagicMirrorPackage]]:
    '''
    Reads in modules from the hidden 'snapshot_file'  and checks if the file is
    out of date. If so, the modules are gathered again from the MagicMirror 3rd
    Party Modules wiki.

    Parameters:
        force_refresh (bool): Boolean flag to force refresh of snapshot

    Returns:
        packages (Dict[str, List[MagicMirrorPackage]]): dictionary of MagicMirror 3rd party modules
    '''

    packages: dict = {}

    db_exists: bool = os.path.exists(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_SNAPSHOT_FILE)

    if not mmpm.utils.assert_snapshot_directory():
        message: str = 'Failed to create directory for MagicMirror snapshot'
        mmpm.utils.fatal_msg(message)

    if db_exists:
        mmpm.utils.log.info(f'Backing up database file as {mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_SNAPSHOT_FILE}.bak')

        shutil.copyfile(
            mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_SNAPSHOT_FILE,
            f'{mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_SNAPSHOT_FILE}.bak'
        )

        mmpm.utils.log.info(f'Back up of database complete')

    # if the snapshot has expired, or doesn't exist, get a new one
    if force_refresh or not db_exists:
        mmpm.utils.plain_print(
            f"{mmpm.consts.GREEN_DASHES} {'Refreshing' if db_exists else 'Initializing'} MagicMirror 3rd party packages database "
        )

        packages = retrieve_packages()

        if not packages:
            print(mmpm.consts.RED_X)
            mmpm.utils.error_msg(f'Failed to retrieve packages from {mmpm.consts.MAGICMIRROR_MODULES_URL}. Please check your internet connection.')

        # save the new snapshot
        else:
            with open(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_SNAPSHOT_FILE, 'w') as snapshot:
                json.dump(packages, snapshot, default=lambda pkg: pkg.serialize())

            print(mmpm.consts.GREEN_CHECK_MARK)

    if not packages and db_exists:
        with open(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_SNAPSHOT_FILE, 'r') as snapshot_file:
            packages = json.load(snapshot_file)

            for category in packages.keys():
                packages[category] = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(packages[category])

    if packages and os.path.exists(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE) and os.stat(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE).st_size:
        packages.update(**load_external_packages())

    return packages


def load_external_packages() -> Dict[str, List[MagicMirrorPackage]]:
    '''
    Extracts the external packages from the JSON files stored in
    ~/.config/mmpm/mmpm-external-packages.json

    If no data is found, an empty list is returned

    Parameters:
        None

    Returns:
        external_packages (Dict[str, List[MagicMirrorPackage]]): the list of manually added MagicMirror packages
    '''
    external_packages: List[MagicMirrorPackage] = []

    try:
        with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'r') as f:
            external_packages = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(json.load(f)[mmpm.consts.EXTERNAL_PACKAGES])
    except Exception:
        message = f'Failed to load data from {mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE}. Please examine the file, as it may be malformed and required manual corrective action.'
        mmpm.utils.warning_msg(message)

    return {mmpm.consts.EXTERNAL_PACKAGES: external_packages}

def retrieve_packages() -> Dict[str, List[MagicMirrorPackage]]:
    '''
    Scrapes the MagicMirror 3rd Party Wiki for all packages listed by community members

    Parameters:
        None

    Returns:
        packages (Dict[str, List[MagicMirrorPackage]]): dictionary of MagicMirror 3rd party modules
    '''

    packages: Dict[str, List[MagicMirrorPackage]] = defaultdict(list)

    try:
        url = urlopen(mmpm.consts.MAGICMIRROR_MODULES_URL)
        web_page = url.read()
    except (HTTPError, URLError):
        print(mmpm.consts.RED_X)
        mmpm.utils.fatal_msg('Unable to retrieve MagicMirror modules. Is your internet connection up?')
        return {}

    soup = BeautifulSoup(web_page, 'html.parser')
    table_soup: list = soup.find_all('table')

    category_soup: list = soup.find_all(attrs={'class': 'markdown-body'})
    categories_soup: list = category_soup[0].find_all('h3')

    categories: list = []

    for index, _ in enumerate(categories_soup):
        last_element: object = len(categories_soup[index].contents) - 1
        new_category: object = categories_soup[index].contents[last_element]

        if new_category != 'General Advice':
            categories.append(new_category)

    tr_soup: list = []

    for table in table_soup:
        tr_soup.append(table.find_all("tr"))

    for index, row in enumerate(tr_soup):
        for column_number, _ in enumerate(row):
            # ignore cells that literally say "Title", "Author", "Description"
            if column_number > 0:
                td_soup: list = tr_soup[index][column_number].find_all('td')

                package = MagicMirrorPackage()

                title: str = mmpm.consts.NOT_AVAILABLE
                repo: str = mmpm.consts.NOT_AVAILABLE
                author: str = mmpm.consts.NOT_AVAILABLE
                desc: str = mmpm.consts.NOT_AVAILABLE

                for idx, _ in enumerate(td_soup):
                    if idx == 0:
                        for td in td_soup[idx]:
                            title = td.contents[0]

                        for a in td_soup[idx].find_all('a'):
                            if a.has_attr('href'):
                                repo = a['href']

                        package.repository = str(repo).strip()
                        package.title = str(title)

                    elif idx == 1:
                        for contents in td_soup[idx].contents:
                            if type(contents).__name__ == 'Tag':
                                for tag in contents:
                                    author = tag.strip()
                            else:
                                author = contents

                        author = str(author)

                    else:
                        if contents:
                            desc = str()
                        for contents in td_soup[idx].contents:
                            if type(contents).__name__ == 'Tag':
                                for content in contents:
                                    desc += content.string
                            else:
                                desc += contents.string

                packages[categories[index]].append(
                    MagicMirrorPackage(
                        title=mmpm.utils.sanitize_name(title).strip(),
                        author=author.strip(),
                        description=desc.strip(),
                        repository=repo.strip()
                    )
                )

    return packages


def display_categories(packages: Dict[str, List[MagicMirrorPackage]], title_only: bool = False) -> None:
    '''
    Prints module category names and the total number of modules in one of two
    formats. The default is similar to the Debian apt package manager, and the
    prettified table alternative

    Parameters:
        packages (Dict[str, List[MagicMirrorPackage]]): list of dictionaries containing category names and module count

    Returns:
        None
    '''

    categories: List[dict] = [
        {
            mmpm.consts.CATEGORY: key,
            mmpm.consts.PACKAGES: len(packages[key])
        } for key in packages.keys()
    ]

    for category in categories:
        print(mmpm.color.normal_green(category[mmpm.consts.CATEGORY]), f'\n  Packages: {category[mmpm.consts.PACKAGES]}\n')
    return


def display_packages(packages: Dict[str, List[MagicMirrorPackage]], title_only: bool = False, include_path: bool = False) -> None:
    '''
    Depending on the user flags passed in from the command line, either all
    existing packages may be displayed, or the names of all categories of
    packages may be displayed.

    Parameters:
        packages (Dict[str, List[MagicMirrorPackage]]): dictionary of MagicMirror 3rd party packages
        list_categories (bool): Boolean flag to list categories

    Returns:
        None
    '''
    format_description = lambda desc: desc[:MAX_LENGTH] + '...' if len(desc) > MAX_LENGTH else desc
    MAX_LENGTH: int = 120

    if title_only:
        _print_ = lambda package: print(package.title)

    elif include_path:
        _print_ = lambda package: print(
            mmpm.color.normal_green(f'{package.title}'),
            (f'\n  Directory: {package.directory}'),
            (f"\n  {format_description(package.description)}\n")
        )

    else:
        _print_ = lambda package: print(
            mmpm.color.normal_green(f'{package.title}'),
            (f"\n  {format_description(package.description)}\n")
        )

    for _, _packages in packages.items():
        for _, package in enumerate(_packages):
            _print_(package)


def display_available_upgrades() -> None:
    '''
    Based on the current environment, available upgrades for packages, and
    MagicMirror will be displayed. The status of upgrades available for MMPM is
    static, regardless of the environment. The available upgrades are read from
    a file, `~/.config/mmpm/mmpm-available-upgrades.json`, which is updated
    after running `mmpm update`

    Parameters:
        None

    Returns:
        None
    '''
    cyan_application: str = f"{mmpm.color.normal_cyan('application')}"
    cyan_package: str = f"{mmpm.color.normal_cyan('package')}"
    env: str = mmpm.consts.MMPM_MAGICMIRROR_ROOT

    upgrades_available: bool = False
    upgrades = get_available_upgrades()

    if upgrades[env][mmpm.consts.PACKAGES]:
        for package in upgrades[env][mmpm.consts.PACKAGES]:
            print(mmpm.color.normal_green(package.title), f'[{cyan_package}]')
            upgrades_available = True

    if upgrades[mmpm.consts.MMPM]:
        upgrades_available = True
        print(f'{mmpm.color.normal_green(mmpm.consts.MMPM)} [{cyan_application}]')

    if upgrades[env][mmpm.consts.MAGICMIRROR]:
        upgrades_available = True
        print(f'{mmpm.color.normal_green(mmpm.consts.MAGICMIRROR)} [{cyan_application}]')

    if upgrades_available:
        print('Run `mmpm upgrade` to upgrade available packages/applications')
    else:
        print(f'No upgrades available {mmpm.consts.YELLOW_X}')


def get_available_upgrades() -> dict:
    '''

    '''
    env: str = mmpm.consts.MMPM_MAGICMIRROR_ROOT
    reset_file: bool = False
    add_key: bool = False

    with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'r') as available_upgrades:
        try:
            upgrades: dict = json.load(available_upgrades)
            upgrades[env][mmpm.consts.PACKAGES] = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(
                upgrades[env][mmpm.consts.PACKAGES]
            )
        except json.JSONDecodeError:
            reset_file = True
        except KeyError:
            add_key = True

    if reset_file:
        with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w') as available_upgrades:
            upgrades = {mmpm.consts.MMPM: False, env: {mmpm.consts.PACKAGES: [], mmpm.consts.MAGICMIRROR: False }}
            json.dump(upgrades, available_upgrades)

    elif add_key:
        with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w') as available_upgrades:
            upgrades[env] = {mmpm.consts.PACKAGES: [], mmpm.consts.MAGICMIRROR: False}
            json.dump(upgrades, available_upgrades)

    return upgrades


def get_installed_packages(packages: Dict[str, List[MagicMirrorPackage]]) -> Dict[str, List[MagicMirrorPackage]]:
    '''
    Saves a list of all currently installed packages in the
    ~/MagicMirror/modules directory, and compares against the known packages
    from the MagicMirror 3rd Party Wiki.

    Parameters:
        packages (Dict[str, List[MagicMirrorPackage]]): Dictionary of MagicMirror packages

    Returns:
        installed_modules (Dict[str, List[MagicMirrorPackage]]): Dictionary of installed MagicMirror packages
    '''

    package_dirs: List[str] = mmpm.utils.get_existing_package_directories()

    if not package_dirs:
        mmpm.utils.env_variables_error_msg('Failed to find MagicMirror root directory.')
        return {}

    os.chdir(mmpm.consts.MAGICMIRROR_MODULES_DIR)

    installed_packages: Dict[str, List[MagicMirrorPackage]] = {}
    packages_found: Dict[str, List[MagicMirrorPackage]] = {mmpm.consts.PACKAGES: []}

    for package_dir in package_dirs:
        if not os.path.isdir(package_dir) or not os.path.exists(os.path.join(os.getcwd(), package_dir, '.git')):
            continue

        try:
            os.chdir(os.path.join(mmpm.consts.MAGICMIRROR_MODULES_DIR, package_dir))

            error_code, remote_origin_url, stderr = mmpm.utils.run_cmd(
                ['git', 'config', '--get', 'remote.origin.url'],
                progress=False
            )

            if error_code:
                mmpm.utils.error_msg(f'Unable to communicate with git server to retrieve information about {package_dir}')
                continue

            error_code, project_name, stderr = mmpm.utils.run_cmd(
                ['basename', remote_origin_url.strip(), '.git'],
                progress=False
            )

            if error_code:
                mmpm.utils.error_msg(f'Unable to determine repository origin for {project_name}')
                continue

            packages_found[mmpm.consts.PACKAGES].append(
                MagicMirrorPackage(
                    title=project_name.strip(),
                    repository=remote_origin_url.strip(),
                    directory=os.getcwd()
                )
            )

        except Exception:
            mmpm.utils.error_msg(stderr)

        finally:
            os.chdir('..')

    for category, package_names in packages.items():
        installed_packages.setdefault(category, [])
        for package in package_names:
            for package_found in packages_found[mmpm.consts.PACKAGES]:
                if package.repository == package_found.repository:
                    package.directory = package_found.directory
                    installed_packages[category].append(package)

    return installed_packages


def add_external_package(title: str = None, author: str = None, repo: str = None, description: str = None) -> str:
    '''
    Adds an external source for user to install a module from. This may be a
    private git repo, or a specific branch of a public repo. All modules added
    in this manner will be added to the 'External Module Sources' category.
    These sources are stored in ~/.config/mmpm/mmpm-external-packages.json

    Parameters:
        title (str): External source title
        author (str): External source author
        repo (str): External source repo url
        description (str): External source description

    Returns:
        (bool): Upon success, a True result is returned
    '''
    try:
        if not title:
            title = mmpm.utils.assert_valid_input('Title: ')
        else:
            print(f'Title: {title}')

        if not author:
            author = mmpm.utils.assert_valid_input('Author: ')
        else:
            print(f'Author: {author}')

        if not repo:
            repo = mmpm.utils.assert_valid_input('Repository: ')
        else:
            print(f'Repository: {repo}')

        if not description:
            description = mmpm.utils.assert_valid_input('Description: ')
        else:
            print(f'Description: {description}')

    except KeyboardInterrupt:
        mmpm.utils.keyboard_interrupt_log()

    external_package = MagicMirrorPackage(title=title, repository=repo, author=author, description=description)

    try:
        if os.path.exists(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE) and os.stat(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE).st_size:
            config: dict = {}

            with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'r') as mmpm_ext_srcs:
                config[mmpm.consts.EXTERNAL_PACKAGES] = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(json.load(mmpm_ext_srcs)[mmpm.consts.EXTERNAL_PACKAGES])

            with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'w') as mmpm_ext_srcs:
                config[mmpm.consts.EXTERNAL_PACKAGES].append(external_package)
                json.dump(config, mmpm_ext_srcs, default=lambda pkg: pkg.serialize())
        else:
            # if file didn't exist previously, or it was empty, this is the first external package that's been added
            with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'w') as mmpm_ext_srcs:
                json.dump({mmpm.consts.EXTERNAL_PACKAGES: [external_package]}, mmpm_ext_srcs, default=lambda pkg: pkg.serialize())

        print(mmpm.color.normal_green(f"\nSuccessfully added {title} to '{mmpm.consts.EXTERNAL_PACKAGES}'\n"))

    except IOError as error:
        mmpm.utils.error_msg('Failed to save external module')
        return str(error)

    return ''


def remove_external_package_source(titles: List[str] = None, assume_yes: bool = False) -> bool:
    '''
    Allows user to remove an external source from the sources saved in
    ~/.config/mmpm/mmpm-external-packages.json

    Parameters:
        titles (List[str]): External source titles

    Returns:
        success (bool): True on success, False on error
    '''

    if not os.path.exists(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE):
        mmpm.utils.fatal_msg(f'{mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE} does not appear to exist')

    elif not os.stat(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE).st_size:
        mmpm.utils.fatal_msg(f'{mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE} is empty')

    ext_packages: Dict[str, List[MagicMirrorPackage]] = {}
    marked_for_removal: List[MagicMirrorPackage] = []
    cancelled_removal: List[MagicMirrorPackage] = []

    with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'r') as mmpm_ext_srcs:
        ext_packages[mmpm.consts.EXTERNAL_PACKAGES] = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(json.load(mmpm_ext_srcs)[mmpm.consts.EXTERNAL_PACKAGES])

    if not ext_packages[mmpm.consts.EXTERNAL_PACKAGES]:
        mmpm.utils.fatal_msg('No external packages found in database')

    for title in titles:
        for package in ext_packages[mmpm.consts.EXTERNAL_PACKAGES]:
            if package.title == title:
                prompt: str = f'Would you like to remove {mmpm.color.normal_green(title)} ({package.repository}) from the MMPM/MagicMirror local database?'
                if mmpm.utils.prompt_user(prompt, assume_yes=assume_yes):
                    marked_for_removal.append(package)
                else:
                    cancelled_removal.append(package)

    if not marked_for_removal and not cancelled_removal:
        mmpm.utils.error_msg('No external sources found matching provided query')
        return False

    for package in marked_for_removal:
        ext_packages[mmpm.consts.EXTERNAL_PACKAGES].remove(package)
        print(f'Removed {package.title} ({package.repository}) {mmpm.consts.GREEN_CHECK_MARK}')

    # if the error_msg was triggered, there's no need to even bother writing back to the file
    with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'w') as mmpm_ext_srcs:
        json.dump(ext_packages, mmpm_ext_srcs, default=lambda pkg: pkg.serialize())

    return True


def display_active_packages() -> None:

    '''
    Parses the MagicMirror config file for the modules listed, and reports
    which modules are currently enabled. A module is considered disabled if the
    module explictly contains a 'disabled' flag with a 'true' value. Otherwise,
    the module is considered enabled.

    Parameters:
        None

    Returns:
        None
    '''

    if not os.path.exists(mmpm.consts.MAGICMIRROR_CONFIG_FILE):
        mmpm.utils.env_variables_fatal_msg('MagicMirror config file not found.')

    temp_config: str = f'{mmpm.consts.MMPM_MAGICMIRROR_ROOT}/config/temp_config.js'
    shutil.copyfile(mmpm.consts.MAGICMIRROR_CONFIG_FILE, temp_config)

    with open(temp_config, 'a') as temp:
        temp.write('console.log(JSON.stringify(config))')

    _, stdout, _ = mmpm.utils.run_cmd(['node', temp_config], progress=False)
    config: dict = json.loads(stdout.split('\n')[0])

    # using -f so any errors can be ignored
    mmpm.utils.run_cmd(['rm', '-f', temp_config], progress=False)

    if 'modules' not in config or not config['modules']:
        mmpm.utils.error_msg(f'No modules found in {mmpm.consts.MAGICMIRROR_CONFIG_FILE}')

    for module_config in config['modules']:
        print(
            mmpm.color.normal_green(module_config['module']),
            f"\n  Status: {'disabled' if 'disabled' in module_config and module_config['disabled'] else 'enabled'}\n"
        )


def get_web_interface_url() -> str:
    '''
    Parses the MMPM nginx conf file for the port number assigned to the web
    interface, and returns a string containing containing the host IP and
    assigned port.

    Parameters:
        None

    Returns:
        str: The URL of the MMPM web interface
    '''

    if not os.path.exists(mmpm.consts.MMPM_NGINX_CONF_FILE):
        mmpm.utils.fatal_msg('The MMPM NGINX configuration file does not appear to exist. Is the GUI installed?')

    # this value needs to be retrieved dynamically in case the user modifies the nginx conf
    with open(mmpm.consts.MMPM_NGINX_CONF_FILE, 'r') as conf:
        mmpm_conf = conf.read()

    try:
        port: str = re.findall(r"listen\s?\d+", mmpm_conf)[0].split()[1]
    except IndexError:
        mmpm.utils.fatal_msg('Unable to retrieve the port number of the MMPM web interface')

    return f'http://{gethostbyname(gethostname())}:{port}'



def stop_magicmirror() -> bool:
    '''
    Stops MagicMirror using pm2, if found, otherwise the associated
    processes are killed

    Parameters:
       None

    Returns:
        None
    '''
    if shutil.which('pm2') and mmpm.consts.MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
        mmpm.utils.log.info("Using 'pm2' to stop MagicMirror")
        _, _, stderr = mmpm.utils.run_cmd(['pm2', 'stop', mmpm.consts.MMPM_MAGICMIRROR_PM2_PROCESS_NAME], progress=False)

        if stderr:
            mmpm.utils.env_variables_error_msg(stderr.strip())
            return False

        mmpm.utils.log.info('stopped MagicMirror using PM2')
        return True

    mmpm.utils.kill_magicmirror_processes()
    return True


def start_magicmirror() -> bool:
    '''
    Launches MagicMirror using pm2, if found, otherwise a 'npm start' is run as
    a background process

    Parameters:
       None

    Returns:
        None
    '''
    mmpm.utils.log.info('Starting MagicMirror')
    os.chdir(mmpm.consts.MMPM_MAGICMIRROR_ROOT)

    mmpm.utils.log.info("Running 'npm start' in the background")

    if shutil.which('pm2') and mmpm.consts.MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
        mmpm.utils.log.info("Using 'pm2' to start MagicMirror")
        error_code, _, stderr = mmpm.utils.run_cmd(
            ['pm2', 'start', mmpm.consts.MMPM_MAGICMIRROR_PM2_PROCESS_NAME],
            background=True
        )

        if error_code:
            mmpm.utils.env_variables_error_msg(stderr.strip())
            return False

        mmpm.utils.log.info('started MagicMirror using PM2')
        return True

    os.system('npm start &')
    mmpm.utils.log.info("Using 'npm start' to start MagicMirror. Stdout/stderr capturing not possible in this case")
    return False if error_code else True


def restart_magicmirror() -> bool:
    '''
    Restarts MagicMirror using pm2, if found, otherwise the associated
    processes are killed and 'npm start' is re-run a background process

    Parameters:
       None

    Returns:
        None
    '''
    if shutil.which('pm2') and mmpm.consts.MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
        mmpm.utils.log.info("Using 'pm2' to restart MagicMirror")
        _, _, stderr = mmpm.utils.run_cmd(
            ['pm2', 'restart', mmpm.consts.MMPM_MAGICMIRROR_PM2_PROCESS_NAME],
            progress=False
        )

        if stderr:
            mmpm.utils.env_variables_error_msg(stderr.strip())
            return False

        mmpm.utils.log.info('restarted MagicMirror using PM2')
        return True

    if not stop_magicmirror():
        mmpm.utils.log.error('Failed to stop MagicMirror using npm commands')
        return False

    if not start_magicmirror():
        mmpm.utils.log.error('Failed to start MagicMirror using npm commands')
        return False

    mmpm.utils.log.info('Restarted MagicMirror using npm commands')
    return True


def display_log_files(cli_logs: bool = False, gui_logs: bool = False, tail: bool = False) -> None:
    '''
    Displays contents of log files to stdout. If the --tail option is supplied,
    log contents will be displayed in real-time

    Parameters:
       cli_logs (bool): if True, the CLI log files will be displayed
       gui_logs (bool): if True, the Gunicorn log files for the web interface will be displayed
       tail (bool): if True, the contents will be displayed in real time

    Returns:
        None
    '''
    logs: List[str] = []

    if cli_logs:
        if os.path.exists(mmpm.consts.MMPM_CLI_LOG_FILE):
            logs.append(mmpm.consts.MMPM_CLI_LOG_FILE)
        else:
            mmpm.utils.error_msg('MMPM log file not found')

    if gui_logs:
        if os.path.exists(mmpm.consts.MMPM_GUNICORN_ACCESS_LOG_FILE):
            logs.append(mmpm.consts.MMPM_GUNICORN_ACCESS_LOG_FILE)
        else:
            mmpm.utils.error_msg('Gunicorn access log file not found')
        if os.path.exists(mmpm.consts.MMPM_GUNICORN_ERROR_LOG_FILE):
            logs.append(mmpm.consts.MMPM_GUNICORN_ERROR_LOG_FILE)
        else:
            mmpm.utils.error_msg('Gunicorn error log file not found')

    if logs:
        os.system(f"{'tail -F' if tail else 'cat'} {' '.join(logs)}")


def display_mmpm_env_vars(detailed: bool = False) -> None:
    '''
    Displays the environment variables associated with MMPM, as well as their
    current value. A user may modify these values by setting them in their
    shell configuration file

    Parameters:
        detailed (bool): if True, comments displaying the usage of the
                         environment variables are displayed

    Returns:
        None
    '''

    mmpm.utils.log.info(f'User listing environment variables, set with the following values')

    if detailed:
        for var, info in mmpm.consts.MMPM_ENV.items():
            output: str = f"{var}={info['value']} # {info['detail']}"
            mmpm.utils.log.info(output)
            print(output)

    else:
        for var, info in mmpm.consts.MMPM_ENV.items():
            output = f"{var}={info['value']}"
            mmpm.utils.log.info(output)
            print(output)


def install_autocompletion(assume_yes: bool = False) -> None:
    '''
    Adds autocompletion configuration to a user's shell configuration file.
    Detects configuration files for bash, zsh, fish, and tcsh

    Parameters:
        assume_yes (bool): if True, assume yes for user response, and do not display prompt

    Returns:
        None
    '''

    if not mmpm.utils.prompt_user('Are you sure you want to install the autocompletion feature for the MMPM CLI?', assume_yes=assume_yes):
        mmpm.utils.log.info('User cancelled installation of autocompletion for MMPM CLI')
        return

    mmpm.utils.log.info('user attempting to install MMPM autocompletion')
    shell: str = os.environ['SHELL']

    mmpm.utils.log.info(f'detected user shell to be {shell}')

    autocomplete_url: str = 'https://github.com/kislyuk/argcomplete#activating-global-completion'
    error_message: str = f'Please see {autocomplete_url} for help installing autocompletion'

    complete_message = lambda config: f'Autocompletion installed. Please source {config} for the changes to take effect'
    failed_match_message = lambda shell, configs: f'Unable to locate {shell} configuration file (looked for {configs}). {error_message}'

    def __match_shell_config__(configs: List[str]) -> str:
        mmpm.utils.log.info(f'searching for one of the following shell configuration files {configs}')
        for config in configs:
            config = os.path.join(mmpm.consts.HOME_DIR, config)
            if os.path.exists(config):
                mmpm.utils.log.info(f'found {config} shell configuration file for {shell}')
                return config
        return ''

    def __echo_and_eval__(command: str) -> None:
        mmpm.utils.log.info(f'executing {command} to install autocompletion')
        print(f'{mmpm.consts.GREEN_DASHES} {mmpm.color.normal_green(command)}')
        os.system(command)

    if 'bash' in shell:
        files = ['.bashrc', '.bash_profile', '.bash_login', '.profile']
        config = __match_shell_config__(files)

        if not config:
            mmpm.utils.fatal_msg(failed_match_message('bash', files))

        __echo_and_eval__(f'echo \'eval "$(register-python-argcomplete mmpm)"\' >> {config}')

        print(complete_message(config))

    elif 'zsh' in shell:
        files = ['.zshrc', '.zprofile', '.zshenv', '.zlogin', '.profile']
        config = __match_shell_config__(files)

        if not config:
            mmpm.utils.fatal_msg(failed_match_message('zsh', files))

        __echo_and_eval__(f"echo 'autoload -U bashcompinit' >> {config}")
        __echo_and_eval__(f"echo 'bashcompinit' >> {config}")
        __echo_and_eval__(f'echo \'eval "$(register-python-argcomplete mmpm)"\' >> {config}')

        print(complete_message(config))

    elif 'tcsh' in shell:
        files = ['.tcshrc', '.cshrc', '.login']
        config = __match_shell_config__(files)

        if not config:
            mmpm.utils.fatal_msg(failed_match_message('tcsh', files))

        __echo_and_eval__(f"echo 'eval `register-python-argcomplete --shell tcsh mmpm`' >> {config}")

        print(complete_message(config))

    elif 'fish' in shell:
        files = ['.config/fish/config.fish']
        config = __match_shell_config__(files)

        if not config:
            mmpm.utils.fatal_msg(failed_match_message('fish', files))

        __echo_and_eval__(f"register-python-argcomplete --shell fish mmpm >> {config}")

        print(complete_message(config))

    else:
        mmpm.utils.fatal_msg(f'Unable install autocompletion for ({shell}). Please see {autocomplete_url} for help installing autocomplete')


def rotate_raspberrypi_screen(degrees: int) -> bool:
    '''
    Rotates screen of RaspberryPi 3 and RaspberryPi 4 to the setting supplied
    by the user

    Parameters:
        degrees (int): desired setting in degrees

    Returns:
        success (bool): True if successful, False if failure
    '''
    config: str = '/boot/config.txt'

    rotation_map: Dict[int, int] = {
        0: 0,
        90: 3,
        180: 2,
        270: 1
    }

    if os.path.exists('/proc/device-tree/model'):
        with open('/proc/device-tree/model', 'r') as model_info:
            rpi_model = model_info.read()

        if 'Raspberry Pi 3' in rpi_model:
            desired_setting: str = f'display_rotate={rotation_map[degrees]}'
            pattern: str = r'display_rotate=\d'

            # this really should exist anyway
            if not os.path.exists(config):
                os.system(f'touch {config}')

            with open(config, 'r+') as cfg:
                contents: str = cfg.read()
                setting: List[str] = re.findall(pattern, contents)

                if not setting:
                    # this file should not be empty, but just in case
                    contents += f'\n{desired_setting}\n'
                else:
                    contents = re.sub(pattern, desired_setting, contents, count=1)

                cfg.seek(0)
                cfg.write(contents)

        elif 'Raspberry Pi 4' in rpi_model:
            # TODO: figure this out
            pass

    else:
        mmpm.utils.error_msg('Display rotation has not been implemented for this type of computing unit. Only Raspberry Pi 3 and 4 are supported')
        return False

    print('Please restart your RaspberryPi for the changes to take effect')
    return True


def migrate() -> None:
    '''
    Migrates legacy External Module Sources to External Packages. The legacy
    file name of ~/.config/mmpm/mmpm-external-sources.json is renamed to
    ~/.config/mmpm/mmpm-external-packages.json. The key inside the dictionary
    is also renamed from 'External Module Sources' to 'External Packages'

    Parameters:
        None

    Returns:
        None
    '''
    legacy_ext_src_file: str = os.path.join(mmpm.consts.MMPM_CONFIG_DIR, 'mmpm-external-sources.json')
    legacy_key: str = 'External Module Sources'
    data: dict = {}

    if os.path.exists(legacy_ext_src_file):
        with open(legacy_ext_src_file, 'r') as legacy_file:
            mmpm.utils.log.info('Found existing legacy external modules sources file')
            try:
                data = json.load(legacy_file)

                if legacy_key in data:
                    mmpm.utils.log.info(f'Updating {legacy_key} in external modules dictionary to {mmpm.consts.EXTERNAL_PACKAGES}')
                    data[mmpm.consts.EXTERNAL_PACKAGES] = data[legacy_key]
                    data.pop(legacy_key)

                else:
                    mmpm.utils.log.info(f'No data found in the legacy key, resetting with empty list')
                    data[mmpm.consts.EXTERNAL_PACKAGES] = []

            except json.JSONDecodeError:
                mmpm.utils.fatal_msg(f'{legacy_ext_src_file} may be corrupted. Please examine the file')

        mmpm.utils.log.info(f'Renaming external packages file from {legacy_ext_src_file} to {mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE}')
        pathlib.Path.rename(legacy_ext_src_file, mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE)

        with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'w') as ext_pkgs:
            mmpm.utils.log.info(f'Saving updated external packages data')
            json.dump(data, ext_pkgs)

    else:
        mmpm.utils.log.info(f'{legacy_ext_src_file} does not exist, nothing to migrate')

    mmpm.utils.log.info('Completed migration of legacy External Module Sources migrated to External Packages')
    print('Migration complete!')
