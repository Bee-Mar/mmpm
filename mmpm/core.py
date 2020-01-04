#!/usr/bin/env python3
import re
import os
import subprocess
from mmpm import colors, utils, mmpm
from urllib.error import HTTPError
from urllib.request import urlopen


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
    modules_dir = utils.HOME_DIR + "/MagicMirror/modules"
    os.chdir(modules_dir)

    updates_list = []

    dirs = os.listdir(modules_dir)

    if upgrade and modules_to_upgrade:
        dirs = modules_to_upgrade

    if update:
        print(colors.BRIGHT_CYAN + "Checking for updates..." + colors.NORMAL_WHITE)

    for _, value in modules_table.items():
        for i, _ in enumerate(value):
            if value[i]["Title"] in dirs:
                title = value[i]["Title"]
                curr_module_dir = modules_dir + "/" + title

                os.chdir(curr_module_dir)

                if update:
                    git_status = subprocess.run(["git", "fetch", "--dry-run"], stdout=subprocess.PIPE)

                    if git_status.stdout:
                        updates_list.append(title)

                elif upgrade:
                    print(colors.BRIGHT_CYAN + "Requesting upgrade for {}...".format(title) + colors.NORMAL_WHITE)

                    os.system("git pull")

                    if os.path.isfile(os.getcwd() + "/package.json"):
                        print(colors.BRIGHT_CYAN + "Found package.json. Installing NodeJS dependencies..." + colors.NORMAL_WHITE)
                        os.system("$(which npm) install")

                os.chdir(modules_dir)

    os.chdir(original_dir)

    if update:
        if not updates_list:
            print(colors.BRIGHT_WHITE + "No updates available." + colors.NORMAL)
        else:
            print(colors.BRIGHT_MAGENTA + "Updates are available for the following modules:\n" + colors.NORMAL_WHITE)

            for _, update in enumerate(updates_list):
                print("{}".format(update))

            print(colors.BRIGHT +
                  "\nTo update all modules, execute 'mmpm -U', or you may " +
                  "individual modules\nby executing mmpm -U followed by the" +
                  "name of the modules(s).' For example:" +
                  colors.BRIGHT_GREEN +
                  "\n\n'mmpm -U {}'".format(updates_list[0]) +
                  colors.NORMAL_WHITE +
                  "\n")
