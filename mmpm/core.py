#!/usr/bin/env python3
import re
import os
import json
import datetime
import shutil
import sys
from socket import gethostname, gethostbyname
from textwrap import fill, indent
from urllib.error import HTTPError
from urllib.request import urlopen
from collections import defaultdict
from bs4 import BeautifulSoup
from mmpm import color, utils, mmpm, consts
from mmpm.utils import colored_text
from typing import List, DefaultDict
from mmpm.utils import log, to_bytes
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
        colored_text(color.N_YELLOW, 'Most recent snapshot of MagicMirror Modules taken:'),
        f'{curr_snap_date}'
    )

    print(
        colored_text(color.N_YELLOW, 'The next snapshot will be taken on or after:'),
        f'{next_snap_date}\n'
    )

    print(
        colored_text(color.N_GREEN, 'Module Categories:'),
        f'{num_categories}'
    )

    print(
        colored_text(color.N_GREEN, 'Modules Available:'),
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
        log.info(f'Checking for newer version of MMPM. Current version: {mmpm.__version__}')
        utils.plain_print(f"Checking {colored_text(color.N_GREEN, 'MMPM')} for updates")

        # just to keep the console output the same as all other update commands
        return_code, contents, _ = utils.run_cmd(['curl', consts.MMPM_FILE_URL])

        if return_code:
            utils.fatal_msg('Failed to retrieve MMPM version number')

    except HTTPError as error:
        message: str = 'Unable to retrieve available version number from MMPM repository'
        utils.error_msg(message)
        log.error(error)
        return False

    version_line: List[str] = re.findall(r"__version__ = \d+\.\d+", contents)
    version_list: List[str] = re.findall(r"\d+\.\d+", version_line[0])
    version_number: float = float(version_list[0])

    print(utils.green_check_mark())

    if not version_number:
        utils.fatal_msg('No version number found on MMPM repository')

    if mmpm.__version__ >= version_number:
        print(f'No updates available for MMPM {colored_text(color.N_YELLOW, utils.yellow_x())}')
        log.info(f'No newer version of MMPM found > {version_number} available. The current version is the latest')
        return True

    log.info(f'Found newer version of MMPM: {version_number}')

    print(f'\nInstalled version: {mmpm.__version__}')
    print(f'Available version: {version_number}\n')

    if gui:
        message = f"A newer version of MMPM is available ({version_number}). Please upgrade via terminal using 'mmpm uprade --mmpm"
        utils.separator(message)
        print(message)
        utils.separator(message)
        return True

    if not utils.prompt_user('A newer version of MMPM is available. Would you like to upgrade now?', assume_yes=assume_yes):
        return True

    message = "Upgrading MMPM"

    utils.separator(message)
    print(colored_text(color.B_CYAN, message))
    utils.separator(message)

    log.info(f'User chose to update MMPM')

    os.chdir(os.path.join('/', 'tmp'))
    os.system('rm -rf /tmp/mmpm')

    return_code, _, stderr = utils.clone('mmpm', consts.MMPM_REPO_URL)

    if return_code:
        utils.fatal_msg(stderr)

    os.chdir('/tmp/mmpm')

    # if the user needs to be prompted for their password, this can't be a subprocess
    os.system('make reinstall')
    return True


def upgrade_module(module: dict):
    '''
    Depending on flags passed in as arguments:

    Checks for available module updates, and alerts the user. Or, pulls latest
    version of module(s) from the associated repos.

    If upgrading, a user can upgrade all modules that have available upgrades
    by ommitting additional arguments. Or, upgrade specific modules by
    supplying their case-sensitive name(s) as an addtional argument.

    Parameters:
        module (dict): the MagicMirror module being upgraded

    Returns:
        bool: True on success, False on failure
    '''

    original_dir: str = os.getcwd()
    modules_dir: str = os.path.join(consts.MAGICMIRROR_ROOT, 'modules')
    os.chdir(modules_dir)

    updates_list: List[str] = []

    dirs: List[str] = os.listdir(modules_dir)

    os.chdir(module[consts.DIRECTORY])
    utils.plain_print(f'{utils.green_plus()} Retrieving upgrade for {module[consts.TITLE]}')
    error_code, stdout, stderr = utils.run_cmd(["git", "pull"])

    if error_code:
        utils.error_msg(stderr)
        return False

    print(utils.green_check_mark())

    error_msg: str = utils.install_dependencies()

    if error_msg:
        utils.error_msg(error_msg)
        return False

    return True


def check_for_module_updates(modules: dict, assume_yes: bool = False):
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

    updateable: List[str] = []
    upgraded: bool = True

    dirs: List[str] = os.listdir(modules_dir)

    for _, modules in installed_modules.items():
        for module in modules:
            os.chdir(module[consts.DIRECTORY])

            utils.plain_print(f'Checking {colored_text(color.N_GREEN, module[consts.TITLE])} for updates')
            return_code, _, stdout = utils.run_cmd(['git', 'fetch', '--dry-run'])

            if return_code:
                utils.error_msg('Unable to communicate with git server')
                continue

            if stdout:
                updateable.append(module)

            print(utils.green_check_mark())


    if not updateable:
        print(f'No updates available for modules {colored_text(color.N_YELLOW, utils.yellow_x())}')
        return False

    print(f'\n{len(updateable)} updates are available\n')

    for module in updateable:
        if not utils.prompt_user(f'An upgrade is available for {module[consts.TITLE]}. Would you like to upgrade now?', assume_yes=assume_yes):
            upgraded = False
            continue

        if not upgrade_module(module):
            utils.error_msg('Unable to communicate with git server')

    if not upgraded:
        return False

    if utils.prompt_user('Would you like to restart MagicMirror now?', assume_yes=assume_yes):
        restart_magicmirror()

    return True


def search_modules(modules: dict, query: str, case_sensitive: bool = False, show: bool = False) -> dict:
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

    if query in modules:
        return {query: modules[query]}

    search_results = defaultdict(list)

    if show:
        not_a_match = lambda query, description, title, author: query != title
    elif case_sensitive:
        not_a_match = lambda query, description, title, author: query not in description and query not in title and query not in author
    else:
        query = query.lower()
        not_a_match = lambda query, description, title, author: query not in description.lower() and query not in title.lower() and query not in author.lower()

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


def show_module_details(modules: dict) -> None:
    '''
    Used to display more detailed information that presented in normal search results

    Parameters:
        modules (List[defaultdict]): List of Categorized MagicMirror modules

    Returns:
        None
    '''

    for category, _modules  in modules.items():
        for module in _modules:
            print(colored_text(color.N_GREEN, f'{module[consts.TITLE]}'))
            print(f'  Category: {category}')
            print(f'  Repository: {module[consts.REPOSITORY]}')
            print(f'  Author: {module[consts.AUTHOR]}')
            print(indent(fill(f'Description: {module[consts.DESCRIPTION]}\n', width=80), prefix='  '), '\n')


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
                    log.info(f'Matched {module[consts.TITLE]} to installation candidate')
                    installation_candidates.append(module)

    return installation_candidates


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

    log.info(f'Changing into MagicMirror modules directory {modules_dir}')
    os.chdir(modules_dir)

    # a flag to check if any of the modules have been installed. Used for displaying a message later
    successful_install: bool = False
    marked_for_installation: list = []

    match_count: int = len(installation_candidates)

    print(
        colored_text(
            color.N_CYAN,
            f"Matched query to {match_count} {'package' if match_count == 1 else 'packages'} \n"
        )
    )

    for index, candidate in enumerate(installation_candidates):
        if not utils.prompt_user(f'Install {colored_text(color.N_GREEN, candidate[consts.TITLE])} ({candidate[consts.REPOSITORY]})?', assume_yes=assume_yes):
            log.info(f'User not chose to install {candidate[consts.TITLE]}')
            installation_candidates[index] = {}
        else:
            log.info(f'User chose to install {candidate[consts.TITLE]} ({candidate[consts.REPOSITORY]})')

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

            remote_origin_url = remote_origin_url.strip()

            os.chdir('..')

            if return_code:
                utils.error_msg(stderr)
                continue

            if remote_origin_url == repo:
                log.info(f'Found a package named {title} already at {target}, with the same git remote origin url')

                if assume_yes:
                    utils.warning_msg(f'{title} ({repo}) appears to be installed already in {target}. Skipping alt installation option due to --yes flag')
                    log.info(f'User used --yes. Skipping alt installation option for {title} ({repo})')
                    continue

                yes = utils.prompt_user(
                    f'{title} ({repo}) appears to be installed already in {target}\nWould you like to provide an alternative directory name to install {title}?'
                )

                if not yes:
                    utils.warning_msg(f'Skipping installation of {title} ({repo})\n')
                    continue

                try:
                    target = utils.assert_valid_input(f'New directory name: ')
                except KeyboardInterrupt as error:
                    message = f'Cancelling installation of {title} ({repo})'
                    log.error(message)
                    utils.warning_msg(message + '\n')
                    continue
                finally:
                    print()

            else:
                log.info(f'Found a package named {title} already at {target}, with a different git remote origin url')

                if assume_yes:
                    utils.warning_msg(f'A package named {title} is already installed in {target}. Skipping alt installation option due to --yes flag')
                    log.info(f'User used --yes. Skipping alt installation option for {title}')
                    continue

                yes = utils.prompt_user(
                    f'A package named {title} is installed already in {target}\nWould you like to provide an alternative directory name to install {title}?'
                )

                if not yes:
                    utils.warning_msg(f'Skipping installation of {title} ({candidate[consts.REPOSITORY]})')
                    continue

                try:
                    target = utils.assert_valid_input(f'New directory name: ')
                except KeyboardInterrupt:
                    print()
                    message = f'Cancelling installation of {title}'
                    log.info(message)
                    utils.warning_msg(message)
                    continue

        if utils.install_module(module, target, modules_dir, assume_yes=assume_yes) and not successful_install:
            successful_install = True

    if not successful_install:
        return False

    print(f'Execute `mmpm open --config` to edit the configuration for newly installed modules')
    return True


def check_for_magicmirror_updates(assume_yes: bool = False) -> bool:
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
    utils.plain_print(f"Checking {colored_text(color.N_GREEN, 'MagicMirror')} for updates")

    # stdout and stderr are flipped for git command output, because that totally makes sense
    # except now stdout doesn't even contain error messages...thanks git
    return_code, _, stdout = utils.run_cmd(['git', 'fetch', '--dry-run'])

    print(utils.green_check_mark())

    if return_code:
        utils.error_msg('Unable to communicate with git server')
        return False

    if stdout:
        if not utils.prompt_user('An upgrade is available for MagicMirror. Would you like to upgrade now?', assume_yes=assume_yes):
            return False

        utils.plain_print('\nUpgrading MagicMirror')
        return_code, _, stdout = utils.run_cmd(['git', 'pull'])

        if return_code:
            utils.error_msg('Failed to communicate with git server')
            return False

        print(utils.green_check_mark(), '\n\nUpgrade complete!\n')

        if not utils.prompt_user('Would you like to restart MagicMirror now?', assume_yes=assume_yes):
            return False

        restart_magicmirror()

    else:
        print(f'No updates available for MagicMirror {colored_text(color.N_YELLOW, utils.yellow_x())}')

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

    if os.path.exists(consts.MAGICMIRROR_ROOT):
        utils.fatal_msg('MagicMirror is installed already')

    if utils.prompt_user(f"Use '{consts.HOME_DIR}' as the parent directory of the MagicMirror installation?"):
        parent = consts.HOME_DIR
    else:
        parent = os.path.abspath(input('Absolute path to MagicMirror parent directory: '))
        print(f'Please set the MMPM_MAGICMIRROR_ROOT env variable in your bashrc to {parent}/MagicMirror')

    os.chdir(parent)
    print(colored_text(color.N_CYAN, f'Installing MagicMirror in {parent}/MagicMirror ...'))
    os.system('bash -c "$(curl -sL https://raw.githubusercontent.com/sdetweil/MagicMirror_scripts/master/raspberry.sh)"')
    return True


def remove_modules(installed_modules: dict, modules_to_remove: List[str], assume_yes: bool = False) -> bool:
    '''
    Gathers list of modules currently installed in the ~/MagicMirror/modules
    directory, and removes each of the modules from the folder, if modules are
    currently installed. Otherwise, the user is shown an error message alerting
    them no modules are currently installed.

    Parameters:
        installed_modules (List[defaultdict]): List of dictionary of MagicMirror modules
        modules_to_remove (list): List of modules to remove
        assume_yes (bool): if True, all prompts are assumed to have a response of yes from the user

    Returns:
        bool: True upon success, False upon failure
    '''
    cancelled_removal: List[str] = []
    marked_for_removal: List[str] = []
    curr_dir: str = os.getcwd()

    modules_dir: str = os.path.join(consts.MAGICMIRROR_ROOT, 'modules')
    module_dirs: List[str] = os.listdir(modules_dir)

    try:
        for category, modules in installed_modules.items():
            for module in modules:
                dir_name = os.path.basename(module[consts.DIRECTORY])
                if dir_name in module_dirs and dir_name in modules_to_remove:
                    if utils.prompt_user(
                        f'Would you like to remove {colored_text(color.N_GREEN, module[consts.TITLE])} ({dir_name})?',
                        assume_yes=assume_yes
                    ):
                        marked_for_removal.append(dir_name)
                        log.info(f'User marked {dir_name} for removal')
                    else:
                        cancelled_removal.append(dir_name)
                        log.info(f'User chose not to remove {dir_name}')
    except KeyboardInterrupt:
        print()
        log.info('Caught keyboard interrupt during attempt to remove modules')
        return True

    for name in modules_to_remove:
        if name not in marked_for_removal and name not in cancelled_removal:
            utils.error_msg(f"No module named '{name}' found in {modules_dir}")
            log.info(f"User attemped to remove {name}, but no module named '{name}' was found in {modules_dir}")

    for dir_name in marked_for_removal:
        shutil.rmtree(dir_name)
        print(f'{utils.green_plus()} Removed {dir_name}')
        log.info(f'Removed {dir_name}')

    if marked_for_removal:
        print(f'Execute `mmpm open --config` to delete associated configurations of any removed modules')

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
        message: str = 'Failed to create directory for MagicMirror snapshot'
        log.error(message)
        utils.fatal_msg(message)

    # if the snapshot has expired, or doesn't exist, get a new one
    if force_refresh:
        utils.plain_print(utils.green_plus() + ' Refreshing MagicMirror modules snapshot ... ')
        modules = retrieve_modules()

        # save the new snapshot
        with open(consts.SNAPSHOT_FILE, 'w') as snapshot:
            json.dump(modules, snapshot)

        print(utils.green_check_mark())

    else:
        with open(consts.SNAPSHOT_FILE, 'r') as snapshot_file:
            modules = json.load(snapshot_file)

    if os.path.exists(consts.MMPM_EXTERNAL_SOURCES_FILE) and os.stat(consts.MMPM_EXTERNAL_SOURCES_FILE).st_size:
        try:
            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'r') as f:
                modules[consts.EXTERNAL_MODULE_SOURCES] = json.load(f)[consts.EXTERNAL_MODULE_SOURCES]
        except Exception as error:
            message = f'Failed to load data from {consts.MMPM_EXTERNAL_SOURCES_FILE}.'
            utils.warning_msg(message)
            log.error(message)

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
    except HTTPError as error:
        log.error(error)
        utils.error_msg('Unable to retrieve MagicMirror modules. Is your internet connection down?')
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
        modules.update({categories[index]: list()})

        for column_number, _ in enumerate(row):
            # ignore cells that literally say "Title", "Author", "Description"
            if column_number > 0:
                td_soup: list = tr_soup[index][column_number].find_all('td')

                title: str = consts.NOT_AVAILABLE
                repo: str = consts.NOT_AVAILABLE
                author: str = consts.NOT_AVAILABLE
                desc: str = consts.NOT_AVAILABLE

                for idx, _ in enumerate(td_soup):
                    if idx == 0:
                        for td in td_soup[idx]:
                            title = td.contents[0]

                        for a in td_soup[idx].find_all('a'):
                            if a.has_attr('href'):
                                repo = a['href']

                        repo = str(repo)
                        title = str(title)

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

                modules[categories[index]].append({
                    consts.TITLE: utils.sanitize_name(title).strip(),
                    consts.REPOSITORY: repo.strip(),
                    consts.AUTHOR: author.strip(),
                    consts.DESCRIPTION: desc.strip()
                })

    return modules


