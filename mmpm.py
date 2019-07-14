#!/usr/bin/env python3
import os
import re
import sys
import pip
import time
import json
import shutil
import datetime
import subprocess
import urllib.error
import urllib.request
from math import floor
from collections import defaultdict


try:
    import argparse
except ImportError:
    print("ArgParse package not found. Pip installing with --user flag.")
    print("==========================================================\n")
    pip.main(["install", "--user", "argparse"])
    print("\n\n")

try:
    import pygit2
except ImportError:
    print("PyGit2 package not found. Pip installing with --user flag.")
    print("==========================================================\n")
    pip.main(["install", "--user", "pygit2"])
    print("\n\n")

try:
    import bs4
except ImportError:
    print("BeautifulSoup4 package not found. Pip installing with --user flag.")
    print("==================================================================\n")
    pip.main(["install", "--user", "bs4"])
    print("\n\n")

try:
    import colorama
except ImportError:
    print("Colorama package not found. Pip installing with --user flag.")
    print("============================================================\n")
    pip.main(["install", "--user", "colorama"])
    print("\n\n")

import pygit2
import argparse
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style

__version__ = 0.2

BRIGHT_CYAN = Style.BRIGHT + Fore.CYAN
BRIGHT_GREEN = Style.BRIGHT + Fore.GREEN
BRIGHT_MAGENTA = Style.BRIGHT + Fore.MAGENTA
BRIGHT_WHITE = Style.BRIGHT + Fore.WHITE
BRIGHT_YELLOW = Style.BRIGHT + Fore.YELLOW
NORMAL_WHITE = Style.NORMAL + Fore.WHITE

home_dir = os.path.expanduser("~")


def error_msg(msg):
    '''
    Displays error message to user, and exits program.

    Arguments
    =========
    msg: String
    '''
    print(Fore.RED + Style.BRIGHT + "ERROR: " + Fore.WHITE + msg)
    exit(0)


def warning_msg(msg):
    '''
    Displays warning message to user and continues program execution.

    Arguments
    =========
    msg: String
    '''
    print(BRIGHT_YELLOW + "WARNING: " + Fore.WHITE + msg)


def check_for_mmpm_enhancements():
    '''
    Scrapes the main file of MMPM off the github repo, and compares the current
    version, versus the one available in the master branch. If there is a newer
    version, the user is prompted for an upgrade.

    Arguments
    =========
    None

    '''
    mmpm_repository = "https://github.com/Bee-Mar/mmpm.git"
    mmpm_main_file = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm.py"

    try:
        mmpm_file = urllib.request.urlopen(mmpm_main_file)
        contents = str(mmpm_file.read())
        version_line = re.findall("__version__ = \d+\.\d+", contents)

        version_number = re.findall("\d+\.\d+", version_line[0])
        version_number = float(version_number[0])

        if version_line and __version__ < version_number:
            valid_response = False

            while not valid_response:
                user_response = input(BRIGHT_GREEN +
                                      "MMPM has an upgrade available. "
                                      + NORMAL_WHITE +
                                      "Would you like to upgrade now? [yes/no | y/n] " +
                                      NORMAL_WHITE
                                      )

                if 'yes' in user_response or 'y' in user_response:
                    original_dir = os.getcwd()

                    os.chdir(home_dir + "/Downloads")
                    os.system("rm -rf mmpm")
                    os.system("git clone {}".format(mmpm_repository))
                    os.chdir("mmpm")
                    os.system("make")

                    os.chdir(original_dir)

                    os.system("rm -rf " + home_dir + "/Downloads/mmpm")

                    print("Newly cloned MMPM repository in ~/Downloads.")
                    print("Feel free to remove the directory.")

                    valid_response = True

                elif 'no' in user_response or 'n' in user_response:
                    valid_response = True
                else:
                    warning_msg("Respond with yes/no or y/n.")

    except urllib.error.HTTPError as err:
        pass


