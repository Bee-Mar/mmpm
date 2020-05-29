#!/usr/bin/env python3
import re
import os
import json
import datetime
import shutil
import sys
from socket import gethostname, gethostbyname
from textwrap import fill, indent
from tabulate import tabulate
from urllib.error import HTTPError
from urllib.request import urlopen
from collections import defaultdict
from bs4 import BeautifulSoup
from mmpm import colors, utils, mmpm, consts
from mmpm.utils import colored_text
from typing import List
from mmpm.utils import log, to_bytes
from shutil import which
import subprocess
import select


def snapshot_details(modules: dict) -> None:
    '''
    Displays information regarding the most recent 'snapshot_file', ie. when it
    was taken, when the next scheduled snapshot will be taken, how many module
    categories exist, and the total number of modules available. Additionally,
    tells user how to forcibly request a new snapshot be taken.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules

    Returns:
        None
    '''

    num_categories: int = len(modules.keys())
    num_modules: int = 0

    current_snapshot, next_snapshot = utils.calc_snapshot_timestamps()
    curr_snap_date = datetime.datetime.fromtimestamp(int(current_snapshot))
    next_snap_date = datetime.datetime.fromtimestamp(int(next_snapshot))

    for value in modules.values():
        num_modules += len(value)

    print(
        colored_text(colors.N_YELLOW, 'Most recent snapshot of MagicMirror Modules taken:'),
        f'{curr_snap_date}'
    )

    print(
        colored_text(colors.N_YELLOW, 'The next snapshot will be taken on or after:'),
        f'{next_snap_date}\n'
    )

    print(
        colored_text(colors.N_GREEN, 'Module Categories:'),
        f'{num_categories}'
    )

    print(
        colored_text(colors.N_GREEN, 'Modules Available:'),
        f'{num_modules}\n'
    )



def check_for_mmpm_enhancements(assume_yes=False, gui=False) -> bool:
    '''
    Scrapes the main file of MMPM off the github repo, and compares the current
    version, versus the one available in the master branch. If there is a newer
    version, the user is prompted for an upgrade.

    Parameters:
        None

    Returns:
        bool: True on success, False on failure
    '''

    try:
        log.logger.info(f'Checking for newer version of MMPM. Current version: {mmpm.__version__}')
        utils.plain_print(f'Checking for newer version of MMPM ... ')

        MMPM_FILE = urlopen(consts.MMPM_FILE_URL)
        contents: str = str(MMPM_FILE.read())

    except HTTPError as error:
        message: str = 'Unable to retrieve available version number from MMPM repository'
        utils.error_msg(message)
        log.logger.info(error)
        return False

    version_line: List[str] = re.findall(r"__version__ = \d+\.\d+", contents)
    version_list: List[str] = re.findall(r"\d+\.\d+", version_line[0])
    version_number: float = float(version_list[0])

    print(utils.done())

    if not version_number:
        message: str = 'No version number found on MMPM repository'
        utils.error_msg(message)
        log.logger.info(message)
        return False

    if mmpm.__version__ >= version_number:
        print('You have the latest version of MMPM')
        log.logger.info('No newer version of MMPM found > {version_number} available. The current version is the latest')
        return True

    log.logger.info(f'Found newer version of MMPM: {version_number}')

    print(f'\nInstalled version: {mmpm.__version__}')
    print(f'Available version: {version_number}\n')

    if gui:
        message = f"A newer version of MMPM is available ({version_number}). Please upgrade via terminal using 'mmpm uprade --mmpm"
        utils.separator(message)
        print(message)
        utils.separator(message)
        return True

    yes = utils.prompt_user('A newer version of MMPM is available. Would you like to upgrade now?')

    if not yes:
        return True

    original_dir = os.getcwd()

    message = "Upgrading MMPM"

    utils.separator(message)
    print(colored_text(colors.B_CYAN, message))
    utils.separator(message)

    log.logger.info(f'User chose to update MMPM with {original_dir} as the starting directory')

    os.chdir(os.path.join('/', 'tmp'))
    os.system('rm -rf /tmp/mmpm')

    return_code, _, stderr = utils.clone('mmpm', consts.MMPM_REPO_URL)

    if return_code:
        utils.error_msg(stderr)
        sys.exit(1)

    os.chdir('/tmp/mmpm')

    # if the user needs to be prompted for their password, this can't be a subprocess
    os.system('make reinstall')

    os.chdir(original_dir)
    log.logger.info(f'Changing back to original working directory: {original_dir}')

    return True


