#!/usr/bin/env python3
import re
import os
import json
import datetime
import shutil
import sys
from socket import gethostname, gethostbyname
from textwrap import fill
from tabulate import tabulate
from urllib.error import HTTPError
from urllib.request import urlopen
from collections import defaultdict
from bs4 import BeautifulSoup
from mmpm import colors, utils, mmpm, consts
from typing import List
from mmpm.utils import log
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

    print(colors.B_YELLOW + "Most recent snapshot of MagicMirror Modules taken" + colors.B_WHITE + f": {curr_snap_date}")
    print(colors.B_YELLOW + "The next snapshot will be taken on or after" + colors.B_WHITE + f": {next_snap_date}\n")
    print(colors.B_GREEN + "Module Categories" + colors.B_WHITE + f": {num_categories}")
    print(colors.B_GREEN + "Modules Available" + colors.B_WHITE + f": {num_modules}\n")



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
        log.logger.info(f'Checking for MMPM enhancements. Current version: {mmpm.__version__}')

        MMPM_FILE = urlopen(consts.MMPM_FILE_URL)
        contents: str = str(MMPM_FILE.read())

        version_line: List[str] = re.findall(r"__version__ = \d+\.\d+", contents)
        version_list: List[str] = re.findall(r"\d+\.\d+", version_line[0])
        version_number: float = float(version_list[0])

        if version_number and mmpm.__version__ < version_number:
            log.logger.info(f'Found newer version of MMPM: {version_number}')
            valid_response = False

            if gui:
                print(f'Currently installed version: {mmpm.__version__}')
                print(f'Available version: {version_number}\n')
                message = f"A newer version of MMPM is available ({version_number}). Please upgrade via terminal using 'mmpm -e'"
                utils.separator(message)
                print(message)
                utils.separator(message)
                return True

            print(utils.done())

            while not valid_response:
                print(f'\nCurrently installed version: {mmpm.__version__}')
                print(f'Available version: {version_number}\n')

                response = "yes" if assume_yes else input(
                    colors.B_GREEN + "A newer version of MMPM is available\n\n" +
                    colors.RESET + "Would you like to upgrade now?" + colors.B_WHITE + " [yes/y | no/n]: " +
                    colors.RESET
                )

                if response in ("yes", "y"):
                    valid_response = True
                    original_dir = os.getcwd()

                    message = "Upgrading MMPM"

                    utils.separator(message)
                    print(colors.B_CYAN + message + colors.RESET)
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

                elif response in ("no", "n"):
                    valid_response = True
                else:
                    utils.warning_msg("Respond with yes/no or y/n.")
        else:
            print(utils.done())
            print("\nNo enhancements available for MMPM. You have the latest version.")
            log.logger.info('No newer version of MMPM available')
            return False
        return True
    except HTTPError:
        return False



def enhance_modules(modules: dict, update: bool = False, upgrade: bool = False, modules_to_upgrade: List[str] = None) -> bool:
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

    if upgrade and modules_to_upgrade:
        dirs = modules_to_upgrade


    for _, value in installed_modules.items():
        for index, _ in enumerate(value):
            if value[index][consts.TITLE] in dirs:
                title: str = value[index][consts.TITLE]
                curr_module_dir: str = os.path.join(modules_dir, title)
                os.chdir(curr_module_dir)

                if update:
                    utils.plain_print(f"Checking {title} for updates")
                    error_code, stdout, stderr = utils.run_cmd(["git", "fetch", "--dry-run"])

                    if error_code:
                        utils.error_msg(stderr)
                        return False

                    if stdout:
                        updates_list.append(title)

                    print(utils.done())

                elif upgrade:
                    utils.plain_print(f"Requesting upgrade for {title}")
                    error_code, stdout, stderr = utils.run_cmd(["git", "pull"])

                    if error_code:
                        utils.error_msg(stderr)
                        return False

                    print(utils.done())

                    if "Already up to date." in stdout:
                        print(stdout)
                        continue

                    error_msg: str = utils.handle_installation_process()

                    if error_msg:
                        utils.error_msg(error_msg)
                        return False

                os.chdir(modules_dir)

    os.chdir(original_dir)

    if update:
        if not updates_list:
            utils.plain_print(colors.RESET + "\nNo updates available.\n")
        else:
            utils.plain_print(colors.B_MAGENTA + "Updates are available for the following modules:\n" + colors.RESET)
            for module in updates_list:
                print(f"{module}")
    return True