def get_module_categories(modules: dict) -> List[dict]:
    '''
    Wrapper method to build dictionary of module categories and the number of
    modules per category

    Parameters:
        modules (dict): the full modules database

    Returns:
        modules (List[dict]): list of dictionaries containing the category names and module count per category
    '''
    print(type(modules))
    return [{consts.CATEGORY: key, 'Modules': len(modules[key])} for key in modules.keys()]


def display_categories(categories: List[dict], table_formatted: bool = False) -> None:
    '''
    Prints module category names and the total number of modules in one of two
    formats. The default is similar to the Debian apt package manager, and the
    prettified table alternative

    Parameters:
        modules (List[dict]): list of dictionaries containing category names and module count
        table_formatted (bool): if True, the output is printed as a prettified table

    Returns:
        None
    '''
    MAX_LENGTH: int = 120

    if not table_formatted:
        for category in categories:
            print(
                colored_text(color.N_GREEN, category[consts.CATEGORY]),
                f'\n  Modules: {category[consts.MODULES]}\n'
            )
        return

    global_row: int = 1
    columns: int = 2
    rows = len(categories) + 1  # to include the header row

    table = utils.allocate_table_memory(rows, columns)
    table[0][0], table[0][1] = to_bytes(consts.CATEGORY), to_bytes(consts.MODULES)

    for category in categories:
        table[global_row][0] = to_bytes(category[consts.CATEGORY])
        table[global_row][1] = to_bytes(str(category[consts.MODULES]))
        global_row += 1

    utils.display_table(table, rows, columns)