def enhance_modules(modules_table, update=False, upgrade=True, modules_to_upgrade=None):
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
    modules_dir = home_dir + "/MagicMirror/modules"
    os.chdir(modules_dir)

    updates_avail = False
    updates_list = []

    dirs = os.listdir(modules_dir)

    if upgrade and modules_to_upgrade:
        dirs = modules_to_upgrade

    if update:
        print(BRIGHT_CYAN + "Checking for updates..." + NORMAL_WHITE)

    for key, value in modules_table.items():
        for i in range(len(value)):
            if value[i]["Title"] in dirs:
                title = value[i]["Title"]
                curr_module_dir = modules_dir + "/" + title

                os.chdir(curr_module_dir)

                if update:
                    git_status = subprocess.run(["git", "fetch", "--dry-run"],
                                                stdout=subprocess.PIPE)

                    if git_status.stdout:
                        updates_list.append(title)

                elif upgrade:
                    print(BRIGHT_CYAN +
                          "Requesting upgrade for {}...".format(title) +
                          NORMAL_WHITE
                          )

                    os.system("git pull")
                    os.system("npm install")

                print("\n")
                os.chdir(modules_dir)

    os.chdir(original_dir)

    if update:
        if not updates_list:
            print(BRIGHT_WHITE + "No updates available." + Style.NORMAL)
        else:
            print(BRIGHT_MAGENTA +
                  "Updates are available for the following modules:\n" +
                  NORMAL_WHITE
                  )

            for i in range(len(updates_list)):
                print("{}".format(updates_list[i]))

            print(Style.BRIGHT +
                  "\nTo update all modules, execute 'mmpm -U', or you may choose individual " +
                  "modules to update\nby executing mmpm -U followed by the name of the modules(s).'" +
                  "For example:" +
                  BRIGHT_GREEN +
                  "\n\n'mmpm -U {}'".format(updates_list[0]) +
                  NORMAL_WHITE +
                  "\n"
                  )


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

    try:
        for query in search:
            if modules_table[query]:
                search_results[query] = modules_table[query]

        return search_results

    except KeyError as err:
        pass

    try:
        search_results = defaultdict(list)

        for query in search:
            query = query.lower()

            for key, value in modules_table.items():
                for i in range(len(value)):
                    title = value[i]["Title"]
                    desc = value[i]["Description"]
                    repo = value[i]["Repository"]
                    author = value[i]["Author"]

                    if query in title.lower() or query in desc.lower() or query in author.lower():
                        entry = {"Title": title,
                                 "Repository": repo,
                                 "Author": author,
                                 "Description": desc
                                 }

                        if entry not in search_results[key]:
                            search_results[key].append(entry)

        return search_results

    except KeyError as err:
        pass


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

    modules_dir = home_dir + "/MagicMirror/modules"

    original_dir = os.getcwd()

    if not os.path.exists(modules_dir):
        msg = "The directory '{}' does not exist. ".format(modules_dir)
        msg += "Have you installed MagicMirror properly?"
        error_msg(msg)

    os.chdir(modules_dir)

    successful_installs = []

    for key, value in modules_table.items():
        curr_subdir = os.getcwd()

        for i in range(len(value)):
            if value[i]["Title"] in modules_to_install:
                title = value[i]["Title"]
                target = os.getcwd() + "/" + title
                repo = value[i]["Repository"]

                successful_installs.append(title)

                try:
                    os.mkdir(target)

                except FileExistsError as err:
                    msg = "The {} module already exists. ".format(title)
                    msg += "To remove the module, run 'mmpm -r {}'".format(
                        title)
                    error_msg(msg)

                os.chdir(target)

                print(BRIGHT_GREEN +
                      "Installing {}".format(value[i]["Title"]) +
                      Fore.YELLOW +
                      " @ " +
                      Fore.GREEN +
                      "{}\n".format(target) +
                      Fore.WHITE
                      )

                print(Fore.CYAN + "Cloning repository for {}...".format(title))

                pygit2.clone_repository(repo, target)

                print(Fore.CYAN + "Repository cloned...")
                print(Fore.CYAN + "Installing NodeJS dependencies...\n" + NORMAL_WHITE)

                os.system("npm install")
                os.chdir(curr_subdir)

                print("\n")

    os.chdir(original_dir)

    for i in range(len(modules_to_install)):
        if modules_to_install[i] not in successful_installs:
            msg = "Unable to match '{}' ".format(modules_to_install[i])
            msg += "with installation candidate. Is the title casing correct?\n"
            warning_msg(msg)

    print(BRIGHT_GREEN +
          "To finish installation, populate " +
          Fore.WHITE +
          "'~/MagicMirror/config/config.js'" +
          Fore.GREEN +
          "\nwith the necessary configurations for each of the newly installed modules.\n" +
          NORMAL_WHITE +
          "\nWhile I did my best to install dependencies for you, " +
          "there may be additional steps required\nto fully setup each of the modules " +
          "(ie. running 'make' for specific targets within each directory).\n\n" +
          "Review the GitHub pages for each of the newly installed modules " +
          "for any additional instructions.\n"
          )


