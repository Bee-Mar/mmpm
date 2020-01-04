#!/usr/bin/env python3

import os
import sys
import time
import json
import shutil
import argparse
import datetime
import textwrap
import subprocess
from urllib.request import urlopen
from collections import defaultdict
from colorama import Fore, Style
from bs4 import BeautifulSoup
from tabulate import tabulate
from mmpm import utils, colors, core

__version__ = 0.36


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
            for i, _ in enumerate(value):
                title = value[i]["Title"]
                desc = value[i]["Description"]
                repo = value[i]["Repository"]
                author = value[i]["Author"]

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

    modules_dir = utils.HOME_DIR + "/MagicMirror/modules"

    original_dir = os.getcwd()

    if not os.path.exists(modules_dir):
        utils.error_msg("The directory '{}' does not exist. Have you installed MagicMirror properly?".format(modules_dir))

    os.chdir(modules_dir)

    successful_installs = []

    for value in modules_table.values():
        curr_subdir = os.getcwd()

        for i in range(len(value)):
            if value[i]["Title"] in modules_to_install:
                title = value[i]["Title"]
                target = os.getcwd() + "/" + title
                repo = value[i]["Repository"]

                successful_installs.append(title)

                try:
                    os.mkdir(target)

                except OSError:
                    utils.error_msg("The {0} module already exists. To remove the module, run 'mmpm -r {0}'".format(title))

                os.chdir(target)

                print(colors.BRIGHT_GREEN +
                      "Installing {}".format(value[i]["Title"]) +
                      Fore.YELLOW +
                      " @ " +
                      Fore.GREEN +
                      "{}\n".format(target))

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

    if not os.path.exists(utils.HOME_DIR + "/MagicMirror"):
        print(colors.BRIGHT_CYAN +
              "MagicMirror directory not found. " +
              colors.NORMAL_WHITE +
              "Installing MagicMirror..." +
              colors.NORMAL_WHITE)

        os.system(
            'bash -c "$(curl -sL https://raw.githubusercontent.com/MichMich/MagicMirror/master/installers/raspberry.sh)"')

    else:
        message = colors.BRIGHT_CYAN + "MagicMirror directory found. " + colors.NORMAL_WHITE
        message += "Would you like to check for updates? "
        message += "[yes/no | y/n]: "

        valid_response = False

        while not valid_response:
            response = input(message)

            if response in ("yes", "y"):
                os.chdir(utils.HOME_DIR + "/MagicMirror")

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

    modules_dir = utils.HOME_DIR + "/MagicMirror/modules"
    original_dir = os.getcwd()

    if not os.path.exists(modules_dir):
        utils.error_msg("The '{}' directory doesn't exist. Have you installed MagicMirror?".format(modules_dir))

    os.chdir(modules_dir)
    successful_removals = []
    curr_dir = os.getcwd()

    for module in modules_to_remove:
        dir_to_rm = curr_dir + "/" + module

        try:
            shutil.rmtree(dir_to_rm)
            successful_removals.append(module)

        except OSError:
            utils.warning_msg("The directory for '{}' does not exist.".format(module))

    if successful_removals:
        print(colors.BRIGHT_GREEN + "The following modules were successfully deleted:" + Style.NORMAL)

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

        core.check_for_mmpm_enhancements()
        checked_for_enhancements = True

    else:
        with open(snapshot_file, "r") as f:
            modules = json.load(f)

    curr_snap = datetime.datetime.fromtimestamp(int(curr_snap))
    next_snap = datetime.datetime.fromtimestamp(int(next_snap))

    return modules, curr_snap, next_snap, checked_for_enhancements


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

        for key, value in modules_table.items():
            for i, _ in enumerate(value):
                rows.append([
                    key,
                    value[i]["Title"],
                    textwrap.fill(value[i]["Repository"]),
                    textwrap.fill(value[i]["Author"], width=12),
                    textwrap.fill(value[i]["Description"], width=15)
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

    original_dir = os.getcwd()
    modules_dir = utils.HOME_DIR + "/MagicMirror/modules"

    if not os.path.exists(modules_dir):
        utils.error_msg("The directory '{}' does not exist. ".format(modules_dir) +
                  "Have you installed MagicMirror properly?")

    os.chdir(modules_dir)

    module_dirs = os.listdir(os.getcwd())

    installed_modules = []

    for values in modules_table.values():
        for value in values:
            if value['Title'] in module_dirs:
                installed_modules.append(value['Title'])

    os.chdir(original_dir)

    return installed_modules


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



def main(argv):
    arg_parser = argparse.ArgumentParser(prog="mmpm",
                                         epilog='''
                                                Detailed usage found at
                                                https://github.com/Bee-Mar/mmpm
                                                ''',
                                         description='''
                                                    The MagicMirror Package
                                                    Manager is a CLI designed
                                                    to simplify the
                                                    installation, removal, and
                                                    maintenance of MagicMirror
                                                    modules.
                                                    ''')

    arg_parser.add_argument("-u",
                            "--update",
                            action="store_true",
                            help='''
                                Check for updates for each of the currently
                                installed modules.
                                ''')

    arg_parser.add_argument("-U",
                            "--upgrade",
                            action="append",
                            nargs="*",
                            help='''
                                 Upgrades currently installed modules. If no
                                 module name is supplied, all modules will be
                                 upgraded. To upgrade specific modules, supply
                                 one or more module name, space delimited.
                                 ''')

    arg_parser.add_argument("-e",
                            "--enhance-mmpm",
                            action="store_true",
                            help='''
                                Checks if enhancements are available for MMPM.
                                User will be prompted if an upgrade is
                                available.
                                ''')

    arg_parser.add_argument("-a",
                            "--all",
                            action="store_true",
                            help="Lists all currently available modules.")

    arg_parser.add_argument("-f",
                            "--force-refresh",
                            action="store_true",
                            help='''
                                Forces a refresh of the modules database
                                snapshot.
                                ''')

    arg_parser.add_argument("-c",
                            "--categories",
                            action="store_true",
                            help='''
                                Lists names of all module categories, ie.
                                Finance, Weather, etc.
                                ''')

    arg_parser.add_argument("-s",
                            "--search",
                            nargs=1,
                            help='''
                                Lists all modules whose information contains
                                the matching string as a category name or
                                substring of the title, author, or description.
                                First, attempts to match the string to the
                                category name is made. If the search fails,
                                attempts to match substrings in the title,
                                description, or author are made. For any
                                searches containing more than one word,
                                surround the search in quotations.
                                Additionally, when searching for modules based
                                on category names, the query is case-sensitive.
                                When searches do not match category names for
                                the query, the search automatically becomes
                                non-case-sensitive. When searching for a
                                category with a lengthy name, it is best to
                                copy and paste the exact name from the results
                                produced by 'mmpm -c' (or the equivalent 'mmpm
                                    --categories'), and surround the name in
                                quotations.
                                ''')

    arg_parser.add_argument("-d",
                            "--snapshot-details",
                            action="store_true",
                            help='''
                                Display details about the most recent snapshot
                                of the MagicMirror 3rd Party Modules taken.
                                '''
                            )

    arg_parser.add_argument("-M",
                            "--magicmirror",
                            action="store_true",
                            help='''
                                Installs the most recent version of MagicMirror
                                based on instructions from the MagicMirror
                                GitHub repo. First, your system will be checked
                                for a an existing installation of MagicMirror,
                                and if one is found, it will check for updates.
                                Otherwise, it will perform a new installation.
                                '''
                            )

    arg_parser.add_argument("-i",
                            "--install",
                            nargs="+",
                            help='''
                                Installs module(s) with given name(s) separated
                                by spaces. Installation candidate names are
                                case-sensitive.
                                '''
                            )

    arg_parser.add_argument("-r",
                            "--remove",
                            nargs="+",
                            help='''
                                Removes module(s) with given name(s) separated
                                by spaces. Removal candidate names are
                                case-sensitive.
                                '''
                            )

    arg_parser.add_argument("-l",
                            "--list-installed",
                            action="store_true",
                            help='''
                                Lists all currently installed modules.
                                '''
                            )

    arg_parser.add_argument("-v",
                            "--version",
                            action="store_true",
                            help='''
                                Displays MMPM version.
                                '''
                            )

    if len(argv) < 2:
        arg_parser.print_help()
        exit(0)

    args = arg_parser.parse_args()

    modules_table = {}

    snapshot_file = utils.HOME_DIR + "/.magic_mirror_modules_snapshot.json"

    modules_table, curr_snap, next_snap, checked_enhancements = load_modules(snapshot_file, args.force_refresh)

    if args.all:
        display_modules(modules_table, list_all=True, list_categories=False)

    elif args.categories:
        display_modules(modules_table, list_all=False, list_categories=True)

    elif args.search:
        display_modules(search_modules(modules_table, args.search), list_all=True, list_categories=False)

    elif args.install:
        install_modules(modules_table, args.install)

    elif args.magicmirror:
        install_magicmirror()

    elif args.remove:
        installed_modules = get_installed_modules(modules_table)
        remove_modules(installed_modules, args.remove)

    elif args.list_installed:
        installed_modules = get_installed_modules(modules_table)

        if not installed_modules:
            utils.error_msg("No modules are currently installed")

        print(colors.BRIGHT_CYAN + "Module(s) Installed:\n" + colors.NORMAL_WHITE)

        for module in installed_modules:
            print(module)

    elif args.snapshot_details or args.force_refresh:
        core.snapshot_details(modules_table, curr_snap, next_snap)

    elif args.update:
        core.enhance_modules(modules_table, update=True, upgrade=False, modules_to_upgrade=None)

    elif args.upgrade:
        core.enhance_modules(modules_table, update=False, upgrade=True, modules_to_upgrade=args.upgrade[0])

    elif args.enhance_mmpm and not checked_enhancements:
        core.check_for_mmpm_enhancements()

    elif args.version:
        print(colors.BRIGHT_CYAN + "MMPM Version: " + colors.BRIGHT_WHITE + "{}".format(__version__))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        utils.error_msg("Caught keyboard interrupt. Exiting")