def search_modules(modules: dict, query: str) -> dict:
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
    query = query.lower()

    for category, _modules in modules.items():
        for module in _modules:
            if query not in module[consts.DESCRIPTION].lower() and query not in module[consts.TITLE].lower() and query not in module[consts.AUTHOR].lower():
                continue

            search_results[category].append({
                consts.TITLE: module[consts.TITLE],
                consts.REPOSITORY: module[consts.REPOSITORY],
                consts.AUTHOR: module[consts.AUTHOR],
                consts.DESCRIPTION: module[consts.DESCRIPTION]
            })

    return search_results


def install_modules(modules: dict, modules_to_install: List[str]) -> bool:
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
        msg = "Failed to find MagicMirror root. Have you installed MagicMirror properly? "
        msg += "You may also set the env variable 'MMPM_MAGICMIRROR_ROOT' to the MagicMirror root directory."
        utils.error_msg(msg)
        return False

    log.logger.info(f'User selected modules to install: {modules_to_install}')
    log.logger.info(f'Changing into MagicMirror modules directory {modules_dir}')

    os.chdir(modules_dir)

    successful_installs: List[str] = []
    existing_modules: List[str] = []
    failed_installs: List[str] = []

    for module_to_install in modules_to_install:
        install_next: bool = False

        for category in modules.values():
            for module in category:
                if module[consts.TITLE] == module_to_install:
                    log.logger.info(f'Matched {module[consts.TITLE]} to installation candidate')
                    title = module[consts.TITLE]
                    target = os.path.join(os.getcwd(), title)
                    repo = module[consts.REPOSITORY]

                    try:
                        os.mkdir(target)
                    except OSError:
                        log.logger.info(f'Found {title} already in {os.getcwd()}. Skipping.')
                        utils.warning_msg(f"The module {title} is already installed. To remove the module, run 'mmpm -r {title}'")
                        existing_modules.append(title)
                        install_next = True
                        continue

                    os.chdir(target)

                    message = f"Installing {title} @ {target}"
                    utils.separator(message)

                    print(colors.RESET + "Installing " + colors.B_CYAN + f"{title}" + colors.B_YELLOW + " @ " + colors.RESET + f"{target}")

                    utils.separator(message)
                    error_code, _, stderr = utils.clone(title, repo, target)

                    if error_code:
                        utils.warning_msg("\n" + stderr)
                        failed_installs.append(title)
                        install_next = True
                        continue

                    print(utils.done())
                    error: str = utils.handle_installation_process()

                    if error:
                        utils.error_msg(error)
                        failed_install_path = os.path.join(modules_dir, title)
                        message = f"Failed to install {title}, removing the directory: '{failed_install_path}'"
                        utils.error_msg(message)
                        log.logger.info(message)
                        failed_installs.append(title)
                        utils.run_cmd(['rm', '-rf', failed_install_path], progress=False)

                    else:
                        successful_installs.append(title)

                    os.chdir(modules_dir)
                    install_next = True
                    break

            if install_next:
                break

    for module in modules_to_install:
        if module not in successful_installs and module not in existing_modules and module not in failed_installs:
            utils.warning_msg(f"Unable to match '{module}' with installation candidate. Is the casing correct?")

    if successful_installs:
        print(colors.B_WHITE + f"\nThe installed modules may need additional configuring within '{consts.MAGICMIRROR_CONFIG_FILE}'" + colors.RESET)
        return True

    return False


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
            print(colors.B_CYAN + "MagicMirror directory not found. " + colors.RESET + "Installing MagicMirror..." + colors.RESET)
            os.system('bash -c "$(curl -sL https://raw.githubusercontent.com/sdetweil/MagicMirror_scripts/master/raspberry.sh)"')

        else:
            if not gui:
                message = colors.B_CYAN + "MagicMirror directory found. " + colors.RESET + "Would you like to check for updates? [yes/no | y/n]: "

            valid_response = False

            while not valid_response:
                response: str = 'yes' if gui else input(message)

                if response in ("no", "n"):
                    print(colors.B_MAGENTA + "Aborting MagicMirror update")
                    break

                if response in ("yes", "y"):
                    os.chdir(consts.MAGICMIRROR_ROOT)

                    print(colors.B_CYAN + "Checking for updates..." + colors.RESET)
                    return_code, stdout, stderr = utils.run_cmd(['git', 'fetch', '--dry-run'])

                    if return_code:
                        utils.error_msg(stderr)
                        break

                    if not stdout:
                        print("No updates available for MagicMirror.")
                        break

                    print(colors.B_CYAN + "Updates found for MagicMirror. " + colors.RESET + "Requesting upgrades...")
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


def remove_modules(modules: dict, modules_to_remove: List[str]) -> bool:
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
        print(colors.B_GREEN + "The following modules were successfully deleted:" + colors.N)

        for removal in successful_removals:
            print(colors.RESET + f"{removal}")
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
        utils.plain_print(utils.green_plus() + " Refreshing MagicMirror module snapshot ... ")
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