def upgrade_modules(modules: dict, modules_to_upgrade: List[str], assume_yes: bool = False):
    '''
    Depending on flags passed in as arguments:

    Checks for available module updates, and alerts the user. Or, pulls latest
    version of module(s) from the associated repos.

    If upgrading, a user can upgrade all modules that have available upgrades
    by ommitting additional arguments. Or, upgrade specific modules by
    supplying their case-sensitive name(s) as an addtional argument.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules
        update (bool): Flag to update modules
        upgrade (bool): Flag to upgrade modules
        modules_to_upgrade (List[str]): List of modules to update/upgrade

    Returns:
        None
    '''

    original_dir: str = os.getcwd()
    modules_dir: str = os.path.join(consts.MAGICMIRROR_ROOT, 'modules')
    os.chdir(modules_dir)

    installed_modules: dict = get_installed_modules(modules)

    updates_list: List[str] = []

    dirs: List[str] = os.listdir(modules_dir)

    if modules_to_upgrade:
        dirs = modules_to_upgrade

    for _, value in installed_modules.items():
        for index, _ in enumerate(value):
            if value[index][consts.TITLE] in dirs:
                title: str = value[index][consts.TITLE]
                curr_module_dir: str = os.path.join(modules_dir, title)
                os.chdir(curr_module_dir)

                utils.plain_print(f"Requesting upgrade for {title}")
                error_code, stdout, stderr = utils.run_cmd(["git", "pull"])

                if error_code:
                    utils.error_msg(stderr)
                    return False

                print(utils.done())

                if "Already up to date." in stdout:
                    print(stdout)
                    continue

                error_msg: str = utils.install_dependencies()

                if error_msg:
                    utils.error_msg(error_msg)
                    return False

            os.chdir(modules_dir)

    os.chdir(original_dir)

    #yes = utils.prompt_user('Are you sure you want to upgrade?', ['yes', 'y'], ['no', 'n'])

    return True


def check_for_module_updates(modules: dict):
    '''
    Depending on flags passed in as arguments:

    Checks for available module updates, and alerts the user. Or, pulls latest
    version of module(s) from the associated repos.

    If upgrading, a user can upgrade all modules that have available upgrades
    by ommitting additional arguments. Or, upgrade specific modules by
    supplying their case-sensitive name(s) as an addtional argument.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules
        update (bool): Flag to update modules
        upgrade (bool): Flag to upgrade modules
        modules_to_upgrade (List[str]): List of modules to update/upgrade

    Returns:
        None
    '''

    original_dir: str = os.getcwd()
    modules_dir: str = os.path.join(consts.MAGICMIRROR_ROOT, 'modules')
    os.chdir(modules_dir)

    installed_modules: dict = get_installed_modules(modules)

    updates_list: List[str] = []

    dirs: List[str] = os.listdir(modules_dir)

    for _, value in installed_modules.items():
        for index, _ in enumerate(value):
            if value[index][consts.TITLE] in dirs:
                title: str = value[index][consts.TITLE]
                curr_module_dir: str = os.path.join(modules_dir, title)
                os.chdir(curr_module_dir)

                utils.plain_print(f"Checking {title} for updates")
                return_code, _, stdout = utils.run_cmd(["git", "fetch", "--dry-run"])

                if return_code:
                    utils.error_msg('Unable to communicate with git server')
                    continue

                if stdout:
                    updates_list.append(title)

                print(utils.done())

                os.chdir(modules_dir)

    os.chdir(original_dir)

    if not updates_list:
        print(colored_text(colors.RESET, "No updates available"))
    else:
        utils.plain_print(colored_text(colors.B_MAGENTA, "Updates are available for the following modules:\n"))

        modules_with_updates = {'Modules': updates_list}

        for module in updates_list:
            print(f"{module}")

        read_mode = bool(os.stat(consts.MMPM_AVAILABLE_UPDATES_FILE).st_size)

        if not os.path.exists(consts.MMPM_AVAILABLE_UPDATES_FILE):
            return_code, stdout, stderr = utils.run_cmd(['touch', consts.MMPM_AVAILABLE_UPDATES_FILE])

            if return_code:
                utils.error_msg(stderr)
                sys.exit(1)

        # naming schem is not great here, but just leaving for the moment
        with open(consts.MMPM_AVAILABLE_UPDATES_FILE, 'r' if read_mode else 'w') as updates:
            if read_mode:
                data = json.load(updates)
            else:
                json.dump(updates_list, updates)

    return True


def search_modules(modules: dict, query: str, case_sensitive: bool = False, by_title_only: bool = False) -> dict:
    '''
    Used to search the 'modules' for either a category, or keyword/phrase
    appearing within module descriptions. If the argument supplied is a
    category name, all modules from that category will be listed. Otherwise,
    all modules whose descriptions contain the keyword/phrase will be
    displayed.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules
        query (str): Search query

    Returns:
        dict
    '''

    search_results: dict = {}

    if query in modules:
        return {query: modules[query]}

    search_results = defaultdict(list)

    if case_sensitive:
        not_a_match = lambda query, description, title, author : query not in description and query not in title and query not in author
    elif case_sensitive and by_title_only:
        not_a_match = lambda query, description, title, author : query not in title
    else:
        query = query.lower()
        not_a_match = lambda query, description, title, author : query not in description.lower() and query not in title.lower() and query not in author.lower()

    for category, _modules in modules.items():
        for module in _modules:
            if not_a_match(query, module[consts.DESCRIPTION], module[consts.TITLE], module[consts.AUTHOR]):
                continue

            search_results[category].append({
                consts.TITLE: module[consts.TITLE],
                consts.REPOSITORY: module[consts.REPOSITORY],
                consts.AUTHOR: module[consts.AUTHOR],
                consts.DESCRIPTION: module[consts.DESCRIPTION]
            })

    return search_results