def display_modules(modules: dict, table_formatted: bool = False, include_path: bool = False) -> None:
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
    format_description = lambda desc : desc[:MAX_LENGTH] + '...' if len(desc) > MAX_LENGTH else desc
    MAX_LENGTH: int = 120

    if table_formatted:
        columns: int = 2
        global_row: int = 1
        rows: int = 1  # to include the header row

        for row in modules.values():
            rows += len(row)

        if include_path:
            columns += 1
            MAX_LENGTH = 80

        table = utils.allocate_table_memory(rows, columns)

        table[0][0] = to_bytes(consts.TITLE)
        table[0][1] = to_bytes(consts.DESCRIPTION)

        if include_path:
            table[0][2] =  to_bytes(consts.DIRECTORY)

            def __fill_row__(table, row, module):
                table[row][0] = to_bytes(module[consts.TITLE])
                table[row][1] = to_bytes(format_description(module[consts.DESCRIPTION]))
                table[row][2] =  to_bytes(os.path.basename(module[consts.DIRECTORY]))
        else:
            def __fill_row__(table, row, module):
                table[row][0] = to_bytes(module[consts.TITLE])
                table[row][1] = to_bytes(format_description(module[consts.DESCRIPTION]))

        for category, _modules in modules.items():
            for index, module in enumerate(_modules):
                __fill_row__(table, global_row, module)
                global_row += 1

        utils.display_table(table, rows, columns)

    else:
        if include_path:
            _print_ = lambda module : print(
                colored_text(color.N_GREEN, f'{module[consts.TITLE]}'),
                (f'\n  Directory: {os.path.basename(module[consts.DIRECTORY])}'),
                (f"\n  {format_description(module[consts.DESCRIPTION])}\n")
            )

        else:
            _print_ = lambda module : print(
                colored_text(color.N_GREEN, f'{module[consts.TITLE]}'),
                (f"\n  {format_description(module[consts.DESCRIPTION])}\n")
            )

        for category, _modules in modules.items():
            for index, module in enumerate(_modules):
                _print_(module)


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
                consts.REPOSITORY: remote_origin_url.strip(),
                consts.DIRECTORY: os.getcwd()
            })

        except Exception as error:
            log.error(error)
            utils.error_msg(stderr)

        finally:
            os.chdir('..')

    for category, module_names in modules.items():
        installed_modules.setdefault(category, [])
        for module in module_names:
            for module_found in modules_found['Modules']:
                if module[consts.REPOSITORY] == module_found[consts.REPOSITORY]:
                    installed_modules[category].append({
                        consts.TITLE: module[consts.TITLE],
                        consts.REPOSITORY: module[consts.REPOSITORY],
                        consts.AUTHOR: module[consts.AUTHOR],
                        consts.DESCRIPTION: module[consts.DESCRIPTION],
                        consts.DIRECTORY: module_found[consts.DIRECTORY]
                    })

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
    try:
        if not title:
            title = utils.assert_valid_input('Title: ')
        else:
            print(f'Title: {title}')

        if not author:
            author = utils.assert_valid_input('Author: ')
        else:
            print(f'Author: {author}')

        if not repo:
            repo = utils.assert_valid_input('Repository: ')
        else:
            print(f'Repository: {repo}')

        if not desc:
            desc = utils.assert_valid_input('Description: ')
        else:
            print(f'Description: {desc}')

    except KeyboardInterrupt as error:
        print()
        log.error(error)
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

            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'w') as mmpm_ext_srcs:
                config[consts.EXTERNAL_MODULE_SOURCES].append(new_source)
                json.dump(config, mmpm_ext_srcs)
        else:
            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'w') as mmpm_ext_srcs:
                json.dump({consts.EXTERNAL_MODULE_SOURCES: [new_source]}, mmpm_ext_srcs)

        print(colored_text(color.N_GREEN, f"\nSuccessfully added {title} to '{consts.EXTERNAL_MODULE_SOURCES}'\n"))

    except IOError as error:
        utils.error_msg('Failed to save external module')
        log.error(error)
        return False

    return True


