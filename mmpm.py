#!/usr/bin/python3
import os
import sys
import time
import json
import shutil
import pygit2
import argparse
import datetime
import subprocess
import urllib.request
from math import floor
from bs4 import BeautifulSoup
from collections import defaultdict
from colorama import Fore, Back, Style


def error_msg(msg):
    print(Fore.RED + Style.BRIGHT + "ERROR: " + Fore.WHITE + msg)
    exit(0)


def warning_msg(msg):
    print(Fore.YELLOW + Style.BRIGHT + "WARNING: " + Fore.WHITE + msg)


def update_or_upgrade_modules(modules_table, update=False, upgrade=True, modules_to_upgrade=None):
    original_dir = os.getcwd()
    modules_dir = os.path.expanduser("~") + "/MagicMirror/modules"
    os.chdir(modules_dir)

    updates_avail = False
    updates_list = []

    dirs = os.listdir(modules_dir)

    if upgrade and modules_to_upgrade:
        dirs = modules_to_upgrade

    if update:
        print(Style.BRIGHT +
              Fore.CYAN +
              "Checking for updates..." +
              Fore.WHITE +
              Style.NORMAL
              )

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
                    print(Style.BRIGHT +
                          Fore.CYAN +
                          "Requesting upgrade for {}...".format(title) +
                          Fore.WHITE +
                          Style.NORMAL
                          )

                    os.system("git pull")
                    os.system("npm install")

                print("\n")
                os.chdir(modules_dir)

    os.chdir(original_dir)

    if update:
        if not updates_list:
            print(Fore.WHITE + Style.BRIGHT +
                  "No updates available." + Style.NORMAL)
        else:
            print(Fore.MAGENTA +
                  Style.BRIGHT +
                  "Updates are available for the following modules:\n" +
                  Style.NORMAL +
                  Fore.WHITE
                  )

            for i in range(len(updates_list)):
                print("{}".format(updates_list[i]))

            print(Style.BRIGHT +
                  "\nTo update all modules, execute 'mmpm -U', or you may choose individual " +
                  "modules to update\nby executing mmpm -U followed by the name of the modules(s).'" +
                  "For example:" +
                  Fore.GREEN +
                  Style.BRIGHT +
                  "\n\n'mmpm -U {}'".format(updates_list[0]) +
                  Fore.WHITE +
                  Style.NORMAL +
                  "\n"
                  )


def search_modules(modules_table, search):

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

    modules_dir = os.path.expanduser("~") + "/MagicMirror/modules"
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

                print(Fore.GREEN +
                      Style.BRIGHT +
                      "Installing {}".format(value[i]["Title"]) +
                      Fore.YELLOW +
                      " @ " +
                      Fore.GREEN +
                      "{}\n".format(target) +
                      Fore.WHITE)

                print(Fore.CYAN + "Cloning repository for {}...".format(title))
                pygit2.clone_repository(repo, target)
                print(Fore.CYAN + "Repository cloned...")
                print(Fore.CYAN +
                      "Installing NodeJS dependencies...\n" +
                      Fore.WHITE +
                      Style.NORMAL
                      )
                os.system("npm install")
                os.chdir(curr_subdir)
                print("\n")

    os.chdir(original_dir)

    for i in range(len(modules_to_install)):
        if modules_to_install[i] not in successful_installs:
            msg = "Unable to match '{}' ".format(modules_to_install[i])
            msg += "with installation candidate. Is the title casing correct?\n"
            warning_msg(msg)

    print(Fore.GREEN +
          Style.BRIGHT +
          "To finish installation, populate " +
          Fore.WHITE +
          "'~/MagicMirror/config/config.js'" +
          Fore.GREEN +
          "\nwith the necessary configurations for each of the newly installed modules.\n" +
          Fore.WHITE +
          Style.NORMAL +
          "\nWhile I did my best to install dependencies for you, " +
          "there may be additional steps required\nto fully setup each of the modules " +
          "(ie. running 'make' for specific targets within each directory).\n\n" +
          "Review the GitHub pages for each of the newly installed modules " +
          "for any additional instructions.\n"
          )