def show_module_details(modules: List[defaultdict]) -> None:
    '''
    Used to display more detailed information that presented in normal search results

    Parameters:
        modules (List[defaultdict]): List of Categorized MagicMirror modules

    Returns:
        None
    '''

    for _, group in enumerate(modules):
        for category, _modules  in group.items():
            for module in _modules:
                print(colored_text(colors.N_GREEN, f'{module[consts.TITLE]}'))
                print(f'  Category: {category}')
                print(f'  Repository: {module[consts.REPOSITORY]}')
                print(f'  Author: {module[consts.AUTHOR]}')
                print(f'  Last Commit: ')
                print(indent(fill(f'Description: {module[consts.DESCRIPTION]}\n', width=70), prefix='  '), '\n')


def get_installation_candidates(modules: dict, modules_to_install: List[str]) -> list:
    '''
    Used to display more detailed information that presented in normal search results

    Parameters:
        modules (dict): MagicMirror modules database snapshot
        modules_to_install (List[str]): list of modules provided by user through command line arguments

    Returns:
        installation_candidates (List[dict]): list of modules whose module names match those of the modules_to_install
    '''

    installation_candidates: List[dict] = []

    for module_to_install in modules_to_install:
        for category in modules.values():
            for module in category:
                if module[consts.TITLE] == module_to_install:
                    log.logger.info(f'Matched {module[consts.TITLE]} to installation candidate')
                    installation_candidates.append(module)

    return installation_candidates


def __install_module__(module: dict, target: str, modules_dir: str, assume_yes: bool = False) -> bool:
    '''
    Used to display more detailed information that presented in normal search results

    Parameters:
        modules (dict): MagicMirror modules database snapshot
        modules_to_install (List[str]): list of modules provided by user through command line arguments

    Returns:
        installation_candidates (List[dict]): list of modules whose module names match those of the modules_to_install
    '''

    error_code, _, stderr = utils.clone(module[consts.TITLE], module[consts.REPOSITORY], target)

    if error_code:
        utils.warning_msg("\n" + stderr)
        return False

    print(utils.done())

    os.chdir(target)
    error: str = utils.install_dependencies()
    os.chdir('..')

    if error:
        utils.error_msg(error)
        failed_install_path = os.path.join(modules_dir, module[consts.TITLE])

        message: str = f"Failed to install {module[consts.TITLE]} at '{failed_install_path}'"

        if assume_yes:
            message = f'{message}. Removing directory due to --yes flag'
            utils.error_msg(message)
            log.logger.info(message)
            return False

        log.logger.info(message)

        yes = utils.prompt_user(f"{colored_text(colors.B_RED, 'ERROR:')} Failed to install {module[consts.TITLE]} at '{failed_install_path}'. Remove the directory?")

        if yes:
            message = f"User chose to remove {module[consts.TITLE]} at '{failed_install_path}'"
            utils.run_cmd(['rm', '-rf', failed_install_path], progress=False)
            print(f"\nRemoved '{failed_install_path}'\n")
        else:
            message = f"Keeping {module[consts.TITLE]} at '{failed_install_path}'"
            print(f'\n{message}\n')
            log.logger.info(message)

        return False
    return True


def install_modules(installation_candidates: dict, assume_yes: bool = False) -> bool:
    '''
    Compares list of 'modules_to_install' to modules found within the
    'modules', clones the repository within the ~/MagicMirror/modules
    directory, and runs 'npm install' for each newly installed module.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules
        modules_to_install (List[str]): List of modules to install

    Returns:
        bool: True upon success, False upon failure
    '''

    modules_dir: str = os.path.join(consts.MAGICMIRROR_ROOT, 'modules')

    if not os.path.exists(modules_dir):
        utils.error_msg(
            'MagicMirror directory not found in {const.MAGICMIRROR_ROOT}. ' +
            'If the MagicMirror root directory is elswhere, set the MMPM_MAGICMIRROR_ROOT env var to that location.'
        )
        return False

    if not installation_candidates:
        utils.error_msg('Unable to match query to installation candidates')
        return False


    log.logger.info(f'Changing into MagicMirror modules directory {modules_dir}')
    os.chdir(modules_dir)

    # a flag to check if any of the modules have installed. Used for displaying a message later
    successful_install: bool = False

    if not assume_yes:
        for index, candidate in enumerate(installation_candidates):
            prompt = f'The following package was matched as an installation candidate:'
            prompt += f' \n{colored_text(colors.N_GREEN, candidate[consts.TITLE])} ({candidate[consts.REPOSITORY]})\nInstall?'

            if not utils.prompt_user(prompt):
                log.logger.info(f'User not chose to install {candidate[consts.TITLE]}')
                installation_candidates[index] = {}
            else:
                log.logger.info(f'User chose to install {candidate[consts.TITLE]}')

            print('')

    for module in installation_candidates:
        if not module:
            continue

        title = module[consts.TITLE]
        target = os.path.join(os.getcwd(), title)
        repo = module[consts.REPOSITORY]

        if os.path.exists(target):
            os.chdir(target)

            return_code, remote_origin_url, stderr = utils.run_cmd(
                ['git', 'config', '--get', 'remote.origin.url'],
                progress=False
            )

            os.chdir('..')

            if return_code:
                utils.error_msg(stderr)
                continue

            if remote_origin_url.strip() == repo.strip():
                log.logger.info(f'Found a package named {title} already at {target}, with the same git remote origin url')

                if assume_yes:
                    utils.warning_msg(f'{title} appears to be installed already. Skipping alt installation option due to --yes flag')
                    log.logger.info(f'User used --yes. Skipping alt installation option for {title}')
                    continue

                yes = utils.prompt_user(
                    f'\n{title} appears to be installed already. Would you like to install {title} into a different target directory?'
                )

                if not yes:
                    utils.warning_msg(f'Skipping installation of {title}')
                    continue

                try:
                    print(f'\nOriginal target directory name: {title}')
                    new_target = input('New target directory name: ')
                    __install_module__(module, new_target, modules_dir)
                except KeyboardInterrupt:
                    print('\n')
                    utils.warning_msg(f'Cancelling installation of {title}')
                    continue

            else:
                log.logger.info(f'Found a package named {title} already at {target}, with a different git remote origin url')

                if assume_yes:
                    utils.warning_msg(f'A package named {title} is installed already. Skipping alt installation option due to --yes flag')
                    log.logger.info(f'User used --yes. Skipping alt installation option for {title}')
                    continue

                yes = utils.prompt_user(
                    f'\nA package named {title} is installed already.\nWould you like to provide a different installation path for the new package named {title}?'
                )

                if not yes:
                    utils.warning_msg(f'Skipping installation of {title}')
                    continue

                try:
                    print(f'\nOriginal target directory name: {title}')
                    new_target = input('New target directory name: ')
                    __install_module__(module, new_target, modules_dir)
                except KeyboardInterrupt:
                    print('\n')
                    utils.warning_msg(f'Cancelling installation of {title}')
                    continue

            continue

        if __install_module__(module, target, modules_dir) and not successful_install:
            successful_install = True
            print('')

    if not successful_install:
        return False

    print(f"\nThe installed modules may need additional configuring within '{consts.MAGICMIRROR_CONFIG_FILE}'")

    return True


