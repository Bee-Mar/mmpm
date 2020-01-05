#!/usr/bin/env python3
import re
import os
import time
import json
import datetime
import subprocess
import shutil
from tabulate import tabulate
from textwrap import fill
from mmpm import colors, utils, mmpm
from urllib.error import HTTPError
from urllib.request import urlopen
from collections import defaultdict
from bs4 import BeautifulSoup


def snapshot_details(modules, curr_snap, next_snap):
    '''
    Displays information regarding the most recent 'snapshot_file', ie. when it
    was taken, when the next scheduled snapshot will be taken, how many module
    categories exist, and the total number of modules available. Additionally,
    tells user how to forcibly request a new snapshot be taken.

    Arguments
    =========
    modules: Dictionary
    curr_snap: String (timestamp)
    next_snap: String (timestamp)
    '''

    num_categories = len(modules.keys())
    num_modules = 0

    for value in modules.values():
        num_modules += len(value)

    print(colors.BRIGHT_YELLOW + "\nMost recent snapshot of MagicMirror Modules taken: " + colors.BRIGHT_WHITE + "{}".format(curr_snap))
    print(colors.BRIGHT_YELLOW + "The next snapshot will be taken on or after: " + colors.BRIGHT_WHITE + " {}\n".format(next_snap))
    print(colors.BRIGHT_GREEN + "Module Categories: " + colors.BRIGHT_WHITE + "{}".format(num_categories))
    print(colors.BRIGHT_GREEN + "Modules Available: " + colors.BRIGHT_WHITE + "{}".format(num_modules))
    print(colors.BRIGHT_WHITE + "\nTo forcibly refresh the snapshot, run 'mmpm -f' or 'mmpm --force-refresh'\n")


def check_for_mmpm_enhancements():
    '''
    Scrapes the main file of MMPM off the github repo, and compares the current
    version, versus the one available in the master branch. If there is a newer
    version, the user is prompted for an upgrade.

    Arguments
    =========
    None
    '''

    MMPM_REPO = "https://github.com/Bee-Mar/mmpm.git"
    MMPM_FILE = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"

    try:
        MMPM_FILE = urlopen(MMPM_FILE)
        contents = str(MMPM_FILE.read())

        version_line = re.findall(r"__version__ = \d+\.\d+", contents)
        version_number = re.findall(r"\d+\.\d+", version_line[0])
        version_number = float(version_number[0])

        if version_number and mmpm.__version__ < version_number:
            valid_response = False

            utils.plain_print(colors.BRIGHT_CYAN + "Automated check for MMPM enhancements... " + colors.NORMAL_WHITE)

            while not valid_response:
                response = input(colors.BRIGHT_GREEN + "MMPM enhancements are available. " +
                                 colors.BRIGHT_WHITE + "Would you like to upgrade now? [yes/no | y/n]: " +
                                 colors.NORMAL)

                if response in ("yes", "y"):
                    original_dir = os.getcwd()

                    os.chdir(utils.HOME_DIR + "/Downloads")

                    # make sure there isn't a pre-existing version cloned
                    os.system("rm -rf mmpm")

                    print("\n")

                    return_code, std_out, std_err = utils.run_cmd(['git', 'clone', MMPM_REPO])

                    if return_code:
                        utils.error_msg(std_err)

                    os.chdir("mmpm")
                    print("\n")

                    return_code, std_out, std_err = utils.run_cmd(['make'])

                    if return_code:
                        utils.error_msg(std_err)

                    os.chdir(original_dir)
                    print(colors.BRIGHT_GREEN + "\nMMPM Version {} installed.".format(version_number))
                    valid_response = True

                elif response in ("no", "n"):
                    valid_response = True
                else:
                    utils.warning_msg("Respond with yes/no or y/n.")
        else:
            print("No enhancements available for MMPM.")

    except HTTPError:
        pass


