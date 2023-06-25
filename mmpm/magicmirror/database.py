#!/usr/bin/env python3
import os
import sys
import pip
import json
import shutil
import datetime
import requests
import urllib.request
import mmpm.consts
import mmpm.color
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.logger import MMPMLogger
from mmpm.singleton import Singleton
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.env import MMPMEnv
from mmpm.constants import paths
from re import findall
from collections import defaultdict
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from pygments import highlight, formatters
from pygments.lexers.data import JsonLexer
from functools import lru_cache
from pathlib import Path, PosixPath
from pygments import highlight, formatters
from pygments.lexers.data import JsonLexer


logger = MMPMLogger.get_logger(__name__)


class MagicMirrorDatabase(Singleton):
    def __init__(self):
        self.packages: List[MagicMirrorPackage] = None
        self.last_update: datetime.datetime = None
        self.expiration_date: datetime.datetime = None
        self.categories: List[str] = None

    def update(self, can_upgrade_mmpm: bool = False, can_upgrade_magicmirror: bool = False) -> int:
        upgradable: List[MagicMirrorPackage] = []

        for package in self.packages:
            if package.is_installed:
                logger.msg.retrieving(package.repository, package.title)
                package.update()

                if package.is_upgradable:
                    upgradable.append(package)

        configuration = self.read_available_upgrades()

        configuration["MagicMirror"] = can_upgrade_magicmirror
        configuration["mmpm"] = can_upgrade_mmpm
        configuration["packages"] = [package.serialize() for package in upgradable]

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="w", encoding="utf-8") as upgrade_file:
            json.dump(configuration, upgrade_file)

        return int(can_upgrade_mmpm) + int(can_upgrade_magicmirror) + len(upgradable)


    def get_upgradable(self) -> dict:
        upgradable = {}

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="r", encoding="utf-8") as upgrade_file:
            upgradable = json.load(upgrade_file)

        return upgradable


    def info(self):
        '''
        Displays information regarding the most recent database file, ie. when it
        was taken, when the next scheduled database retrieval will be taken, how many module
        categories exist, and the total number of modules available. Additionally,
        tells user how to forcibly request the database be updated.

        Parameters:
            packages (Dict[str, List[MagicMirrorPackage]]): Dictionary of MagicMirror modules

        Returns:
            None
        '''
        print(mmpm.color.normal_green('Last updated:'), f'{str(self.last_update.replace(microsecond=0))}')
        print(mmpm.color.normal_green('Next scheduled update:'), f'{str(self.expiration_date.replace(microsecond=0))}')
        print(mmpm.color.normal_green('Categories:'), f'{len(self.categories)}')
        print(mmpm.color.normal_green('Packages:'), f'{len(self.packages)}')


    def download(self):
        '''
        Scrapes the MagicMirror 3rd Party Wiki for all packages listed by community members

        Parameters:
            None

        Returns:
            packages (Dict[str, List[MagicMirrorPackage]]): dictionary of MagicMirror 3rd party modules
        '''

        self.packages: List[MagicMirrorPackage] = []
        response: requests.Response = requests.Response()

        try:
            response = requests.get(mmpm.consts.MAGICMIRROR_MODULES_URL, timeout=10)
        except requests.exceptions.RequestException:
            print(mmpm.consts.RED_X)
            logger.msg.fatal('Unable to retrieve MagicMirror modules.')
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        table_soup = soup.find_all('table')
        categories_soup = soup.find_all(attrs={'class': 'markdown-body'})[0].find_all('h3')

        # the last entry of the html element contents contains the actual category name
        # also skip past "Module Authors" and "General Advice"
        categories: list = [category.contents[-1] for category in categories_soup][2:]

        # the first index is a row that literally says 'Title' 'Author' 'Description'
        tr_soup: list = [table.find_all('tr')[1:] for table in table_soup]

        try:
            for index, row in enumerate(tr_soup):
                for entry in row:
                    table_data: list = entry.find_all('td')

                    if table_data[0].contents[0].contents[0] == "mmpm":
                        continue

                    pkg = MagicMirrorPackage.from_raw_data(table_data, category=categories[index])
                    self.packages.append(pkg)

        except Exception as error:
            logger.msg.fatal(str(error))


    def expired(self) -> bool:
        db_file = mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE
        db_expiration_file = mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE

        for file_name in [db_file, db_expiration_file]:
            if not file_name.exists() or not bool(file_name.stat().st_size):
                return True # the file is empty

        if self.last_update is None or self.expiration_date is None:
            with open(db_expiration_file) as expiration_file:
                data = json.load(expiration_file)
                self.expiration_date = datetime.datetime.fromisoformat(data["expiration"])
                self.last_update = datetime.datetime.fromisoformat(data["last-update"])

        return datetime.datetime.now() > self.expiration_date


    def search(self, query: str, case_sensitive: bool = False, by_title_only: bool = False) -> List[MagicMirrorPackage]:
        '''
        Used to search the 'modules' for either a category, or keyword/phrase
        appearing within module descriptions. If the argument supplied is a
        category name, all modules from that category will be listed. Otherwise,
        all modules whose descriptions contain the keyword/phrase will be
        displayed.

        Parameters:
            query (str): user provided search string
            case_sensitive (bool): if True, the query's exact casing is used in search
            by_title_only (bool): if True, only the title is considered when matching packages to query

        Returns:
            search_results (List[MagicMirrorPackage]): the dictionary of packages, grouped by category that are search matches
        '''

        query = query.strip()

        if by_title_only:
            if case_sensitive:
                match = lambda query, pkg: query == pkg.title
            else:
                query = query.lower()
                match = lambda query, pkg: query == pkg.title.lower()

        else:
            # if the query matches one of the category names exactly, return everything in that category
            if query in self.categories:
                return [package for package in self.packages if package.category == query]
            elif case_sensitive:
                match = lambda query, pkg: query in pkg.description or query in pkg.title or query in pkg.author
            else:
                query = query.lower()
                match = lambda query, pkg: query in pkg.description.lower() or query in pkg.title.lower() or query in pkg.author.lower()

        return [package for package in self.packages if match(query, package)]

    def load(self, refresh: bool = False) -> None:
        '''
        Reads in modules from the hidden database file and checks if the file is
        out of date. If so, the modules are gathered again from the MagicMirror 3rd
        Party Modules wiki.

        Parameters:
            refresh (bool): Boolean flag to force refresh of the database

        Returns:
            None
        '''

        db_file = mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE
        db_exists = db_file.exists() and bool(db_file.stat().st_size)
        ext_pkgs_file = mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE

        if refresh or not db_exists:
            logger.msg.retrieving(mmpm.consts.MAGICMIRROR_MODULES_URL, "Database")
            self.download()

            if not self.packages:
                print(mmpm.consts.RED_X)
                logger.msg.error(f'Failed to retrieve packages from {mmpm.consts.MAGICMIRROR_MODULES_URL}. Please check your internet connection.')
            else:
                with open(db_file, 'w', encoding="utf-8") as db:
                    json.dump(self.packages, db, default=lambda package: package.serialize())

                with open(paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE, 'w', encoding='utf-8') as expiration_file:
                    self.last_update = datetime.datetime.now()
                    self.expiration_date = self.last_update + datetime.timedelta(hours=12)
                    json.dump({"last-update": str(self.last_update), "expiration": str(self.expiration_date)}, expiration_file)

        if not self.packages and db_exists:
            self.packages = []

            with open(db_file, mode="r", encoding="utf-8") as db:
                packages = json.load(db)
                self.packages = [MagicMirrorPackage(**package) for package in packages]

        data = {}

        with open(ext_pkgs_file, mode="r+", encoding="utf-8") as ext_pkgs:
            try:
                data = json.load(ext_pkgs)
            except json.decoder.JSONDecodeError:
                logger.msg.error(f"{ext_pkgs_file} has an invalid layout. Recreating file.")
                logger.error(f"{ext_pkgs_file} has an invalid layout. Recreating file.")
                data = { "External Packages": [] }
                json.dump(data, ext_pkgs)

        for package in data["External Packages"]:
            self.packages.append(MagicMirrorPackage(**package))

        self.categories = {package.category for package in self.packages}

        self.__discover_installed_packages__()


    def __discover_installed_packages__(self) -> None:
        '''
        Scans the list <MMPM_MAGICMIRROR_ROOT>/modules directory, and compares
        against the known packages from the MagicMirror 3rd Party Wiki. Returns a
        dictionary of all found packages

        Parameters:
            packages (Dict[str, List[MagicMirrorPackage]]): Dictionary of MagicMirror packages

        Returns:
            installed_modules (Dict[str, List[MagicMirrorPackage]]): Dictionary of installed MagicMirror packages
        '''

        modules_dir: PosixPath = Path(MMPMEnv.mmpm_magicmirror_root.get()) / 'modules'

        if not modules_dir.exists():
            logger.warning(f"{modules_dir} does not exist")
            return

        package_directories: List[PosixPath] = [directory for directory in modules_dir.iterdir() if directory.is_dir() and (directory / ".git").exists()]

        if not package_directories:
            logger.msg.error('Failed to find MagicMirror root directory.')
            return

        packages_found: List[MagicMirrorPackage] = []

        for package_dir in package_directories:
            try:
                os.chdir(package_dir)

                error_code, remote_origin_url, _ = mmpm.utils.run_cmd(['git', 'config', '--get', 'remote.origin.url'], progress=False)

                if error_code:
                    logger.msg.error(f'Unable to communicate with git server to retrieve information about {package_dir}')
                    continue

                error_code, project_name, _ = mmpm.utils.run_cmd(['basename', remote_origin_url.strip(), '.git'], progress=False)

                if error_code:
                    logger.msg.error(f'Unable to determine repository origin for {project_name}')
                    continue

                packages_found.append(MagicMirrorPackage(repository=remote_origin_url.strip(), directory=package_dir.name))

            except Exception as error:
                logger.msg.error(str(error))
            finally:
                os.chdir(modules_dir)

        for package in self.packages:
            if package in packages_found:
                package.is_installed = True

    def display_categories(self, title_only: bool = False) -> None:
        '''
        Prints module category names and the total number of modules in one of two
        formats. The default is similar to the Debian apt package manager.

        Parameters:
            title_only (bool): boolean flag to show only the title of the category

        Returns:
            None
        '''

        categories = set([package.category for package in self.packages])

        if title_only:
            for category in categories:
                print(category)
        else:
            for category in categories:
                package_count = sum(1 for package in self.packages if package.category == category)
                print(mmpm.color.normal_green(category), f'\n  Packages: {package_count}\n')


    def display_upgradable(self) -> None:
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

        mmpm_magicmirror_root: str = MMPMEnv.mmpm_magicmirror_root.get()

        app_label: str = f"{mmpm.color.normal_cyan('application')}"
        pkg_label: str = f"{mmpm.color.normal_cyan('package')}"

        upgrades_available: bool = False
        upgradable = self.upgradable()

        if upgradable["packages"] or upgradable["mmpm"] or upgradable["MagicMirror"]:
            upgrades_available = True

        for package in upgradable["packages"]:
            print(mmpm.color.normal_green(MagicMirrorPackage(**package).title), f'[{pkg_label}]')

        if upgradable["mmpm"]:
            print(f'{mmpm.color.normal_green("mmpm")} [{app_label}]')

        if upgradable["MagicMirror"]:
            print(f'{mmpm.color.normal_green("MagicMirror")} [{app_label}]')

        if upgrades_available:
            print('Run `mmpm upgrade` to upgrade available packages/applications')
        else:
            print(f'No upgrades available {mmpm.consts.YELLOW_X}')


    def upgradable(self) -> dict:
        '''
        Retrieves all available packages and applications from the
        mmpm-available-upgrades.json file, and ensures the contents are valid.
        If the contents are malformed, the file is reset.

        Parameters:
            None

        Returns:
            upgradable (dict): a dictionary containg the upgrades available
                                    for every MagicMirror environment encountered
        '''
        reset_file: bool = False

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, 'r', encoding="utf-8") as upgradable:
            try:
                upgrades: dict = json.load(upgradable)
            except json.JSONDecodeError:
                logger.warning(f"Encountered error when reading from {paths.MMPM_AVAILABLE_UPGRADES_FILE}. Resetting file.")
                reset_file = True

        if not reset_file:
            return upgrades

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, 'w', encoding="utf-8") as upgradable:
            upgrades = {"mmpm": False, "MagicMirror": False, "packages": [] }
            json.dump(upgrades, upgradable)

        return upgrades


    def add_mm_pkg(self, title: str = None, author: str = None, repository: str = None, description: str = None) -> str:
        '''
        Adds an external source for user to install a module from. This may be a
        private git repo, or a specific branch of a public repo. All modules added
        in this manner will be added to the 'External Packages' category.
        These sources are stored in ~/.config/mmpm/mmpm-external-packages.json

        Parameters:
            title (str): module title
            author (str): module author
            repo (str): module repo url
            description (str): module description

        Returns:
            (bool): Upon success, a True result is returned
        '''

        package = MagicMirrorPackage(category="External Packages")

        try:
            fields = [('Title', title), ('Author', author), ('Repository', repository), ('Description', description)]

            for field_name, field_value in fields:
                if field_value is None:
                    field_value = mmpm.utils.assert_valid_input(f'{field_name}: ')
                else:
                    print(f'{field_name}: {field_value}')
                setattr(package, field_name.lower(), field_value)

            print(title, author, repository, description)
        except KeyboardInterrupt:
            logger.info("User killed process with CTRL-C")
            sys.exit(127)

        package.directory = Path(f'{package.repository.split("/")[-1].replace(".git", "")}-ext-mm-pkg')

        try:
            ext_pkgs_file: PosixPath = mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE

            if ext_pkgs_file.exists() and ext_pkgs_file.stat().st_size:
                external_packages = {}

                with open(ext_pkgs_file, 'r', encoding="utf-8") as mmpm_ext_srcs:
                    external_packages = json.load(mmpm_ext_srcs)

                with open(ext_pkgs_file, 'w', encoding="utf-8") as mmpm_ext_srcs:
                    external_packages[package.category].append(package.serialize())
                    json.dump(external_packages, mmpm_ext_srcs)
            else:
                # if file didn't exist previously, or it was empty, this is the first external package that's been added
                with open(ext_pkgs_file, 'w', encoding="utf-8") as mmpm_ext_srcs:
                    json.dump({"External Packages": [package.serialize()]}, mmpm_ext_srcs)

            print(mmpm.color.normal_green(f"\nSuccessfully added {package.title} to 'External Packages'\n"))

        except IOError as error:
            logger.msg.error('Failed to save external module')
            return str(error)

        return ''


    # @TODO
    def remove_mm_pkg(self, titles: List[str] = None, assume_yes: bool = False) -> bool:
        '''
        Allows user to remove an External Pac kage from the data saved in
        ~/.config/mmpm/mmpm-external-packages.json

        Parameters:
            titles (List[str]): External source titles
            assume_yes (bool): if True, assume yes for user response, and do not display prompt

        Returns:
            success (bool): True on success, False on error
        '''

        if not os.path.exists(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE):
            logger.msg.fatal(f'{mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE} does not appear to exist')

        elif not os.stat(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE).st_size:
            logger.msg.fatal(f'{mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE} is empty')

        ext_packages: Dict[str, List[MagicMirrorPackage]] = {}
        marked_for_removal: List[MagicMirrorPackage] = []
        cancelled_removal: List[MagicMirrorPackage] = []

        with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'r', encoding="utf-8") as mmpm_ext_srcs:
            print("@FIXME")
            #ext_packages[mmpm.consts.EXTERNAL_PACKAGES] = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(json.load(mmpm_ext_srcs)[mmpm.consts.EXTERNAL_PACKAGES])

        if not ext_packages[mmpm.consts.EXTERNAL_PACKAGES]:
            logger.msg.fatal('No external packages found in database')

        for title in titles:
            for package in ext_packages[mmpm.consts.EXTERNAL_PACKAGES]:
                if package.title == title:
                    prompt: str = f'Would you like to remove {mmpm.color.normal_green(title)} ({package.repository}) from the MMPM/MagicMirror local database?'
                    if assume_yes or mmpm.utils.prompt(prompt):
                        marked_for_removal.append(package)
                    else:
                        cancelled_removal.append(package)

        if not marked_for_removal and not cancelled_removal:
            logger.msg.error('No external sources found matching provided query')
            return False

        for package in marked_for_removal:
            ext_packages[mmpm.consts.EXTERNAL_PACKAGES].remove(package)
            print(f'Removed {package.title} ({package.repository}) {mmpm.consts.GREEN_CHECK_MARK}')

        # if the error_msg was triggered, there's no need to even bother writing back to the file
        with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'w', encoding="utf-8") as mmpm_ext_srcs:
            json.dump(ext_packages, mmpm_ext_srcs, default=lambda pkg: pkg.serialize())

        return True


    def dump(self) -> None:
        '''
        Pretty prints contents of database to stdout
        Parameters:
            None
        Returns:
            None
        '''

        print(
            highlight(
                json.dumps(self.packages, indent=2, default=lambda package: package.serialize()),
                JsonLexer(),
                formatters.TerminalFormatter(),
            )
        )

    def read_available_upgrades(self) -> Dict[str, Any]:
            configuration = {}

            with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="r", encoding="utf-8") as upgrade_file:
                try:
                    configuration = json.load(upgrade_file)
                except json.JSONDecodeError as error:
                    logger.error(f"Failed to parse {paths.MMPM_AVAILABLE_UPGRADES_FILE}, resetting file: {error}")
                    configuration = {"mmpm": False, "MagicMirror": False, "packages": []}

            return configuration