def check_for_magicmirror_updates() -> bool:
    '''
    Checks for updates available to the MagicMirror repository. Alerts user if an upgrade is available.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules
        modules_to_install (List[str]): List of modules to install

    Returns:
        bool: True upon success, False upon failure
    '''
    if not os.path.exists(consts.MAGICMIRROR_ROOT):
        utils.error_msg(
            'MagicMirror directory not found in {const.MAGICMIRROR_ROOT}.' +
            'If the MagicMirror root directory is elswhere, set the MMPM_MAGICMIRROR_ROOT env var to that location.'
        )
        return False

    os.chdir(consts.MAGICMIRROR_ROOT)
    utils.plain_print('Checking for MagicMirror updates')

    # stdout and stderr are flipped for git commands...because that makes sense
    # except now stdout doesn't even contain error messages
    return_code, _, stdout = utils.run_cmd(['git', 'fetch', '--dry-run'])

    print(utils.done())

    if return_code:
        utils.error_msg('Unable to communicate with git server')
        return False

    if stdout:
        print(
            colored_text(colors.B_CYAN, 'An update is available for MagicMirror'),
            'Execute `mmpm upgrade --magicmirror` to perform the upgrade'
        )

    else:
        print('No updates found for MagicMirror')

    return True


def install_magicmirror(gui=False) -> bool:
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

    original_dir: str = os.getcwd()

    try:
        if not os.path.exists(consts.MAGICMIRROR_ROOT):
            print(
                colored_text(colors.B_CYAN, "MagicMirror directory not found."),
                "Installing MagicMirror..."
            )
            os.system('bash -c "$(curl -sL https://raw.githubusercontent.com/sdetweil/MagicMirror_scripts/master/raspberry.sh)"')

        else:
            if not gui:
                message = colored_text(colors.B_CYAN, "MagicMirror directory found.") + " Would you like to check for updates? [yes/no | y/n]: "

            valid_response = False

            while not valid_response:
                response: str = 'yes' if gui else input(message)

                if response in ("no", "n"):
                    print(colored_text(colors.B_MAGENTA, "Aborting MagicMirror update"))
                    break

                if response in ("yes", "y"):
                    os.chdir(consts.MAGICMIRROR_ROOT)

                    print(colored_text(colors.B_CYAN, "Checking for updates..."))
                    return_code, _, stdout = utils.run_cmd(['git', 'fetch', '--dry-run'])

                    if return_code:
                        utils.error_msg('Unable to communicate with git server')
                        break

                    if not stdout:
                        print("No updates available for MagicMirror.")
                        break

                    print(colored_text(colors.B_CYAN, "Updates found for MagicMirror."), "Requesting upgrades...")
                    error_code, _, stderr = utils.run_cmd(['git', 'pull'])

                    if error_code:
                        utils.error_msg(stderr)
                        return False

                    print(utils.done())
                    error_code, _, stderr = utils.npm_install()

                    if error_code:
                        utils.error_msg(stderr)
                        valid_response = True

                    print(utils.done())
                else:
                    utils.warning_msg("Respond with yes/no or y/n.")
    except Exception:
        return False

    os.chdir(original_dir)
    return True


def get_removal_candidates() -> list:
    return []