def enhance_modules(modules_table, update=False, upgrade=False, modules_to_upgrade=None):
    '''
    Depending on flags passed in as arguments:

    Checks for available module updates, and alerts the user. Or, pulls latest
    version of module(s) from the associated repos.

    If upgrading, a user can upgrade all modules that have available upgrades
    by ommitting additional arguments. Or, upgrade specific modules by
    supplying their case-sensitive name(s) as an addtional argument.

    Arguments
    =========
    modules_table: Dictionary
    update: Boolean
    upgrade: Boolean
    modules_to_upgrade: List
    '''

    original_dir = os.getcwd()
    modules_dir = os.path.join(utils.get_magicmirror_root(), 'modules')
    os.chdir(modules_dir)

    updates_list = []

    dirs = os.listdir(modules_dir)

    if upgrade and modules_to_upgrade:
        dirs = modules_to_upgrade

    if update:
        utils.plain_print(colors.BRIGHT_CYAN + "Checking for updates... " + colors.NORMAL_WHITE)

    for _, value in modules_table.items():
        for index, _ in enumerate(value):
            if value[index]["Title"] in dirs:
                title = value[index]["Title"]
                curr_module_dir = os.path.join(modules_dir, title)
                os.chdir(curr_module_dir)

                if update:
                    git_status = subprocess.run(["git", "fetch", "--dry-run"], stdout=subprocess.PIPE)

                    if git_status.stdout:
                        updates_list.append(title)

                elif upgrade:
                    utils.plain_print(colors.BRIGHT_CYAN + "Requesting upgrade for {}... ".format(title) + colors.NORMAL_WHITE)

                    os.system("git pull")

                    if os.path.isfile(os.getcwd() + "/package.json"):
                        print(colors.BRIGHT_CYAN + "Found package.json. Installing NodeJS dependencies... " + colors.NORMAL_WHITE)
                        os.system("$(which npm) install")

                os.chdir(modules_dir)

    os.chdir(original_dir)

    if update:
        if not updates_list:
            utils.plain_print(colors.BRIGHT_WHITE + "No updates available.\n" + colors.NORMAL)
        else:
            utils.plain_print(colors.BRIGHT_MAGENTA + "Updates are available for the following modules:\n" + colors.NORMAL_WHITE)

            for update in updates_list:
                print("{}".format(update))


def search_modules(modules_table, search):
    '''
    Used to search the 'modules_table' for either a category, or keyword/phrase
    appearing within module descriptions. If the argument supplied is a
    category name, all modules from that category will be listed. Otherwise,
    all modules whose descriptions contain the keyword/phrase will be
    displayed.

    Arguments
    =========
    modules_table: Dictionary
    search: String
    '''

    search_results = {}
    query = search[0]

    try:
        if modules_table[query]:
            search_results[query] = modules_table[query]
            return search_results

    except KeyError:
        pass

    try:
        search_results = defaultdict(list)
        query = query.lower()

        for key, value in modules_table.items():
            for index, _ in enumerate(value):
                title = value[index]["Title"]
                desc = value[index]["Description"]
                repo = value[index]["Repository"]
                author = value[index]["Author"]

                if query in title.lower() or query in desc.lower() or query in author.lower():
                    entry = {"Title": title,
                             "Repository": repo,
                             "Author": author,
                             "Description": desc}

                    if entry not in search_results[key]:
                        search_results[key].append(entry)

    except KeyError:
        pass

    return search_results


def install_modules(modules_table, modules_to_install):
    '''
    Compares list of 'modules_to_install' to modules found within the
    'modules_table', clones the repository within the ~/MagicMirror/modules
    directory, and runs 'npm install' for each newly installed module.

    Arguments
    =========
    modules_table: Dictionary
    modules_to_install: List
    '''

    modules_dir = os.path.join(utils.get_magicmirror_root(), 'modules')
    original_dir = os.getcwd()

    if not os.path.exists(modules_dir):
        utils.error_msg("The directory '{}' does not exist. Have you installed MagicMirror properly?".format(modules_dir))

    os.chdir(modules_dir)
    successful_installs = []

    for value in modules_table.values():
        curr_subdir = os.getcwd()

        for index in range(len(value)):
            if value[index]["Title"] in modules_to_install:
                title = value[index]["Title"]
                target = os.path.join(os.getcwd(), title)
                repo = value[index]["Repository"]

                successful_installs.append(title)

                try:
                    os.mkdir(target)

                except OSError:
                    utils.error_msg("The {0} module already exists. To remove the module, run 'mmpm -r {0}'".format(title))

                os.chdir(target)

                print(colors.BRIGHT_GREEN + "Installing {}".format(value[index]["Title"]) +
                      colors.BRIGHT_YELLOW + " @ " +
                      colors.BRIGHT_GREEN + "{}\n".format(target))

                utils.plain_print(colors.BRIGHT_CYAN + "Cloning {} repository ... ".format(title) + colors.NORMAL_WHITE)

                return_code, std_out, std_err = utils.run_cmd(['git', 'clone', repo, target])
                utils.handle_warnings(return_code, std_err)

                if os.path.isfile(os.getcwd() + "/package.json"):
                    utils.plain_print(colors.BRIGHT_CYAN + "Found package.json. Installing NodeJS dependencies... ")
                    return_code, std_out, std_err = utils.run_cmd(['npm', 'install'])
                    utils.handle_warnings(return_code, std_err)

                if os.path.isfile(os.getcwd() + '/Makefile') or os.path.isfile(os.getcwd() + '/makefile'):
                    utils.plain_print(colors.BRIGHT_CYAN + "Found Makefile. Attempting to run 'make'... ")
                    return_code, std_out, std_err = utils.run_cmd(['make'])
                    utils.handle_warnings(return_code, std_err)

                if os.path.isfile(os.getcwd() + '/CMakeLists.txt'):
                    utils.plain_print(colors.BRIGHT_CYAN + "Found CMakeLists.txt. Attempting to run 'cmake'... ")
                    os.system('mkdir -p build')
                    os.chdir('build')
                    return_code, std_out, std_err = utils.run_cmd(['cmake', '..'])
                    utils.handle_warnings(return_code, std_err)

                    os.chdir('..')

                os.chdir(curr_subdir)

    os.chdir(original_dir)

    for module in modules_to_install:
        if module not in successful_installs:
            utils.warning_msg("Unable to match '{}' with installation candidate. Is the title casing correct?\n".format(module))

    utils.plain_print(colors.BRIGHT_GREEN + "\nTo complete installation, populate " + colors.BRIGHT_WHITE)
    print(colors.BRIGHT_WHITE + "'~/MagicMirror/config/config.js'" + colors.BRIGHT_GREEN + " with the necessary configurations for each of the newly installed modules\n")
    print(colors.NORMAL_WHITE + "There may be additional installation steps required. Review the associated GitHub pages for each newly installed module")


