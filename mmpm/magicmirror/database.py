#!/usr/bin/env python3
import os
import json
import shutil
import datetime
import requests
import mmpm.consts
from collections import defaultdict
from typing import Dict, List
from bs4 import BeautifulSoup
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.utils import get_env
from pygments import highlight, formatters
from pygments.lexers.data import JsonLexer
from functools import lru_cache
from mmpm.logger import MMPMLogger


logger = MMPMLogger.get_logger(__name__)

class MagicMirrorDatabase:
    def __init__(self):
        self.data = None
        self.categories = None
        self.packages = None
        self.last_update: datetime.datetime = None
        self.expiration_date: datetime.datetime  = None


    def update(self):
        pass


    def details(self):
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
        num_categories: int = len(self.packages)
        num_packages: int = 0

        for category in self.packages.values():
            num_packages += len(category)

        num_packages -= 1 # skip MMPM itself in the package count

        print(mmpm.color.normal_green('Last updated:'), f'{str(self.last_update)}')
        print(mmpm.color.normal_green('Next scheduled update:'), f'{str(self.expiration_date)}')
        print(mmpm.color.normal_green('Package categories:'), f'{num_categories}')
        print(mmpm.color.normal_green('Packages available:'), f'{num_packages}')


    def retrieve_packages(self):
        '''
        Scrapes the MagicMirror 3rd Party Wiki for all packages listed by community members

        Parameters:
            None

        Returns:
            packages (Dict[str, List[MagicMirrorPackage]]): dictionary of MagicMirror 3rd party modules
        '''

        self.packages: Dict[str, List[MagicMirrorPackage]] = defaultdict(list)
        response: requests.Response = requests.Response()

        try:
            response = requests.get(mmpm.consts.MAGICMIRROR_MODULES_URL, timeout=10)
        except requests.exceptions.RequestException:
            print(mmpm.consts.RED_X)
            mmpm.utils.fatal_msg('Unable to retrieve MagicMirror modules. Is your internet connection up?')
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')
        table_soup: list = soup.find_all('table')
        category_soup = soup.find_all(attrs={'class': 'markdown-body'})
        categories_soup = category_soup[0].find_all('h3')
        del categories_soup[0] # the General Advice section

        # the last entry of the html element contents contains the actual category name
        categories: list = [category.contents[-1] for category in categories_soup]

        # the first index is a row that literally says 'Title' 'Author' 'Description'
        tr_soup: list = [table.find_all('tr')[1:] for table in table_soup]

        try:
            for index, row in enumerate(tr_soup):
                for tag in row:
                    table_data: list = tag.find_all('td')

                    if table_data[0].contents[0].contents[0] == mmpm.consts.MMPM:
                        break

                    self.packages[categories[index]].append(MagicMirrorPackage.from_raw_data(table_data))

        except Exception as error:
            mmpm.utils.fatal_msg(str(error))


    def is_expired(self) -> bool:
        for file_name in [mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE, mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE]:
            if not file_name.exists() or not bool(file_name.stat().st_size):
                return True # the file is empty

        if self.last_update is None or self.expiration_date is None:
            with open(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE) as expiration_file:
                data = json.load(expiration_file)
                self.expiration_date = datetime.datetime.fromisoformat(data["expiration"])
                self.last_update = datetime.datetime.fromisoformat(data["last-update"])

        return datetime.datetime.now() > self.expiration_date


    def load_packages(self, force_refresh: bool = False):

        '''
        Reads in modules from the hidden database file  and checks if the file is
        out of date. If so, the modules are gathered again from the MagicMirror 3rd
        Party Modules wiki.

        Parameters:
            force_refresh (bool): Boolean flag to force refresh of the database

        Returns:
            packages (Dict[str, List[MagicMirrorPackage]]): dictionary of MagicMirror 3rd party modules
        '''

        packages: dict = {}

        db_file = mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE
        db_exists: bool = db_file.exists() and bool(db_file.stat().st_size)
        ext_pkgs_file: str = mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE

        if db_exists:
            logger.info(f'Backing up database file as {mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE}.bak')

            shutil.copyfile(
                str(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE),
                f'{str(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE)}.bak'
            )

            logger.info('Back up of database complete')


        # if the database has expired, or doesn't exist, get a new one
        if force_refresh or not db_exists:
            mmpm.utils.plain_print(
                f"{mmpm.consts.GREEN_PLUS} {'Refreshing' if db_exists else 'Initializing'} MagicMirror 3rd party packages database "
            )

            self.retrieve_packages()

            if not self.packages:
                print(mmpm.consts.RED_X)
                mmpm.utils.error_msg(f'Failed to retrieve packages from {mmpm.consts.MAGICMIRROR_MODULES_URL}. Please check your internet connection.')

            # save the new database
            else:
                with open(db_file, 'w', encoding="utf-8") as db:
                    json.dump(self.packages, db, default=lambda pkg: pkg.serialize())

                with open(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE, 'w', encoding='utf-8') as expiration_file:
                    self.last_update = datetime.datetime.now().date()
                    self.expiration_date = self.last_update + datetime.timedelta(hours=12)

                    json.dump({"last-update": str(self.last_update), "expiration": str(self.expiration_date)})

                print(mmpm.consts.GREEN_CHECK_MARK)

        if not self.packages and db_exists:
            self.packages = {}

            with open(db_file, 'r', encoding="utf-8") as db:
                packages = json.load(db)

                for category in packages:
                    self.packages[category] = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(packages[category])

        if self.packages and os.path.exists(ext_pkgs_file) and bool(os.stat(ext_pkgs_file).st_size):
            self.packages.update(**self.__load_external_packages__())


    def dump(self) -> None:
        '''
        Pretty prints contents of database to stdout

        Parameters:
            None

        Returns:
            None
        '''
        contents: dict = {}

        with open(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE, 'r', encoding="utf-8") as db:
            try:
                contents.update(json.load(db))
            except json.JSONDecodeError:
                pass

        if os.stat(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE).st_size:
            with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'r', encoding="utf-8") as db:
                try:
                    contents.update(json.load(db))
                except json.JSONDecodeError:
                    logger.warning('External Packages appears to be empty, skipping during database dump')

        print(highlight(json.dumps(contents, indent=2), JsonLexer(), formatters.TerminalFormatter()))


    def __load_external_packages__(self) -> Dict[str, List[MagicMirrorPackage]]:
        '''
        Extracts the external packages from the JSON files stored in
        ~/.config/mmpm/mmpm-external-packages.json

        If no data is found, an empty dictionary is returned

        Parameters:
            None

        Returns:
            external_packages (Dict[str, List[MagicMirrorPackage]]): the list of manually added MagicMirror packages
        '''
        external_packages: List[MagicMirrorPackage] = []

        if bool(os.stat(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE).st_size):
            try:
                with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'r', encoding="utf-8") as ext_pkgs:
                    external_packages = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(json.load(ext_pkgs)[mmpm.consts.EXTERNAL_PACKAGES])
            except Exception:
                message = f'Failed to load data from {mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE}. Please examine the file, as it may be malformed and required manual corrective action.'
                mmpm.utils.warning_msg(message)
        else:
            with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, mode= 'w', encoding="utf-8") as ext_pkgs:
                json.dump({mmpm.consts.EXTERNAL_PACKAGES: external_packages}, ext_pkgs)

        return {mmpm.consts.EXTERNAL_PACKAGES: external_packages}


    def get_installed_packages(self):
        '''
        Scans the list <MMPM_MAGICMIRROR_ROOT>/modules directory, and compares
        against the known packages from the MagicMirror 3rd Party Wiki. Returns a
        dictionary of all found packages

        Parameters:
            packages (Dict[str, List[MagicMirrorPackage]]): Dictionary of MagicMirror packages

        Returns:
            installed_modules (Dict[str, List[MagicMirrorPackage]]): Dictionary of installed MagicMirror packages
        '''

        package_dirs: List[str] = mmpm.utils.get_existing_package_directories()

        if not package_dirs:
            mmpm.utils.env_variables_error_msg('Failed to find MagicMirror root directory.')
            return {}

        MAGICMIRROR_MODULES_DIR: str = os.path.join(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV), 'modules')

        os.chdir(MAGICMIRROR_MODULES_DIR)

        installed_packages: Dict[str, List[MagicMirrorPackage]] = {}
        packages_found: Dict[str, List[MagicMirrorPackage]] = {mmpm.consts.PACKAGES: []}

        for package_dir in package_dirs:
            if not os.path.isdir(package_dir) or not os.path.exists(os.path.join(os.getcwd(), package_dir, '.git')):
                continue

            try:
                os.chdir(os.path.join(MAGICMIRROR_MODULES_DIR, package_dir))

                error_code, remote_origin_url, _ = mmpm.utils.run_cmd(
                    ['git', 'config', '--get', 'remote.origin.url'],
                    progress=False
                )

                if error_code:
                    mmpm.utils.error_msg(f'Unable to communicate with git server to retrieve information about {package_dir}')
                    continue

                error_code, project_name, _ = mmpm.utils.run_cmd(
                    ['basename', remote_origin_url.strip(), '.git'],
                    progress=False
                )

                if error_code:
                    mmpm.utils.error_msg(f'Unable to determine repository origin for {project_name}')
                    continue

                packages_found[mmpm.consts.PACKAGES].append(
                    MagicMirrorPackage(
                        title=project_name.strip(),
                        repository=remote_origin_url.strip(),
                        directory=os.getcwd()
                    )
                )

            except Exception as error:
                mmpm.utils.error_msg(str(error))

            finally:
                os.chdir('..')

        for category, package_names in self.packages.items():
            installed_packages.setdefault(category, [])

            for package in package_names:
                for package_found in packages_found[mmpm.consts.PACKAGES]:
                    if package.repository == package_found.repository:
                        package.directory = package_found.directory
                        installed_packages[category].append(package)

        return installed_packages

    def display_packages(self, title_only: bool = False, include_path: bool = False, exclude_local: bool = False) -> None:
        '''
        Depending on the user flags passed in from the command line, either all
        existing packages may be displayed, or the names of all categories of
        packages may be displayed.

        Parameters:
            packages (Dict[str, List[MagicMirrorPackage]]): dictionary of MagicMirror 3rd party packages
            title_only (bool): boolean flag to show only the title of the given packages
            include_path (bool): boolean flag to show the installation path of the given packages. Used only when displaying installed packages
            exclude_local (bool): boolean flag to exclude the locally installed packages

        Returns:
            None
        '''
        format_description = lambda desc: desc[:MAX_LENGTH] + '...' if len(desc) > MAX_LENGTH else desc
        MAX_LENGTH: int = 120

        if title_only:
            _print_ = lambda package: print(package.title)

        elif include_path:
            _print_ = lambda package: print(
                mmpm.color.normal_green(f'{package.title}'),
                (f'\n  Directory: {package.directory}'),
                (f"\n  {format_description(package.description)}\n")
            )

        else:
            _print_ = lambda package: print(
                mmpm.color.normal_green(f'{package.title}'),
                (f"\n  {format_description(package.description)}\n")
            )

        pkgs = self.packages if not exclude_local else mmpm.utils.get_difference_of_packages(self.packages, self.get_installed_packages())

        for _, packages in pkgs.items():
            for _, package in enumerate(packages):
                _print_(package)


    def display_categories(self, title_only: bool = False) -> None:
        '''
        Prints module category names and the total number of modules in one of two
        formats. The default is similar to the Debian apt package manager, and the
        prettified table alternative

        Parameters:
            packages (Dict[str, List[MagicMirrorPackage]]): list of dictionaries containing category names and module count
            title_only (bool): boolean flag to show only the title of the category

        Returns:
            None
        '''

        categories: List[dict] = [
            {
                mmpm.consts.CATEGORY: key,
                mmpm.consts.PACKAGES: len(self.packages[key])
            } for key in self.packages
        ]

        if title_only:
            for category in categories:
                print(category[mmpm.consts.CATEGORY])
            return

        for category in categories:
            print(
                mmpm.color.normal_green(category[mmpm.consts.CATEGORY]),
                f'\n  Packages: {category[mmpm.consts.PACKAGES]}\n'
            )


    def display_available_upgrades(self) -> None:
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
        MMPM_MAGICMIRROR_ROOT: str = os.path.normpath(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV))

        cyan_application: str = f"{mmpm.color.normal_cyan('application')}"
        cyan_package: str = f"{mmpm.color.normal_cyan('package')}"

        upgrades_available: bool = False
        upgrades = self.get_available_upgrades()

        if upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES]:
            for package in upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES]:
                print(mmpm.color.normal_green(package.title), f'[{cyan_package}]')
                upgrades_available = True

        if upgrades[mmpm.consts.MMPM]:
            upgrades_available = True
            print(f'{mmpm.color.normal_green(mmpm.consts.MMPM)} [{cyan_application}]')

        if upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.MAGICMIRROR]:
            upgrades_available = True
            print(f'{mmpm.color.normal_green(mmpm.consts.MAGICMIRROR)} [{cyan_application}]')

        if upgrades_available:
            print('Run `mmpm upgrade` to upgrade available packages/applications')
        else:
            print(f'No upgrades available {mmpm.consts.YELLOW_X}')


    def get_available_upgrades(self) -> dict:
        '''
        Parses the mmpm-available-upgrades.json file, and ensures the contents are
        valid. If the contents are malformed, the file is reset.

        Parameters:
            None

        Returns:
            available_upgrades (dict): a dictionary containg the upgrades available
                                    for every MagicMirror environment encountered

        '''
        MMPM_MAGICMIRROR_ROOT: str = os.path.normpath(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV))

        reset_file: bool = False
        add_key: bool = False

        with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'r', encoding="utf-8") as available_upgrades:
            try:
                upgrades: dict = json.load(available_upgrades)
                upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES] = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(
                    upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES]
                )
            except json.JSONDecodeError:
                reset_file = True
            except KeyError:
                add_key = True

        if reset_file:
            with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w', encoding="utf-8") as available_upgrades:
                upgrades = {mmpm.consts.MMPM: False, MMPM_MAGICMIRROR_ROOT: {mmpm.consts.PACKAGES: [], mmpm.consts.MAGICMIRROR: False}}
                json.dump(upgrades, available_upgrades)

        elif add_key:
            with open(mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE, 'w', encoding="utf-8") as available_upgrades:
                upgrades[MMPM_MAGICMIRROR_ROOT] = {mmpm.consts.PACKAGES: [], mmpm.consts.MAGICMIRROR: False}
                json.dump(upgrades, available_upgrades)

        return upgrades


    def add_external_package(self, title: str = None, author: str = None, repo: str = None, description: str = None) -> str:
        '''
        Adds an external source for user to install a module from. This may be a
        private git repo, or a specific branch of a public repo. All modules added
        in this manner will be added to the 'External Module Sources' category.
        These sources are stored in ~/.config/mmpm/mmpm-external-packages.json

        Parameters:
            title (str): External source title
            author (str): External source author
            repo (str): External source repo url
            description (str): External source description

        Returns:
            (bool): Upon success, a True result is returned
        '''
        try:
            if not title:
                title = mmpm.utils.assert_valid_input('Title: ')
            else:
                print(f'Title: {title}')

            if not author:
                author = mmpm.utils.assert_valid_input('Author: ')
            else:
                print(f'Author: {author}')

            if not repo:
                repo = mmpm.utils.assert_valid_input('Repository: ')
            else:
                print(f'Repository: {repo}')

            if not description:
                description = mmpm.utils.assert_valid_input('Description: ')
            else:
                print(f'Description: {description}')

        except KeyboardInterrupt:
            mmpm.utils.keyboard_interrupt_log()

        external_package = MagicMirrorPackage(title=title, repository=repo, author=author, description=description)

        try:
            if os.path.exists(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE) and os.stat(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE).st_size:
                config: dict = {}

                with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'r', encoding="utf-8") as mmpm_ext_srcs:
                    config[mmpm.consts.EXTERNAL_PACKAGES] = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(json.load(mmpm_ext_srcs)[mmpm.consts.EXTERNAL_PACKAGES])

                with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'w', encoding="utf-8") as mmpm_ext_srcs:
                    config[mmpm.consts.EXTERNAL_PACKAGES].append(external_package)
                    json.dump(config, mmpm_ext_srcs, default=lambda pkg: pkg.serialize())
            else:
                # if file didn't exist previously, or it was empty, this is the first external package that's been added
                with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'w', encoding="utf-8") as mmpm_ext_srcs:
                    json.dump({mmpm.consts.EXTERNAL_PACKAGES: [external_package]}, mmpm_ext_srcs, default=lambda pkg: pkg.serialize())

            print(mmpm.color.normal_green(f"\nSuccessfully added {title} to '{mmpm.consts.EXTERNAL_PACKAGES}'\n"))

        except IOError as error:
            mmpm.utils.error_msg('Failed to save external module')
            return str(error)

        return ''


    def remove_external_package_source(self, titles: List[str] = None, assume_yes: bool = False) -> bool:
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
            mmpm.utils.fatal_msg(f'{mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE} does not appear to exist')

        elif not os.stat(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE).st_size:
            mmpm.utils.fatal_msg(f'{mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE} is empty')

        ext_packages: Dict[str, List[MagicMirrorPackage]] = {}
        marked_for_removal: List[MagicMirrorPackage] = []
        cancelled_removal: List[MagicMirrorPackage] = []

        with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'r', encoding="utf-8") as mmpm_ext_srcs:
            ext_packages[mmpm.consts.EXTERNAL_PACKAGES] = mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(json.load(mmpm_ext_srcs)[mmpm.consts.EXTERNAL_PACKAGES])

        if not ext_packages[mmpm.consts.EXTERNAL_PACKAGES]:
            mmpm.utils.fatal_msg('No external packages found in database')

        for title in titles:
            for package in ext_packages[mmpm.consts.EXTERNAL_PACKAGES]:
                if package.title == title:
                    prompt: str = f'Would you like to remove {mmpm.color.normal_green(title)} ({package.repository}) from the MMPM/MagicMirror local database?'
                    if mmpm.utils.prompt_user(prompt, assume_yes=assume_yes):
                        marked_for_removal.append(package)
                    else:
                        cancelled_removal.append(package)

        if not marked_for_removal and not cancelled_removal:
            mmpm.utils.error_msg('No external sources found matching provided query')
            return False

        for package in marked_for_removal:
            ext_packages[mmpm.consts.EXTERNAL_PACKAGES].remove(package)
            print(f'Removed {package.title} ({package.repository}) {mmpm.consts.GREEN_CHECK_MARK}')

        # if the error_msg was triggered, there's no need to even bother writing back to the file
        with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'w', encoding="utf-8") as mmpm_ext_srcs:
            json.dump(ext_packages, mmpm_ext_srcs, default=lambda pkg: pkg.serialize())

        return True