def remove_external_module_source(titles: str = None, assume_yes: bool = False) -> bool:
    '''
    Allows user to remove an external source from the sources saved in
    ~/.config/mmpm/mmpm-external-sources.json

    Parameters:
        title (str): External source title

    Returns:
        (bool): Upon success, a True result is returned
    '''

    if not os.path.exists(consts.MMPM_EXTERNAL_SOURCES_FILE):
        utils.fatal_msg(f'{consts.MMPM_EXTERNAL_SOURCES_FILE} does not appear to exist')

    elif not os.stat(consts.MMPM_EXTERNAL_SOURCES_FILE).st_size:
        utils.fatal_msg(f'{consts.MMPM_EXTERNAL_SOURCES_FILE} is empty')

    modules: dict = {}
    marked_for_removal: list = []
    cancelled_removal: list = []

    with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
        modules[consts.EXTERNAL_MODULE_SOURCES] = json.load(mmpm_ext_srcs)[consts.EXTERNAL_MODULE_SOURCES]

    if not modules[consts.EXTERNAL_MODULE_SOURCES]:
        utils.fatal_msg('No external modules found in database')

    for title in titles:
        for module in modules[consts.EXTERNAL_MODULE_SOURCES]:
            if module[consts.TITLE] == title:
                if utils.prompt_user(
                    f'Would you like to remove {colored_text(color.N_GREEN, title)} ({module[consts.REPOSITORY]}) from the MMPM/MagicMirror local database?',
                    assume_yes=assume_yes
                ):
                    marked_for_removal.append(module)
                else:
                    cancelled_removal.append(module)

    if not marked_for_removal and not cancelled_removal:
        utils.error_msg('No external sources found matching provided query')
        return False

    for module in marked_for_removal:
        modules[consts.EXTERNAL_MODULE_SOURCES].remove(module)
        print(f'{utils.green_plus()} Removed {module[consts.TITLE]} ({module[consts.REPOSITORY]})')

    # if the error_msg was triggered, there's no need to even bother writing back to the file
    with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'w') as mmpm_ext_srcs:
        json.dump(modules, mmpm_ext_srcs)

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
    except Exception:
        utils.error_msg(f'{consts.MAGICMIRROR_CONFIG_FILE} not found. Is the MAGICMIRROR_ROOT env variable set?')
        return False

    return True

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
        utils.fatal_msg('MagicMirror config file not found. If this is a mistake, try setting the MMPM_MAGICMIRROR_ROOT env variable')

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

    if not table_formatted:
        for module_config in config['modules']:
            print(
                colored_text(color.N_GREEN, module_config['module']),
                f"\n  Status: {'disabled' if 'disabled' in module_config and module_config['disabled'] else 'enabled'}\n"
            )
        return

    global_row: int = 1
    columns: int = 2
    rows: int = 1  # to include the header row

    rows = len(config['modules']) + 1

    table = utils.allocate_table_memory(rows, columns)

    table[0][0] = to_bytes('Module')
    table[0][1] = to_bytes('Status')

    for module_config in config['modules']:
        table[global_row][0] = to_bytes(module_config['module'])
        table[global_row][1] = to_bytes('disabled') if 'disabled' in module_config and module_config['disabled'] else to_bytes('enabled')
        global_row += 1

    utils.display_table(table, rows, columns)


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
        utils.fatal_msg('The MMPM nginx configuration file does not appear to exist. Is the GUI installed?')

    # this value needs to be retrieved dynamically in case the user modifies the nginx conf
    with open(mmpm_conf_path, 'r') as conf:
        mmpm_conf = conf.read()

    try:
        port: str = re.findall(r"listen\s?\d+", mmpm_conf)[0].split()[1]
    except IndexError:
        utils.fatal_msg('Unable to retrieve the port number of the MMPM web interface')

    return f'http://{gethostbyname(gethostname())}:{port}'