def remove_modules(installed_modules, modules_to_remove):
    '''
    Gathers list of modules currently installed in the ~/MagicMirror/modules
    directory, and removes each of the modules from the folder, if modules are
    currently installed. Otherwise, the user is shown an error message alerting
    them no modules are currently installed.

    Arguments
    =========
    modules_table: Dictionary
    modules_to_install: List
    '''

    if not installed_modules:
        error_msg("No modules are currently installed.")

    modules_dir = home_dir + "/MagicMirror/modules"
    original_dir = os.getcwd()

    if not os.path.exists(modules_dir):
        msg = "The '{}' directory doesn't exist.".format(modules_dir)
        msg += "have you installed magicmirror?"
        error_msg(msg)

    os.chdir(modules_dir)

    successful_removals = []

    curr_dir = os.getcwd()
    dir = os.listdir(curr_dir)

    for i in range(len(modules_to_remove)):
        module = modules_to_remove[i]
        dir_to_rm = curr_dir + "/" + module

        try:
            shutil.rmtree(dir_to_rm)
            successful_removals.append(module)

        except FileNotFoundError as err:
            msg = "The directory for '{}' does not exist.".format(module)
            warning_msg(msg)

    if successful_removals:
        print(BRIGHT_GREEN +
              "The following modules were successfully deleted:" +
              Style.NORMAL
              )

        for i in range(len(successful_removals)):
            print(Fore.WHITE + "{} ".format(successful_removals[i]), end="")

    else:
        error_msg("Unable to remove modules.")

    print("\n")
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

    if not force_refresh and os.path.exists(snapshot_file):
        curr_snap = os.path.getmtime(snapshot_file)
        next_snap = curr_snap + refresh_interval * 60 * 60
    else:
        next_snap = curr_snap = time.time()

    # if the snapshot has expired, or doesn't exist, get a new one
    if not os.path.exists(snapshot_file) or force_refresh or next_snap - time.time() <= 0.0:
        modules = retrieve_modules()
        with open(snapshot_file, "w") as f:  # save the new snapshot
            json.dump(modules, f)

        curr_snap = os.path.getmtime(snapshot_file)
        next_snap = curr_snap + refresh_interval * 60 * 60

        check_for_mmpm_enhancements()

    else:
        with open(snapshot_file, "r") as f:
            modules = json.load(f)

    curr_snap = datetime.datetime.fromtimestamp(int(curr_snap))
    next_snap = datetime.datetime.fromtimestamp(int(next_snap))

    return modules, curr_snap, next_snap


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
        count = 1

        print(BRIGHT_CYAN + "MagicMirror Module Categories\n" + NORMAL_WHITE)

        for key in modules_table.keys():
            print("{}) {}".format(count, key))
            count += 1

        print("\n")

    elif list_all:
        for key, value in modules_table.items():
            for i in range(len(value)):
                val = value[i]
                print(Fore.CYAN + "{}".format("Category: ") +
                      Fore.WHITE + "{}".format(key))

                print(Fore.CYAN + "{}".format("Title: ") +
                      Fore.WHITE + "{}".format(val["Title"]))

                print(Fore.CYAN + "{}".format("Repository: ") +
                      Fore.WHITE + "{}".format(val["Repository"]))
                print(Fore.CYAN + "{}".format("Author: ") +
                      Fore.WHITE + "{}".format(val["Author"]))
                print(Fore.CYAN + "{}".format("Description: ") +
                      Fore.WHITE + "{}".format(val["Description"]))
                print("\n")


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
    modules_dir = home_dir + "/MagicMirror/modules"

    if not os.path.exists(modules_dir):
        msg = "The directory '{}' does not exist. ".format(modules_dir)
        msg += "Have you installed MagicMirror properly?"
        error_msg(msg)

    os.chdir(modules_dir)

    module_dirs = os.listdir(os.getcwd())

    installed_modules = []

    for key, value in modules_table.items():
        for i in range(len(value)):
            if value[i]["Title"] in module_dirs:
                installed_modules.append(value[i]["Title"])

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
    web_page = urllib.request.urlopen(mmm_url).read()

    soup = BeautifulSoup(web_page, "html.parser")
    table_soup = soup.find_all("table")

    category_soup = soup.find_all(attrs={"class": "markdown-body"})
    categories_soup = category_soup[0].find_all("h3")

    categories = []

    for (i, row) in enumerate(categories_soup):
        last_element = len(categories_soup[i].contents) - 1
        new_category = categories_soup[i].contents[last_element]

        if new_category != "General Advice":
            categories.append(new_category)

    tr_soup = []
    table_soups = []
    hrefs = []
    anchor_tags = []

    for table in table_soup:
        tr_soup.append(table.find_all("tr"))

    for (i, row) in enumerate(tr_soup):
        modules.update({categories[i]: list()})

        for (j, value) in enumerate(row):
            # ignore the cells that contain literally say "Title", "Author", "Description"
            if j > 0:
                td_soup = tr_soup[i][j].find_all("td")

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
                        for content in td_soup[k].contents:
                            if type(content).__name__ == "Tag":
                                for stuff in content:
                                    desc += stuff
                            else:
                                desc += content

                        desc = str(desc)

                modules[categories[i]].append({
                    "Title": title,
                    "Repository": repo,
                    "Author": author,
                    "Description": desc
                })

    return modules


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

    for key, value in modules.items():
        num_modules += len(modules[key])

    print(BRIGHT_YELLOW +
          "\nMost recent snapshot of MagicMirror Modules taken @ " +
          NORMAL_WHITE +
          "{}.".format(curr_snap) +
          BRIGHT_YELLOW +
          "\n"
          "The next snapshot will be taken on or after " +
          NORMAL_WHITE +
          "{}.\n".format(next_snap) +
          Style.BRIGHT +
          "\nModule Categories: " +
          Fore.GREEN +
          "{}\n".format(num_categories) +
          Fore.WHITE +
          "Modules Available: " +
          Fore.GREEN +
          "{}\n".format(num_modules) +
          NORMAL_WHITE +
          "\nTo forcibly refresh the snapshot, run 'mmpm -f' or 'mmpm --force-refresh'\n"
          )