def remove_modules(installed_modules, modules_to_remove):

    if not installed_modules:
        error_msg("No modules are currently installed.")

    modules_dir = os.path.expanduser("~") + "/MagicMirror/modules"
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
        print(Fore.GREEN +
              Style.BRIGHT +
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

    modules = {}
    curr_snap = 0
    refresh_interval = 6

    if not force_refresh and os.path.exists(snapshot_file):
        curr_snap = os.path.getmtime(snapshot_file)
        next_snap = curr_snap + refresh_interval * 60 * 60
    else:

        next_snap = curr_snap = time.time()

    # if the snapshot has expired, get a new one
    if force_refresh or next_snap - time.time() <= 0.0:
        modules = retrieve_modules()
        with open(snapshot_file, "w") as f:  # save the new snapshot
            json.dump(modules, f)

        curr_snap = os.path.getmtime(snapshot_file)
        next_snap = curr_snap + refresh_interval * 60 * 60

    else:
        with open(snapshot_file, "r") as f:
            modules = json.load(f)

    curr_snap = datetime.datetime.fromtimestamp(int(curr_snap))
    next_snap = datetime.datetime.fromtimestamp(int(next_snap))

    return modules, curr_snap, next_snap


def display_all_modules(modules_table, list_all=False, list_categories=False):

    if list_categories:
        count = 1

        print(Fore.CYAN +
              Style.BRIGHT +
              "MagicMirror Module Categories\n" +
              Fore.WHITE +
              Style.NORMAL
              )

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

    original_dir = os.getcwd()
    modules_dir = os.path.expanduser("~") + "/MagicMirror/modules"
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
        categories.append(categories_soup[i].contents[last_element])

    tr_soup = []
    table_soups = []
    hrefs = []
    anchor_tags = []

    for table in table_soup:
        tr_soup.append(table.find_all("tr"))

    for (i, row) in enumerate(tr_soup):
        modules.update({categories[i+1]: list()})
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

                modules[categories[i+1]].append({
                    "Title": title,
                    "Repository": repo,
                    "Author": author,
                    "Description": desc
                })

    return modules


def snapshot_details(modules, curr_snap, next_snap):

    num_categories = len(modules.keys())
    num_modules = 0

    for key, value in modules.items():
        num_modules += len(modules[key])

    print(Style.BRIGHT +
          Fore.WHITE +
          Fore.YELLOW +
          "\nMost recent snapshot of MagicMirror Modules taken @ " +
          Style.NORMAL +
          Fore.WHITE +
          "{}.".format(curr_snap) +
          Style.BRIGHT +
          Fore.YELLOW + "\n"
          "The next snapshot will be taken on or after " +
          Style.NORMAL +
          Fore.WHITE +
          "{}.\n".format(next_snap) +
          Style.BRIGHT +
          "\nModule Categories: " +
          Fore.GREEN +
          "{}\n".format(num_categories) +
          Fore.WHITE +
          "Modules Available: " +
          Fore.GREEN +
          "{}\n".format(num_modules) +
          Style.NORMAL +
          Fore.WHITE +
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

    if len(argv) < 2:
        arg_parser.print_help()
        exit(0)

    args = arg_parser.parse_args()

    modules_table = {}
    installed_modules_table = {}

    home_dir = os.path.expanduser("~")
    snapshot_file = home_dir + "/.magic_mirror_modules_snapshot.json"

    modules_table, curr_snap, next_snap = load_modules(snapshot_file,
                                                       args.force_refresh
                                                       )

    if args.all:
        display_all_modules(modules_table,
                            list_all=True,
                            list_categories=False
                            )

    elif args.categories:
        display_all_modules(modules_table,
                            list_all=False,
                            list_categories=True
                            )

    elif args.search:
        display_all_modules(search_modules(modules_table, args.search),
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

        print(Fore.CYAN +
              Style.BRIGHT +
              "Module(s) Installed:\n" +
              Fore.WHITE +
              Style.NORMAL
              )

        for i in range(len(installed_modules)):
            print(installed_modules[i])

    elif args.snapshot_details or args.force_refresh:
        snapshot_details(modules_table, curr_snap, next_snap)

    elif args.update:
        update_or_upgrade_modules(modules_table, update=True, upgrade=False)

    elif args.upgrade:
        update_or_upgrade_modules(modules_table,
                                  update=False,
                                  upgrade=True,
                                  modules_to_upgrade=args.upgrade[0]
                                  )


if __name__ == "__main__":
    main(sys.argv)