def open_mmpm_gui() -> bool:
    '''
    Attempts to open the MMPM web interface using 'xdg-open'

    Parameters:
        None

    Returns:
        bool: True upon sucess, False upon failure
    '''
    return_code, _, stderr = utils.run_cmd(['xdg-open', get_web_interface_url()], background=True)

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
    if shutil.which('pm2'):
        log.info("Using 'pm2' to stop MagicMirror")
        return_code, stdout, stderr = utils.run_cmd([
            'pm2', 'stop', consts.MMPM_ENV_VARS[consts.MAGICMIRROR_PM2_PROC]],
            progress=False
        )

        if stderr:
            log.error(stderr)
            utils.error_msg(f'{stderr.strip()}. Is the MAGICMIRROR_PM2_PROC env variable set correctly?')
        else:
            log.info('stopped MagicMirror using PM2')
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
    log.info('Starting MagicMirror')
    original_dir = os.getcwd()
    os.chdir(consts.MAGICMIRROR_ROOT)

    log.info("Running 'npm start' in the background")

    if shutil.which('pm2'):
        log.info("Using 'pm2' to start MagicMirror")
        return_code, stdout, stderr = utils.run_cmd(
            ['pm2', 'start', consts.MMPM_ENV_VARS[consts.MAGICMIRROR_PM2_PROC]],
            progress=False
        )

        if stderr:
            log.error(stderr)
            utils.error_msg(f'{stderr.strip()}. Is the MAGICMIRROR_PM2_PROC env variable set correctly?')
        else:
            log.info('started MagicMirror using PM2')
    else:
        log.info("Using 'npm start' to start MagicMirror. Stdout/stderr capturing not possible in this case")
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
    if shutil.which('pm2'):
        log.info("Using 'pm2' to restart MagicMirror")
        return_code, stdout, stderr = utils.run_cmd(
            ['pm2', 'restart', consts.MMPM_ENV_VARS[consts.MAGICMIRROR_PM2_PROC]],
            progress=False
        )

        if stderr:
            log.error(stderr)
            utils.error_msg(f'{stderr.strip()}. Is the MAGICMIRROR_PM2_PROC env variable set correctly?')
        else:
            log.info('restarted MagicMirror using PM2')

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