def remove_modules(modules: dict, modules_to_remove: List[str], assume_yes: bool = False) -> bool:
    '''
    Gathers list of modules currently installed in the ~/MagicMirror/modules
    directory, and removes each of the modules from the folder, if modules are
    currently installed. Otherwise, the user is shown an error message alerting
    them no modules are currently installed.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules
        modules_to_remove (list): List of modules to remove

    Returns:
        bool: True upon success, False upon failure
    '''

    installed_modules: dict = get_installed_modules(modules)

    if not installed_modules:
        utils.error_msg("No modules are currently installed.")
        return False

    modules_dir: str = os.path.join(consts.MAGICMIRROR_ROOT, 'modules')
    original_dir: str = os.getcwd()

    if not os.path.exists(modules_dir):
        msg = "Failed to find MagicMirror root. Have you installed MagicMirror properly? "
        msg += "You may also set the env variable 'MMPM_MAGICMIRROR_ROOT' to the MagicMirror root directory."
        utils.error_msg(msg)
        return False

    removal_candidates = get_removal_candidates()

    os.chdir(modules_dir)
    successful_removals: List[str] = []
    curr_dir: str = os.getcwd()

    for module in modules_to_remove:
        dir_to_rm: str = os.path.join(curr_dir, module)

        try:
            shutil.rmtree(dir_to_rm)
            successful_removals.append(module)
        except OSError:
            utils.warning_msg(f"The directory for '{module}' does not exist.")

    if successful_removals:
        print(colored_text(colors.B_GREEN, "The following modules were successfully deleted:"))

        for removal in successful_removals:
            print(colored_text(colors.RESET, f"{removal}"))
    else:
        utils.error_msg("Unable to remove modules.")
        return False

    os.chdir(original_dir)
    return True

def load_modules(force_refresh: bool = False) -> dict:
    '''
    Reads in modules from the hidden 'snapshot_file'  and checks if the file is
    out of date. If so, the modules are gathered again from the MagicMirror 3rd
    Party Modules wiki.

    Parameters:
        force_refresh (bool): Boolean flag to force refresh of snapshot

    Returns:
        bool: False upon failure
        modules (dict): list of modules upon success
    '''

    modules: dict = {}

    if not utils.assert_snapshot_directory():
        utils.error_msg('Failed to create directory for MagicMirror snapshot')
        sys.exit(1)

    # if the snapshot has expired, or doesn't exist, get a new one
    if force_refresh:
        utils.plain_print(utils.green_plus() + " Refreshing MagicMirror modules snapshot ... ")
        modules = retrieve_modules()

        # save the new snapshot
        with open(consts.SNAPSHOT_FILE, "w") as snapshot:
            json.dump(modules, snapshot)

        print(utils.done())

    else:
        with open(consts.SNAPSHOT_FILE, "r") as snapshot_file:
            modules = json.load(snapshot_file)

    if os.path.exists(consts.MMPM_EXTERNAL_SOURCES_FILE) and os.stat(consts.MMPM_EXTERNAL_SOURCES_FILE).st_size:
        try:
            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, "r") as f:
                modules[consts.EXTERNAL_MODULE_SOURCES] = json.load(f)[consts.EXTERNAL_MODULE_SOURCES]
        except Exception:
            utils.warning_msg(f'Failed to load data from {consts.MMPM_EXTERNAL_SOURCES_FILE}.')

    return modules


def retrieve_modules() -> dict:
    '''
    Scrapes the MagicMirror 3rd Party Wiki, and saves all modules along with
    their full, available descriptions in a hidden JSON file in the users home
    directory.

    Parameters:
        None

    Returns:
        modules (dict): list of modules upon success, None upon failure
    '''

    modules: dict = {}

    try:
        url = urlopen(consts.MAGICMIRROR_MODULES_URL)
        web_page = url.read()
    except HTTPError:
        utils.error_msg("Unable to retrieve MagicMirror modules. Is your internet connection down?")
        return {}

    soup = BeautifulSoup(web_page, "html.parser")
    table_soup: list = soup.find_all("table")

    category_soup: list = soup.find_all(attrs={"class": "markdown-body"})
    categories_soup: list = category_soup[0].find_all("h3")

    categories: list = []

    for index, _ in enumerate(categories_soup):
        last_element: object = len(categories_soup[index].contents) - 1
        new_category: object = categories_soup[index].contents[last_element]

        if new_category != "General Advice":
            #categories.append(re.sub(' // ', '/', new_category))
            categories.append(new_category)

    tr_soup: list = []

    for table in table_soup:
        tr_soup.append(table.find_all("tr"))

    for index, row in enumerate(tr_soup):
        modules.update({categories[index]: list()})

        for column_number, _ in enumerate(row):
            # ignore cells that literally say "Title", "Author", "Description"
            if column_number > 0:
                td_soup: list = tr_soup[index][column_number].find_all("td")

                title: str = consts.NOT_AVAILABLE
                repo: str = consts.NOT_AVAILABLE
                author: str = consts.NOT_AVAILABLE
                desc: str = consts.NOT_AVAILABLE

                for idx, _ in enumerate(td_soup):
                    if idx == 0:
                        for td in td_soup[idx]:
                            title = td.contents[0]

                        for a in td_soup[idx].find_all("a"):
                            if a.has_attr("href"):
                                repo = a["href"]

                        repo = str(repo)
                        title = str(title)

                    elif idx == 1:
                        for contents in td_soup[idx].contents:
                            if type(contents).__name__ == "Tag":
                                for tag in contents:
                                    author = tag.strip()
                            else:
                                author = contents

                        author = str(author)

                    else:
                        if contents:
                            desc = ""
                        for contents in td_soup[idx].contents:
                            if type(contents).__name__ == "Tag":
                                for content in contents:
                                    desc += content.string
                            else:
                                desc += contents.string

                modules[categories[index]].append({
                    consts.TITLE: utils.sanitize_name(title),
                    consts.REPOSITORY: repo,
                    consts.AUTHOR: author,
                    consts.DESCRIPTION: desc
                })

    return modules