def display_modules(modules: dict, list_categories: bool = False) -> None:
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

    if list_categories:
        rows: List[str] = [
            [
                bytes(colors.B_CYAN + "Category", 'utf-8'),
                bytes(colors.B_CYAN + "Modules" + colors.RESET, 'utf-8')
            ]
        ]

        rows: List[List[object]] = [[key, len(modules[key])] for key in modules.keys()]
        utils.display_table(rows)
        return

    rows = [
        [
            bytes(colors.B_CYAN + "Category", 'utf-8'),
            bytes(consts.TITLE, 'utf-8'),
            bytes(consts.REPOSITORY, 'utf-8'),
            bytes(consts.AUTHOR, 'utf-8'),
            bytes(consts.DESCRIPTION + colors.RESET, 'utf-8')
        ]
    ]

    MAX_LENGTH: int = 66

    rows = 0

    for value in modules.values():
        rows += len(value)

    #table = utils.create_table(rows=rows, columns=len(rows[0]))

    #for i, row in enumerate(data):
    #    for j, column in enumerate(data[i]):
    #        table[i][j] = data[i][j]


    for category, _modules in modules.items():
        for module in _modules:
            rows.append([
                bytes(category, 'utf-8'),
                bytes(module[consts.TITLE], 'utf-8'),
                bytes(module[consts.REPOSITORY], 'utf-8'),
                bytes(module[consts.AUTHOR], 'utf-8'),
                bytes(module[consts.DESCRIPTION][:MAX_LENGTH] + '...' if len(module[consts.DESCRIPTION]) > MAX_LENGTH else module[consts.DESCRIPTION], 'utf-8')
            ])

    utils.display_table(rows)


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

    for category, module_names in modules.items():
        for module in module_names:
            if module[consts.TITLE] in module_dirs:
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

    print(colors.B_GREEN + "Register external module source\n" + colors.RESET)

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
                config[consts.EXTERNAL_MODULE_SOURCES] = json.load(
                    mmpm_ext_srcs)[consts.EXTERNAL_MODULE_SOURCES]

            for module in config[consts.EXTERNAL_MODULE_SOURCES]:
                if module[consts.TITLE] == title:
                    utils.error_msg(f"A module named '{title}' already exists")
                    return False

            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'w') as mmpm_ext_srcs:
                config[consts.EXTERNAL_MODULE_SOURCES].append(new_source)
                json.dump(config, mmpm_ext_srcs)
        else:
            with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'w') as mmpm_ext_srcs:
                json.dump({consts.EXTERNAL_MODULE_SOURCES: [new_source]}, mmpm_ext_srcs)

        print(colors.B_WHITE + f"\nSuccessfully added {title} to '{consts.EXTERNAL_MODULE_SOURCES}'\n" + colors.RESET)
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

            print(colors.B_GREEN + f"Successfully removed {', '.join(successful_removals)} from '{consts.EXTERNAL_MODULE_SOURCES}'" + colors.RESET)
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


def get_active_modules() -> None:

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
        utils.error_msg('MagicMirror config file not found')
        sys.exit(1)

    dummy_config: str = f'{consts.MAGICMIRROR_ROOT}/config/dummy_config.js'
    shutil.copyfile(consts.MAGICMIRROR_CONFIG_FILE, dummy_config)

    with open(dummy_config, 'a') as dummy:
        dummy.write('console.log(JSON.stringify(config))')

    return_code, stdout, stderr = utils.run_cmd(['node', dummy_config], progress=False)
    config: dict = json.loads(stdout.split('\n')[0])

    # using -f so any errors can be ignored
    utils.run_cmd(['rm', '-f', dummy_config], progress=False)

    headers = [
        colors.B_CYAN + 'Module' + colors.RESET,
        colors.B_CYAN + 'Status' + colors.RESET
    ]

    ENABLED = colors.B_GREEN + 'Enabled' + colors.RESET
    DISABLED = colors.B_RED + 'Disabled' + colors.RESET

    rows: list = []

    for module_config in config['modules']:
        rows.append([
            module_config['module'],
            DISABLED if 'disabled' in module_config and module_config['disabled'] else ENABLED
        ])

    print(tabulate(rows, headers=headers, tablefmt='fancy_grid'))


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
    return_code, _, stderr = utils.run_cmd(['xdg-open', get_web_interface_url()])

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


def display_log_files(mmpm_logs: bool = False, gunicorn_logs: bool = False, tail: bool = False) -> None:
    logs: List[str] = []

    if mmpm_logs:
        if os.path.exists(consts.MMPM_LOG_FILE):
            logs.append(consts.MMPM_LOG_FILE)
        else:
            utils.error_msg('MMPM log file not found')

    if gunicorn_logs:
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