def install_magicmirror():
    '''
    Installs MagicMirror. First checks if a MagicMirror installation can be
    found, and if one is found, prompts user to update the MagicMirror.
    Otherwise, searches for current version of NodeJS on the system. If one is
    found, the MagicMirror is then installed. If an old version of NodeJS is
    found, a newer version is installed before installing MagicMirror.

    Arguments
    =========
    None
    '''

    original_dir = os.getcwd()

    if not os.path.exists(os.path.join(utils.get_magicmirror_root())):
        print(colors.BRIGHT_CYAN + "MagicMirror directory not found. " +
              colors.NORMAL_WHITE + "Installing MagicMirror..." +
              colors.NORMAL_WHITE)

        os.system('bash -c "$(curl -sL https://raw.githubusercontent.com/MichMich/MagicMirror/master/installers/raspberry.sh)"')

    else:
        message = colors.BRIGHT_CYAN + "MagicMirror directory found. " + colors.NORMAL_WHITE
        message += "Would you like to check for updates? "
        message += "[yes/no | y/n]: "

        valid_response = False

        while not valid_response:
            response = input(message)

            if response in ("yes", "y"):
                os.chdir(os.path.join(utils.HOME_DIR, 'MagicMirror'))

                print(colors.BRIGHT_CYAN + "Checking for updates..." + colors.NORMAL_WHITE)
                git_status = subprocess.run(["git", "fetch", "--dry-run"], stdout=subprocess.PIPE)

                if git_status.stdout:
                    print(colors.BRIGHT_CYAN + "Updates found for MagicMirror. " + colors.NORMAL_WHITE + "Requesting upgrades...")
                    return_code, std_out, std_err = utils.run_cmd(['git', 'pull'])

                    utils.handle_warnings(return_code, std_err)

                    if not return_code:
                        os.system("$(which npm) install")

                else:
                    print("No updates available for MagicMirror.")

                valid_response = True

            elif response in ("no", "n"):
                print(colors.BRIGHT_MAGENTA + "Aborted MagicMirror update.")
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

    Arguments
    =========
    modules_table: Dictionary
    modules_to_remove: List
    '''

    if not installed_modules:
        utils.error_msg("No modules are currently installed.")

    modules_dir = os.path.join(utils.get_magicmirror_root(), 'modules')
    original_dir = os.getcwd()

    if not os.path.exists(modules_dir):
        utils.error_msg("The '{}' directory doesn't exist. Have you installed MagicMirror?".format(modules_dir))

    os.chdir(modules_dir)
    successful_removals = []
    curr_dir = os.getcwd()

    for module in modules_to_remove:
        dir_to_rm = os.path.join(curr_dir, module)

        try:
            shutil.rmtree(dir_to_rm)
            successful_removals.append(module)

        except OSError:
            utils.warning_msg("The directory for '{}' does not exist.".format(module))

    if successful_removals:
        print(colors.BRIGHT_GREEN + "The following modules were successfully deleted:" + colors.NORMAL)

        for removal in successful_removals:
            print(colors.NORMAL_WHITE + "{}".format(removal))

    else:
        utils.error_msg("Unable to remove modules.")

    os.chdir(original_dir)


def load_modules(snapshot_file, force_refresh=False):
    '''
    Reads in modules from the hiddent 'snapshot_file' stored in the users home
    directory, and checks if the file is out of date. If so, the modules are
    gathered again from the MagicMirror 3rd Party Modules wiki.

    Arguments
    =========
    snapshot_file: Path to file
    force_refresh: Boolean
    '''

    modules = {}
    curr_snap = 0
    refresh_interval = 6

    checked_for_enhancements = False
    file_exists = os.path.exists(snapshot_file)

    if not force_refresh and file_exists:
        curr_snap = os.path.getmtime(snapshot_file)
        next_snap = curr_snap + refresh_interval * 60 * 60
    else:
        next_snap = curr_snap = time.time()

    # if the snapshot has expired, or doesn't exist, get a new one
    if not file_exists or force_refresh or next_snap - time.time() <= 0.0:
        utils.plain_print(colors.BRIGHT_CYAN + "Snapshot expired, retrieving modules... ")

        modules = retrieve_modules()

        with open(snapshot_file, "w") as f:  # save the new snapshot
            json.dump(modules, f)

        utils.plain_print(colors.NORMAL_WHITE + "Retrieval complete.\n")

        curr_snap = os.path.getmtime(snapshot_file)
        next_snap = curr_snap + refresh_interval * 60 * 60

        utils.plain_print(colors.BRIGHT_CYAN + "Automated check for MMPM enhancements... " + colors.NORMAL_WHITE)

        check_for_mmpm_enhancements()
        checked_for_enhancements = True

    else:
        with open(snapshot_file, "r") as f:
            modules = json.load(f)

    curr_snap = datetime.datetime.fromtimestamp(int(curr_snap))
    next_snap = datetime.datetime.fromtimestamp(int(next_snap))

    return modules, curr_snap, next_snap, checked_for_enhancements


def retrieve_modules():
    '''
    Scrapes the MagicMirror 3rd Party Wiki, and saves all modules along with
    their full, available descriptions in a hidden JSON file in the users home
    directory.

    Arguments
    =========
    None
    '''

    modules = {}

    mmm_url = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"
    web_page = urlopen(mmm_url).read()

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

        for j, _ in enumerate(row):
            # ignore cells that literally say "Title", "Author", "Description"
            if j > 0:
                td_soup = tr_soup[index][j].find_all("td")

                title = ""
                repo = "N/A"
                author = ""
                desc = ""

                for k in range(len(td_soup)):
                    if k == 0:
                        for td in td_soup[k]:
                            title = td.contents[0]

                        for a in td_soup[k].find_all("a"):
                            if a.has_attr("href"):
                                repo = a["href"]

                        repo = str(repo)
                        title = str(title)

                    elif k == 1:
                        for contents in td_soup[k].contents:
                            if type(contents).__name__ == "Tag":
                                for tag in contents:
                                    author = tag.strip()
                            else:
                                author = contents

                        author = str(author)

                    else:
                        for contents in td_soup[k].contents:
                            if type(contents).__name__ == "Tag":
                                for content in contents:
                                    desc += content
                            else:
                                desc += contents

                        desc = str(desc.encode('utf-8'))

                modules[categories[index]].append({
                    "Title": title,
                    "Repository": repo,
                    "Author": author,
                    "Description": desc
                })

    return modules


def display_modules(modules_table, list_all=False, list_categories=False):
    '''
    Depending on the user flags passed in from the command line, either all
    existing modules may be displayed, or the names of all categories of
    modules may be displayed.

    Arguments
    =========
    modules_table: Dictionary
    list_all: Boolean
    list_categories: Boolean
    '''

    if list_categories:
        headers = [colors.BRIGHT_CYAN + "CATEGORY", colors.BRIGHT_CYAN + "NUMBER OF MODULES" + colors.NORMAL_WHITE]
        rows = [[key, len(modules_table[key])] for key in modules_table.keys()]
        print(tabulate(rows, headers, tablefmt="fancy_grid"))

    elif list_all:

        headers = [
            colors.BRIGHT_CYAN + "CATEGORY",
            "TITLE",
            "REPOSITORY",
            "AUTHOR",
            "DESCRIPTION" + colors.NORMAL_WHITE
        ]

        rows = []

        for category, details in modules_table.items():
            for index, _ in enumerate(details):
                rows.append([
                    category,
                    details[index]["Title"],
                    fill(details[index]["Repository"]),
                    fill(details[index]["Author"], width=12),
                    fill(details[index]["Description"], width=15)
                ])

        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))


def get_installed_modules(modules_table):
    '''
    Saves a list of all currently installed modules in the
    ~/MagicMirror/modules directory, and compares against the known modules
    from the MagicMirror 3rd Party Wiki.

    Arguments
    =========
    modules_table: Dictionary
    '''

    modules_dir = os.path.join(utils.get_magicmirror_root(), 'modules')
    original_dir = os.getcwd()

    if not os.path.exists(modules_dir):
        utils.error_msg("The directory '{}' does not exist. Have you installed MagicMirror properly?".format(modules_dir))

    os.chdir(modules_dir)

    module_dirs = os.listdir(os.getcwd())

    installed_modules = []

    for values in modules_table.values():
        for value in values:
            if value['Title'] in module_dirs:
                installed_modules.append(value['Title'])

    os.chdir(original_dir)

    return installed_modules