def display_modules(modules: dict, list_categories: bool = False, table_formatted: bool = False) -> None:
    '''
    Depending on the user flags passed in from the command line, either all
    existing modules may be displayed, or the names of all categories of
    modules may be displayed.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules list_all
        list_categories (bool): Boolean flag to list categories

    Returns:
        None
    '''

    MAX_LENGTH: int = 80
    global_row: int = 1
    columns: int = 3
    rows: int = 1  # to include the header row

    if list_categories:

        if table_formatted:
            rows = len(modules.keys()) + 1
            columns = 2

            table = utils.allocate_table_memory(rows, columns)

            table[0][0] = to_bytes(consts.CATEGORY)
            table[0][1] = to_bytes('Modules')

            for key in modules.keys():
                table[global_row][0] = to_bytes(key)
                table[global_row][1] = to_bytes(str(len(modules[key])))

                global_row += 1

            utils.display_table(table, rows, columns)
        else:
            for key in modules.keys():
                print(colored_text(colors.N_GREEN, key), f'\n  Modules: {len(modules[key])}\n')
        return

    if table_formatted:
        for row in modules.values():
            rows += len(row)

        table = utils.allocate_table_memory(rows, columns)

        table[0][0] = to_bytes(consts.CATEGORY)
        table[0][1] = to_bytes(consts.TITLE)
        #table[0][2] = to_bytes(consts.REPOSITORY)
        #table[0][3] = to_bytes(consts.AUTHOR)
        table[0][2] = to_bytes(consts.DESCRIPTION)

        for category, _modules in modules.items():
            for index, module in enumerate(_modules):
                description = module[consts.DESCRIPTION][:MAX_LENGTH] + '...' if len(module[consts.DESCRIPTION]) > MAX_LENGTH else module[consts.DESCRIPTION]
                table[global_row][0] = to_bytes(category)
                table[global_row][1] = to_bytes(module[consts.TITLE])
                #table[global_row][2] = to_bytes(module[consts.REPOSITORY])
                #table[global_row][3] = to_bytes(module[consts.AUTHOR])
                table[global_row][2] = to_bytes(description)
                global_row += 1

        utils.display_table(table, rows, columns)

    else:
        MAX_LENGTH = 90

        for category, _modules in modules.items():
            for index, module in enumerate(_modules):
                print(colored_text(colors.N_GREEN, f'{module[consts.TITLE]}'))
                print(f"  {module[consts.DESCRIPTION][:MAX_LENGTH] + '...' if len(module[consts.DESCRIPTION]) > MAX_LENGTH else module[consts.DESCRIPTION]}")
                print(f'  Category: {category}\n')


def get_installed_modules(modules: dict) -> dict:
    '''
    Saves a list of all currently installed modules in the
    ~/MagicMirror/modules directory, and compares against the known modules
    from the MagicMirror 3rd Party Wiki.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules

    Returns:
        None upon failure
        installed_modules (dict): Dictionary of installed MagicMirror modules
    '''

    modules_dir: str = os.path.join(consts.MAGICMIRROR_ROOT, 'modules')
    original_dir: str = os.getcwd()

    if not os.path.exists(modules_dir):
        msg = "Failed to find MagicMirror root. Have you installed MagicMirror properly? "
        msg += "You may also set the env variable 'MMPM_MAGICMIRROR_ROOT' to the MagicMirror root directory."
        utils.error_msg(msg)
        return None

    os.chdir(modules_dir)

    module_dirs: List[str] = os.listdir(os.getcwd())

    installed_modules: dict = {}
    modules_found: dict = {'Modules': []}

    for module_dir in module_dirs:
        if not os.path.isdir(module_dir):
            continue

        try:
            os.chdir(os.path.join(modules_dir, module_dir))

            return_code, remote_origin_url, stderr = utils.run_cmd(
                ['git', 'config', '--get', 'remote.origin.url'],
                progress=False
            )

            return_code, project_name, stderr = utils.run_cmd(
                ['basename', remote_origin_url.strip(), '.git'],
                progress=False
            )

            modules_found['Modules'].append({
                consts.TITLE: project_name.strip(),
                consts.REPOSITORY: remote_origin_url.strip()
            })

        except Exception:
            utils.error_msg(stderr)

        finally:
            os.chdir('..')

    for category, module_names in modules.items():
        for module in module_names:
            for module_found in modules_found['Modules']:
                if module[consts.TITLE] == module_found[consts.TITLE] and module[consts.REPOSITORY] == module_found[consts.REPOSITORY]:
                    installed_modules.setdefault(category, []).append(module)

    os.chdir(original_dir)
    return installed_modules


