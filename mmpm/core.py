#!/usr/bin/env python3
import re
import os
import time
import json
import datetime
import subprocess
import shutil
from textwrap import fill
from tabulate import tabulate
from urllib.error import HTTPError
from urllib.request import urlopen
from collections import defaultdict
from bs4 import BeautifulSoup
from mmpm import colors, utils, mmpm


def snapshot_details(modules, curr_snap, next_snap):
    '''
    Displays information regarding the most recent 'snapshot_file', ie. when it
    was taken, when the next scheduled snapshot will be taken, how many module
    categories exist, and the total number of modules available. Additionally,
    tells user how to forcibly request a new snapshot be taken.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules
        curr_snap (str): Timestamp of current snapshot
        next_snap (str): Timestamp of when next snapshot will be taken

    Returns:
        None
    '''

    num_categories = len(modules.keys())
    num_modules = 0

    for value in modules.values():
        num_modules += len(value)

    print(colors.B_YELLOW + "\nMost recent snapshot of MagicMirror Modules taken: " + colors.B_WHITE + f"{curr_snap}")
    print(colors.B_YELLOW + "The next snapshot will be taken on or after: " + colors.B_WHITE + f" {next_snap}\n")
    print(colors.B_GREEN + "Module Categories: " + colors.B_WHITE + f"{num_categories}")
    print(colors.B_GREEN + "Modules Available: " + colors.B_WHITE + f"{num_modules}\n")


def check_for_mmpm_enhancements():
    '''
    Scrapes the main file of MMPM off the github repo, and compares the current
    version, versus the one available in the master branch. If there is a newer
    version, the user is prompted for an upgrade.

    Parameters:
        None

    Returns:
        None
    '''

    try:
        MMPM_FILE = urlopen(utils.MMPM_FILE_URL)
        contents = str(MMPM_FILE.read())

        version_line = re.findall(r"__version__ = \d+\.\d+", contents)
        version_number = re.findall(r"\d+\.\d+", version_line[0])
        version_number = float(version_number[0])

        if version_number and mmpm.__version__ < version_number:
            valid_response = False

            utils.plain_print(
                colors.B_CYAN + "Automated check for MMPM enhancements... " + colors.RESET)

            while not valid_response:
                response = input(colors.B_GREEN + "MMPM enhancements are available. " +
                                 colors.B_WHITE + "Would you like to upgrade now? [yes/no | y/n]: " +
                                 colors.RESET)

                if response in ("yes", "y"):
                    original_dir = os.getcwd()

                    os.chdir(utils.HOME_DIR + "/Downloads")

                    # make sure there isn't a pre-existing version cloned
                    os.system("rm -rf mmpm")

                    print("\n")

                    return_code, _, std_err = utils.run_cmd(['git', 'clone', utils.MMPM_REPO_URL])

                    if return_code:
                        utils.error_msg(std_err)

                    os.chdir("mmpm")
                    print("\n")

                    return_code, _, std_err = utils.run_cmd(['make'])

                    if return_code:
                        utils.error_msg(std_err)

                    os.chdir(original_dir)
                    print(colors.B_GREEN + f"\nMMPM Version: {version_number}")
                    valid_response = True

                elif response in ("no", "n"):
                    valid_response = True
                else:
                    utils.warning_msg("Respond with yes/no or y/n.")
        else:
            print("No enhancements available for MMPM.")

    except HTTPError:
        pass