def main(argv):
    arg_parser = argparse.ArgumentParser(prog="mmpm",
                                         epilog='''
                                                NOTE: See the GitHub page for
                                                more thorough examples of usage.
                                                ''',
                                         description='''
                                                    The MagicMirror Package
                                                    Manager is a command line
                                                    interface designed to
                                                    simplify the installation,
                                                    removal, and maintenance of
                                                    MagicMirror modules.
                                                    '''
                                         )

    arg_parser.add_argument("-u",
                            "--update",
                            action="store_true",
                            help="Check for updates for each of the currently installed modules."
                            )

    arg_parser.add_argument("-U",
                            "--upgrade",
                            action="append",
                            nargs="*",
                            help='''
                                 Upgrades modules currently installed. If no module name(s)
                                 follows the upgrade command, all modules will be upgraded.
                                 To upgrade specific modules, supply one or more module names,
                                 each separated by a space. For example, 'mmpm -U MMM-Simple-Swiper
                                 MMM-pages'
                                 '''
                            )

    arg_parser.add_argument("-a",
                            "--all",
                            action="store_true",
                            help="Lists all currently available modules."
                            )

    arg_parser.add_argument("-f",
                            "--force-refresh",
                            action="store_true",
                            help="Forces a refresh of the modules database snapshot."
                            )

    arg_parser.add_argument("-c",
                            "--categories",
                            action="store_true",
                            help="Lists names of all module categories, ie. Finance, Weather, etc."
                            )

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
                                '''
                            )

    arg_parser.add_argument("-d",
                            "--snapshot-details",
                            action="store_true",
                            help='''
                                Display details about the most recent snapshot of the
                                MagicMirror 3rd Party Modules taken.
                                '''
                            )

    arg_parser.add_argument("-i",
                            "--install",
                            nargs="+",
                            help='''
                                Installs module(s) with given name(s) separated
                                by spaces.  Installation candidate names are
                                case-sensitive.
                                '''
                            )

    arg_parser.add_argument("-r",
                            "--remove",
                            nargs="+",
                            help='''
                                Removes module(s) with given name(s) separated by spaces.
                                Removal candidate names are case-sensitive.
                                '''
                            )

    arg_parser.add_argument("-L",
                            "--list-installed",
                            action="store_true",
                            help="Lists all currently installed modules."
                            )

    arg_parser.add_argument("-v",
                            "--version",
                            action="store_true",
                            help="Displays MMPM version."
                            )

    if len(argv) < 2:
        arg_parser.print_help()
        exit(0)

    args = arg_parser.parse_args()

    modules_table = {}
    installed_modules_table = {}

    snapshot_file = home_dir + "/.magic_mirror_modules_snapshot.json"

    modules_table, curr_snap, next_snap = load_modules(snapshot_file,
                                                       args.force_refresh
                                                       )

    if args.all:
        display_modules(modules_table, list_all=True, list_categories=False)

    elif args.categories:
        display_modules(modules_table, list_all=False, list_categories=True)

    elif args.search:
        display_modules(search_modules(modules_table, args.search),
                        list_all=True,
                        list_categories=False
                        )

    elif args.install:
        install_modules(modules_table, args.install)

    elif args.remove:
        installed_modules = get_installed_modules(modules_table)
        remove_modules(installed_modules, args.remove)

    elif args.list_installed:
        installed_modules = get_installed_modules(modules_table)

        if not installed_modules:
            error_msg("No modules are currently installed")

        print(BRIGHT_CYAN + "Module(s) Installed:\n" + NORMAL_WHITE)

        for i in range(len(installed_modules)):
            print(installed_modules[i])

    elif args.snapshot_details or args.force_refresh:
        snapshot_details(modules_table, curr_snap, next_snap)

    elif args.update:
        enhance_modules(modules_table, update=True,
                        upgrade=False, modules_to_upgrade=None)

    elif args.upgrade:
        enhance_modules(modules_table, update=False, upgrade=True,
                        modules_to_upgrade=args.upgrade[0])

    elif args.version:
        print(BRIGHT_CYAN + "MMPM Version: " +
              NORMAL_WHITE + "{}".format(__version__))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        error_msg("Caught keyboard interrupt. Exiting")