def install_autocompletion() -> None:
    '''
    Adds appropriate autocompletion configuration to a user's shell
    configuration file. Detects configuration files for bash, zsh, fish,
    and tcsh

    Parameters:
       None

    Returns:
        None
    '''
    log.info('user attempting to install MMPM autocompletion')
    shell: str = os.environ['SHELL']
    log.info(f'detected user shell to be {shell}')
    autocomplete_url: str = 'https://github.com/kislyuk/argcomplete#activating-global-completion'
    error_message: str = f'Please see {autocomplete_url} for help installing autocompletion'
    complete_message = lambda config : f'Autocompletion installed. Please source {config} for the changes to take effect'
    failed_match_message = lambda shell, configs : f'Unable to locate {shell} configuration file (looked for {configs}). {error_message}'

    def __match_shell_config__(configs: List[str]) -> str:
        log.info(f'searching for one of the following shell configuration files {configs}')
        for config in configs:
            config = os.path.join(consts.HOME_DIR, config)
            if os.path.exists(config):
                log.info(f'found {config} shell configuration file for {shell}')
                return config
        return ''

    def __echo_and_eval__(command: str) -> None:
        log.info(f'executing {command} to install autocompletion')
        print(f'{utils.green_plus()} {colored_text(color.N_GREEN, command)}')
        os.system(command)

    if 'bash' in shell:
        files = ['.bashrc', '.bash_profile', '.bash_login', '.profile']
        config = __match_shell_config__(files)

        if not config:
            utils.fatal_msg(failed_match_message('bash', files))

        __echo_and_eval__(f'echo \'eval "$(register-python-argcomplete mmpm)"\' >> {config}')
        print(complete_message(config))

    elif 'zsh' in shell:
        files = ['.zshrc', '.zprofile', '.zshenv', '.zlogin', '.profile']
        config = __match_shell_config__(files)

        if not config:
            utils.fatal_msg(failed_match_message('zsh', files))

        __echo_and_eval__(f"echo 'autoload -U bashcompinit' >> {config}")
        __echo_and_eval__(f"echo 'bashcompinit' >> {config}")
        __echo_and_eval__(f'echo \'eval "$(register-python-argcomplete mmpm)"\' >> {config}')
        print(complete_message(config))

    elif 'tcsh' in shell:
        files = ['.tcshrc', '.cshrc', '.login']
        config = __match_shell_config__(files)

        if not config:
            utils.fatal_msg(failed_match_message('tcsh', files))

        __echo_and_eval__(f"echo 'eval `register-python-argcomplete --shell tcsh mmpm`' >> {config}")
        print(complete_message(config))

    elif 'fish' in shell:
        files = ['.config/fish/config.fish']
        config = __match_shell_config__(files)

        if not config:
            utils.fatal_msg(failed_match_message('fish', files))

        __echo_and_eval__(f"register-python-argcomplete --shell fish mmpm >> {config}")
        print(complete_message(config))

    else:
        utils.fatal_msg(f'Unable install autocompletion for SHELL ({shell}). Please see {autocomplete_url} for help installing autocomplete')