def add_external_module(title: str = None, author: str = None, repo: str = None, desc: str = None) -> bool:
    '''
    Adds an external source for user to install a module from. This may be a
    private git repo, or a specific branch of a public repo. All modules added
    in this manner will be added to the 'External Module Sources' category.
    These sources are stored in ~/.config/mmpm/mmpm-external-sources.json

    Parameters:
        title (str): External source title
        author (str): External source author
        repo (str): External source repo url
        desc (str): External source description

    Returns:
        (bool): Upon success, a True result is returned
    '''

    print(colored_text(colors.B_GREEN, "Add new external module\n"))

    try:
        if not title:
            title = input('Title: ')
        else:
            print(f'Title: {title}')

        if not author:
            author = input('Author: ')
        else:
            print(f'Author: {author}')

        if not repo:
            repo = input('Repository: ')
        else:
            print(f'Repository: {repo}')

        if not desc:
            desc = input('Description: ')
        else:
            print(f'Description: {desc}')

    except KeyboardInterrupt:
        print('\n')
        sys.exit(1)

    new_source = {
        consts.TITLE: title,
        consts.REPOSITORY: repo,
        consts.AUTHOR: author,
        consts.DESCRIPTION: desc
    }

    try:
        if os.path.exists(consts.MMPM_EXTERNAL_SOURCES_FILE) and os.stat(consts.MMPM_EXTERNAL_SOURCES_FILE).st_size:
            config: dict = {}

            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
                config[consts.EXTERNAL_MODULE_SOURCES] = json.load(mmpm_ext_srcs)[consts.EXTERNAL_MODULE_SOURCES]

            for module in config[consts.EXTERNAL_MODULE_SOURCES]:
                if module[consts.TITLE] == title:
                    utils.error_msg(f"A module named '{title}' already exists. Please supply a unique name")
                    return False

            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'w') as mmpm_ext_srcs:
                config[consts.EXTERNAL_MODULE_SOURCES].append(new_source)
                json.dump(config, mmpm_ext_srcs)
        else:
            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'w') as mmpm_ext_srcs:
                json.dump({consts.EXTERNAL_MODULE_SOURCES: [new_source]}, mmpm_ext_srcs)

        print(colored_text(colors.B_WHITE, f"\nSuccessfully added {title} to '{consts.EXTERNAL_MODULE_SOURCES}'\n"))
    except IOError:
        utils.error_msg('Failed to save external module')
        return False
    return True


def remove_external_module_source(titles: str = None) -> bool:
    '''
    Allows user to remove an external source from the sources saved in
    ~/.config/mmpm/mmpm-external-sources.json

    Parameters:
        title (str): External source title

    Returns:
        (bool): Upon success, a True result is returned
    '''

    try:
        if os.path.exists(consts.MMPM_EXTERNAL_SOURCES_FILE) and os.stat(consts.MMPM_EXTERNAL_SOURCES_FILE).st_size:
            config: dict = {}
            successful_removals: list = []

            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
                config[consts.EXTERNAL_MODULE_SOURCES] = json.load(mmpm_ext_srcs)[consts.EXTERNAL_MODULE_SOURCES]

            for title in titles:
                for module in config[consts.EXTERNAL_MODULE_SOURCES]:
                    if module[consts.TITLE] == title:
                        config[consts.EXTERNAL_MODULE_SOURCES].remove(module)
                        successful_removals.append(module[consts.TITLE])

            if not successful_removals:
                utils.error_msg('No external sources found matching provided query')
                return False

            # if the error_msg was triggered, there's no need to even bother writing back to the file
            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'w') as mmpm_ext_srcs:
                json.dump(config, mmpm_ext_srcs)

            print(colored_text(colors.B_GREEN, f"Successfully removed {', '.join(successful_removals)} from '{consts.EXTERNAL_MODULE_SOURCES}'"))
    except IOError:
        utils.error_msg('Failed to remove external module')
        return False
    return True


def open_magicmirror_config() -> bool:
    '''
    Allows user to edit the MagicMirror config file using their $EDITOR

    Parameters:
        None

    Returns:
        bool: True upon success, False upon failure
    '''
    try:
        utils.open_default_editor(utils.get_file_path(consts.MAGICMIRROR_CONFIG_FILE))
        return True
    except Exception:
        utils.error_msg(f'{consts.MAGICMIRROR_CONFIG_FILE} not found. Is the MAGICMIRROR_ROOT env variable set?')
        return False