def enhance_modules(modules, update=False, upgrade=False, modules_to_upgrade=None):
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
        modules_to_upgrade (list): List of modules to update/upgrade

    Returns:
        None
    '''

    original_dir = os.getcwd()
    modules_dir = os.path.join(utils.get_magicmirror_root(), 'modules')
    os.chdir(modules_dir)

    updates_list = []

    dirs = os.listdir(modules_dir)

    if upgrade and modules_to_upgrade:
        dirs = modules_to_upgrade

    if update:
        utils.plain_print(colors.B_CYAN + "Checking for updates... " + colors.RESET)

    for _, value in modules.items():
        for index, _ in enumerate(value):
            if value[index][utils.TITLE] in dirs:
                title = value[index][utils.TITLE]
                curr_module_dir = os.path.join(modules_dir, title)
                os.chdir(curr_module_dir)

                if update:
                    git_status = subprocess.run(
                        ["git", "fetch", "--dry-run"],
                        stdout=subprocess.PIPE)

                    if git_status.stdout:
                        updates_list.append(title)

                elif upgrade:
                    utils.plain_print(
                        colors.B_CYAN + f"Requesting upgrade for {title}... " + colors.RESET)

                    os.system("git pull")

                    if os.path.isfile(os.path.join(os.getcwd(), "package.json")):
                        print(colors.B_CYAN + "Found package.json. Installing NodeJS dependencies... " + colors.RESET)
                        os.system("$(which npm) install")

                os.chdir(modules_dir)

    os.chdir(original_dir)

    if update:
        if not updates_list:
            utils.plain_print(colors.B_WHITE + "No updates available.\n" + colors.RESET)
        else:
            utils.plain_print(colors.B_MAGENTA + "Updates are available for the following modules:\n" + colors.RESET)

            for update in updates_list:
                print(f"{update}")


def search_modules(modules, search):
    '''
    Used to search the 'modules' for either a category, or keyword/phrase
    appearing within module descriptions. If the argument supplied is a
    category name, all modules from that category will be listed. Otherwise,
    all modules whose descriptions contain the keyword/phrase will be
    displayed.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules
        search (str): Search query

    Returns:
        None
    '''

    search_results = {}
    query = search[0]

    try:
        if modules[query]:
            search_results[query] = modules[query]
            return search_results

    except KeyError:
        pass

    try:
        search_results = defaultdict(list)
        query = query.lower()

        for key, value in modules.items():
            for index, _ in enumerate(value):
                title = value[index][utils.TITLE]
                desc = value[index][utils.DESCRIPTION]
                repo = value[index][utils.REPOSITORY]
                author = value[index][utils.AUTHOR]

                if query in title.lower() or query in desc.lower() or query in author.lower():
                    entry = {
                        utils.TITLE: title,
                        utils.REPOSITORY: repo,
                        utils.AUTHOR: author,
                        utils.DESCRIPTION: desc
                    }

                    if entry not in search_results[key]:
                        search_results[key].append(entry)

    except KeyError:
        pass

    return search_results


def install_modules(modules, modules_to_install):
    '''
    Compares list of 'modules_to_install' to modules found within the
    'modules', clones the repository within the ~/MagicMirror/modules
    directory, and runs 'npm install' for each newly installed module.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules
        modules_to_install (list): List of modules to install

    Returns:
        None
    '''

    modules_dir = os.path.join(utils.get_magicmirror_root(), 'modules')
    original_dir = os.getcwd()

    if not os.path.exists(modules_dir):
        msg = "Failed to find MagicMirror root. Have you installed MagicMirror properly? "
        msg += "You may also set the env variable 'MMPM_MAGICMIRROR_ROOT' to the MagicMirror root directory."
        utils.error_msg(msg)

    os.chdir(modules_dir)
    successful_installs = []

    for value in modules.values():
        curr_subdir = os.getcwd()

        for index in range(len(value)):
            if value[index][utils.TITLE] in modules_to_install:
                title = value[index][utils.TITLE]
                target = os.path.join(os.getcwd(), title)
                repo = value[index][utils.REPOSITORY]

                successful_installs.append(title)

                try:
                    os.mkdir(target)
                except OSError:
                    utils.error_msg(f"The {title} module already exists. To remove the module, run 'mmpm -r {title}'")

                os.chdir(target)

                print(colors.B_GREEN + f"Installing {title}" + colors.B_YELLOW + " @ " + colors.B_GREEN + f"{target}\n")

                utils.plain_print(
                    colors.B_CYAN + f"Cloning {title} repository ... " + colors.RESET)

                return_code, _, std_err = utils.run_cmd(['git', 'clone', repo, target])
                utils.handle_warnings(return_code, std_err)

                if os.path.isfile(os.getcwd() + "/package.json"):
                    utils.plain_print(colors.B_CYAN + "Found package.json. Installing NodeJS dependencies... ")
                    return_code, _, std_err = utils.run_cmd(['npm', 'install'])
                    utils.handle_warnings(return_code, std_err)

                if os.path.isfile(os.getcwd() + '/Makefile') or os.path.isfile(os.getcwd() + '/makefile'):
                    utils.plain_print(colors.B_CYAN + "Found Makefile. Attempting to run 'make'... ")
                    return_code, _, std_err = utils.run_cmd(['make'])
                    utils.handle_warnings(return_code, std_err)

                if os.path.isfile(os.getcwd() + '/CMakeLists.txt'):
                    utils.plain_print(colors.B_CYAN + "Found CMakeLists.txt. Attempting to run 'cmake'... ")
                    os.system('mkdir -p build')
                    os.chdir('build')
                    return_code, _, std_err = utils.run_cmd(['cmake', '..'])
                    utils.handle_warnings(return_code, std_err)

                    os.chdir('..')

                os.chdir(curr_subdir)

    os.chdir(original_dir)

    for module in modules_to_install:
        if module not in successful_installs:
            utils.warning_msg(
                f"Unable to match '{module}' with installation candidate. Is the title casing correct?\n")

    utils.plain_print(colors.B_GREEN +
                      "\nTo complete installation, populate " + colors.B_WHITE)
    print(colors.B_WHITE + "'~/MagicMirror/config/config.js'" + colors.B_GREEN +
          " with the necessary configurations for each of the newly installed modules\n")
    print(colors.RESET + "There may be additional installation steps required. Review the associated GitHub pages for each newly installed module")


def install_magicmirror():
    '''
    Installs MagicMirror. First checks if a MagicMirror installation can be
    found, and if one is found, prompts user to update the MagicMirror.
    Otherwise, searches for current version of NodeJS on the system. If one is
    found, the MagicMirror is then installed. If an old version of NodeJS is
    found, a newer version is installed before installing MagicMirror.

    Parameters:
        None

    Returns:
        None
    '''

    original_dir = os.getcwd()

    if not os.path.exists(os.path.join(utils.get_magicmirror_root())):
        print(colors.B_CYAN + "MagicMirror directory not found. " +
              colors.RESET + "Installing MagicMirror..." +
              colors.RESET)

        os.system('bash -c "$(curl -sL https://raw.githubusercontent.com/MichMich/MagicMirror/master/installers/raspberry.sh)"')

    else:
        message = colors.B_CYAN + "MagicMirror directory found. " + colors.RESET + "Would you like to check for updates? [yes/no | y/n]: "
        valid_response = False

        while not valid_response:
            response = input(message)

            if response in ("yes", "y"):
                os.chdir(os.path.join(utils.HOME_DIR, 'MagicMirror'))

                print(colors.B_CYAN + "Checking for updates..." + colors.RESET)
                git_status = subprocess.run(["git", "fetch", "--dry-run"], stdout=subprocess.PIPE)

                if git_status.stdout:
                    print(colors.B_CYAN + "Updates found for MagicMirror. " + colors.RESET + "Requesting upgrades...")
                    return_code, _, std_err = utils.run_cmd(['git', 'pull'])
                    utils.handle_warnings(return_code, std_err)

                    if not return_code:
                        os.system("$(which npm) install")

                else:
                    print("No updates available for MagicMirror.")

                valid_response = True

            elif response in ("no", "n"):
                print(colors.B_MAGENTA + "Aborted MagicMirror update.")
                valid_response = True

            else:
                utils.warning_msg("Respond with yes/no or y/n.")

    os.chdir(original_dir)


def remove_modules(installed_modules, modules_to_remove):
    '''
    Gathers list of modules currently installed in the ~/MagicMirror/modules
    directory, and removes each of the modules from the folder, if modules are
    currently installed. Otherwise, the user is shown an error message alerting
    them no modules are currently installed.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules
        modules_to_remove (list): List of modules to remove

    Returns:
        None
    '''

    if not installed_modules:
        utils.error_msg("No modules are currently installed.")

    modules_dir = os.path.join(utils.get_magicmirror_root(), 'modules')
    original_dir = os.getcwd()

    if not os.path.exists(modules_dir):
        msg = "Failed to find MagicMirror root. Have you installed MagicMirror properly? "
        msg += "You may also set the env variable 'MMPM_MAGICMIRROR_ROOT' to the MagicMirror root directory."
        utils.error_msg(msg)

    os.chdir(modules_dir)
    successful_removals = []
    curr_dir = os.getcwd()

    for module in modules_to_remove:
        dir_to_rm = os.path.join(curr_dir, module)

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

    os.chdir(original_dir)


def load_modules(force_refresh=False):
    '''
    Reads in modules from the hidden 'snapshot_file'  and checks if the file is
    out of date. If so, the modules are gathered again from the MagicMirror 3rd
    Party Modules wiki.

    Parameters:
        force_refresh (bool): Boolean flag to force refresh of snapshot

    Returns:
        None
    '''

    modules = {}
    curr_snap = 0
    refresh_interval = 6

    checked_for_enhancements = False
    snapshot_exists = os.path.exists(utils.SNAPSHOT_FILE)

    if not snapshot_exists:
        try:
            os.mkdir(os.path.dirname(utils.SNAPSHOT_FILE))
        except OSError:
            error_msg('Failed to create directory for snapshot')

    if not force_refresh and snapshot_exists:
        curr_snap = os.path.getmtime(utils.SNAPSHOT_FILE)
        next_snap = curr_snap + refresh_interval * 60 * 60
    else:
        next_snap = curr_snap = time.time()

    # if the snapshot has expired, or doesn't exist, get a new one
    if not snapshot_exists or force_refresh or next_snap - time.time() <= 0.0:
        utils.plain_print(colors.B_CYAN + "Refreshing MagicMirror module snapshot... ")
        modules = retrieve_modules()

        with open(utils.SNAPSHOT_FILE, "w") as f:  # save the new snapshot
            json.dump(modules, f)

        utils.plain_print(colors.RESET + "Retrieval complete.\n")

        curr_snap = os.path.getmtime(utils.SNAPSHOT_FILE)
        next_snap = curr_snap + refresh_interval * 60 * 60

        utils.plain_print(colors.B_CYAN + "Automated check for MMPM enhancements... " + colors.RESET)

        check_for_mmpm_enhancements()
        checked_for_enhancements = True

    else:
        with open(utils.SNAPSHOT_FILE, "r") as f:
            modules = json.load(f)

    if os.path.exists(utils.MMPM_CONFIG_FILE) and os.stat(utils.MMPM_CONFIG_FILE).st_size:
        try:
            with open(utils.MMPM_CONFIG_FILE, "r") as f:
                modules[utils.EXTERNAL_MODULE_SOURCES] = json.load(f)[utils.EXTERNAL_MODULE_SOURCES]
        except Exception:
            utils.warning_msg(f'Failed to load data from {utils.MMPM_CONFIG_FILE}.')

    curr_snap = datetime.datetime.fromtimestamp(int(curr_snap))
    next_snap = datetime.datetime.fromtimestamp(int(next_snap))

    return modules, curr_snap, next_snap, checked_for_enhancements


def retrieve_modules():
    '''
    Scrapes the MagicMirror 3rd Party Wiki, and saves all modules along with
    their full, available descriptions in a hidden JSON file in the users home
    directory.

    Parameters:
        None

    Returns:
        None
    '''

    modules = {}

    try:
        web_page = urlopen(utils.MAGICMIRROR_MODULES_URL).read()
    except HTTPError as err:
        utils.error_msg("Unable to retrieve MagicMirror modules. Is your internet connection down?")

    soup = BeautifulSoup(web_page, "html.parser")
    table_soup = soup.find_all("table")

    category_soup = soup.find_all(attrs={"class": "markdown-body"})
    categories_soup = category_soup[0].find_all("h3")

    categories = []

    for index, _ in enumerate(categories_soup):
        last_element = len(categories_soup[index].contents) - 1
        new_category = categories_soup[index].contents[last_element]

        if new_category != "General Advice":
            categories.append(new_category)

    tr_soup = []

    for table in table_soup:
        tr_soup.append(table.find_all("tr"))

    for index, row in enumerate(tr_soup):
        modules.update({categories[index]: list()})

        for column_number, _ in enumerate(row):
            # ignore cells that literally say "Title", "Author", "Description"
            if column_number > 0:
                td_soup = tr_soup[index][column_number].find_all("td")

                title = ""
                repo = "N/A"
                author = ""
                desc = ""

                for idx in range(len(td_soup)):
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
                        for contents in td_soup[idx].contents:
                            if type(contents).__name__ == "Tag":
                                for content in contents:
                                    desc += content.string
                            else:
                                desc += contents.string

                modules[categories[index]].append({
                    utils.TITLE: title,
                    utils.REPOSITORY: repo,
                    utils.AUTHOR: author,
                    utils.DESCRIPTION: desc
                })

    return modules


def display_modules(modules, list_all=False, list_categories=False):
    '''
    Depending on the user flags passed in from the command line, either all
    existing modules may be displayed, or the names of all categories of
    modules may be displayed.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules list_all (bool): Boolean flag to list all modules
        list_categories (bool): Boolean flag to list categories

    Returns:
        None
    '''

    if list_categories:
        headers = [
            colors.B_CYAN + "Category",
            colors.B_CYAN + "Number of Modules" + colors.RESET
        ]

        rows = [[key, len(modules[key])] for key in modules.keys()]
        print(tabulate(rows, headers, tablefmt="fancy_grid"))

    elif list_all:

        headers = [
            colors.B_CYAN + "Category",
            utils.TITLE,
            utils.REPOSITORY,
            utils.AUTHOR,
            utils.DESCRIPTION + colors.RESET
        ]

        rows = []

        for category, details in modules.items():
            for index, _ in enumerate(details):
                rows.append([
                    category,
                    details[index][utils.TITLE],
                    fill(details[index][utils.REPOSITORY]),
                    fill(details[index][utils.AUTHOR], width=12),
                    fill(details[index][utils.DESCRIPTION], width=15)
                ])

        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))


def get_installed_modules(modules):
    '''
    Saves a list of all currently installed modules in the
    ~/MagicMirror/modules directory, and compares against the known modules
    from the MagicMirror 3rd Party Wiki.

    Parameters:
        modules (dict): Dictionary of MagicMirror modules

    Returns:
        None
    '''

    modules_dir = os.path.join(utils.get_magicmirror_root(), 'modules')
    original_dir = os.getcwd()

    if not os.path.exists(modules_dir):
        msg = "Failed to find MagicMirror root. Have you installed MagicMirror properly? "
        msg += "You may also set the env variable 'MMPM_MAGICMIRROR_ROOT' to the MagicMirror root directory."
        utils.error_msg(msg)

    os.chdir(modules_dir)

    module_dirs = os.listdir(os.getcwd())
    installed_modules = [value[utils.TITLE] for values in modules.values() for value in values if value[utils.TITLE] in module_dirs]
    os.chdir(original_dir)
    return installed_modules


def add_external_module_source(title=None, author=None, repo=None, desc=None):
    print(colors.B_GREEN + "Register external module source\n" + colors.RESET)

    if not title and not author and not repo and not desc:
        try:
            title = input("Title: ")
            author = input("Author: ")
            repo = input("Repository: ")
            desc = input("Description: ")

            new_source = {
                utils.TITLE: title,
                utils.REPOSITORY: repo,
                utils.AUTHOR: author,
                utils.DESCRIPTION: desc
            }

        except KeyboardInterrupt:
            print('\n')
            exit(1)

    try:
        if os.path.exists(utils.MMPM_CONFIG_FILE) and os.stat(utils.MMPM_CONFIG_FILE).st_size:
            config = {}

            with open(utils.MMPM_CONFIG_FILE, 'r') as mmpm_config:
                config[utils.EXTERNAL_MODULE_SOURCES] = json.load(mmpm_config)[utils.EXTERNAL_MODULE_SOURCES]

            with open(utils.MMPM_CONFIG_FILE, 'w') as mmpm_config:
                config[utils.EXTERNAL_MODULE_SOURCES].append(new_source)
                json.dump(config, mmpm_config)
        else:
            with open(utils.MMPM_CONFIG_FILE, 'w') as mmpm_config:
                json.dump({utils.EXTERNAL_MODULE_SOURCES: [new_source]}, mmpm_config)

        print(colors.B_WHITE + f'\nSuccessfully added external module to {utils.MMPM_CONFIG_FILE}\n' + colors.RESET)
        return True
    except IOError:
        error_msg('Failed to save external module')