def get_active_modules(table_formatted: bool = False) -> None:

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

    if not os.path.exists(consts.MAGICMIRROR_CONFIG_FILE):
        utils.error_msg('MagicMirror config file not found. If this is a mistake, try setting the MMPM_MAGICMIRROR_ROOT env variable')
        sys.exit(1)

    temp_config: str = f'{consts.MAGICMIRROR_ROOT}/config/temp_config.js'
    shutil.copyfile(consts.MAGICMIRROR_CONFIG_FILE, temp_config)

    with open(temp_config, 'a') as temp:
        temp.write('console.log(JSON.stringify(config))')

    return_code, stdout, stderr = utils.run_cmd(['node', temp_config], progress=False)
    config: dict = json.loads(stdout.split('\n')[0])

    # using -f so any errors can be ignored
    utils.run_cmd(['rm', '-f', temp_config], progress=False)

    if 'modules' not in config or not config['modules']:
        utils.error_msg(f'No modules found in {consts.MAGICMIRROR_CONFIG_FILE}')

    if table_formatted:
        headers = [
            colored_text(colors.B_CYAN, 'Module'),
            colored_text(colors.B_CYAN, 'Status')
        ]

        ENABLED = colored_text(colors.B_GREEN, 'enabled')
        DISABLED = colored_text(colors.B_RED, 'disabled')

        rows: list = []

        for module_config in config['modules']:
            rows.append([
                module_config['module'],
                DISABLED if 'disabled' in module_config and module_config['disabled'] else ENABLED
            ])

        print(tabulate(rows, headers=headers, tablefmt='fancy_grid'))

    else:
        for module_config in config['modules']:
            print(
                colored_text(colors.N_GREEN, module_config['module']),
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

    mmpm_conf_path = '/etc/nginx/sites-enabled/mmpm.conf'

    if not os.path.exists(mmpm_conf_path):
        utils.error_msg('The MMPM nginx configuration file does not appear to exist. Is the GUI installed?')
        sys.exit(1)

    # this value needs to be retrieved dynamically in case the user modifies the nginx conf
    with open(mmpm_conf_path, 'r') as conf:
        mmpm_conf = conf.read()

    try:
        port: str = re.findall(r"listen\s?\d+", mmpm_conf)[0].split()[1]
    except IndexError:
        utils.error_msg('Unable to retrieve the port number of the MMPM web interface')
        sys.exit(1)

    return f'http://{gethostbyname(gethostname())}:{port}'


def open_mmpm_gui() -> bool:
    '''
    Attempts to open the MMPM web interface using 'xdg-open'

    Parameters:
        None

    Returns:
        bool: True upon sucess, False upon failure
    '''
    return_code, _, stderr = utils.run_cmd(['xdg-open', get_web_interface_url()], progress=False)

    if return_code:
        utils.error_msg(stderr)
        return False
    return True


def stop_magicmirror() -> None:
    '''
    Stops MagicMirror using pm2, if found, otherwise the associated
    processes are killed

    Parameters:
       None

    Returns:
        None
    '''
    if which('pm2'):
        log.logger.info("Using 'pm2' to stop MagicMirror")
        return_code, stdout, stderr = utils.run_cmd(['pm2', 'stop', 'MagicMirror'])
        log.logger.info(f'pm2 stdout: {stdout}')
        log.logger.info(f'pm2 stderr: {stderr}')
    else:
        utils.kill_magicmirror_processes()


def start_magicmirror() -> None:
    '''
    Launches MagicMirror using pm2, if found, otherwise a 'npm start' is run as
    a background process

    Parameters:
       None

    Returns:
        None
    '''
    log.logger.info('Starting MagicMirror')
    original_dir = os.getcwd()
    os.chdir(consts.MAGICMIRROR_ROOT)

    log.logger.info("Running 'npm start' in the background")

    if which('pm2'):
        log.logger.info("Using 'pm2' to start MagicMirror")
        return_code, stdout, stderr = utils.run_cmd(['pm2', 'start', 'MagicMirror'])
        log.logger.info(f'pm2 stdout: {stdout}')
        log.logger.info(f'pm2 stderr: {stderr}')
    else:
        log.logger.info("Using 'npm start' to start MagicMirror. Stdout/stderr capturing not possible in this case")
        os.system('npm start &')

    os.chdir(original_dir)


def restart_magicmirror() -> None:
    '''
    Restarts MagicMirror using pm2, if found, otherwise the associated
    processes are killed and 'npm start' is re-run a background process

    Parameters:
       None

    Returns:
        None
    '''
    if which('pm2'):
        log.logger.info("Using 'pm2' to restart MagicMirror")
        return_code, stdout, stderr = utils.run_cmd(['pm2', 'restart', 'MagicMirror'])
        log.logger.info(f'pm2 stdout: {stdout}')
        log.logger.info(f'pm2 stderr: {stderr}')
    else:
        stop_magicmirror()
        start_magicmirror()


def display_log_files(cli_logs: bool = False, gui_logs: bool = False, tail: bool = False) -> None:
    logs: List[str] = []

    if cli_logs:
        if os.path.exists(consts.MMPM_LOG_FILE):
            logs.append(consts.MMPM_LOG_FILE)
        else:
            utils.error_msg('MMPM log file not found')

    if gui_logs:
        if os.path.exists(consts.GUNICORN_LOG_ACCESS_LOG_FILE):
            logs.append(consts.GUNICORN_LOG_ACCESS_LOG_FILE)
        else:
            utils.error_msg('Gunicorn access log file not found')
        if os.path.exists(consts.GUNICORN_LOG_ERROR_LOG_FILE):
            logs.append(consts.GUNICORN_LOG_ERROR_LOG_FILE)
        else:
            utils.error_msg('Gunicorn error log file not found')

    if logs:
        os.system(f"{'tail -F' if tail else 'cat'} {' '.join(logs)}")

def display_mmpm_env_vars() -> None:
    for key, value in consts.MMPM_ENV_VARS.items():
        print(f'{key}={value}')
