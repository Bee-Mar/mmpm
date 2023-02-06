#!/usr/bin/env python3
import os
import json
import shutil
import datetime
import requests
import mmpm.consts
import mmpm.color
from re import findall
from collections import defaultdict
from typing import Dict, List
from bs4 import BeautifulSoup
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.env import MMPMEnv
from mmpm.constants import paths
from pygments import highlight, formatters
from pygments.lexers.data import JsonLexer
from functools import lru_cache
from mmpm.logger import MMPMLogger
from pathlib import Path, PosixPath
from pygments import highlight, formatters
from pygments.lexers.data import JsonLexer



logger = MMPMLogger.get_logger(__name__)
logger.setLevel(MMPMEnv.mmpm_log_level.get())


class MagicMirrorDatabase:
    packages: List[MagicMirrorPackage] = None
    last_update: datetime.datetime = None
    expiration_date: datetime.datetime = None
    categories: List[str] = None

    @classmethod
    def __update_mmpm__(cls, automated=False) -> bool:
        '''
        Scrapes the main file of MMPM off the github repo, and compares the current
        version, versus the one available in the master branch. If there is a newer
        version, the user is prompted for an upgrade.

        Parameters:
            automated (bool): if True, an extra notification is printed to the screen for the user to see

        Returns:
            bool: True on success, False on failure
        '''

        cyan_application: str = f"{mmpm.color.normal_cyan('application')}"
        logger.info(f'Checking for newer version of MMPM. Current version: {mmpm.mmpm.__version__}')

        if automated:
            message: str = f"Checking {mmpm.color.normal_green('MMPM')} [{cyan_application}] ({mmpm.color.normal_magenta('automated')}) for updates"
        else:
            message = f"Checking {mmpm.color.normal_green('MMPM')} [{cyan_application}] for updates"

        mmpm.utils.plain_print(message)

        try:
            # just to keep the console output the same as all other update commands
            error_code, contents, _ = mmpm.utils.run_cmd(['curl', mmpm.consts.MMPM_FILE_URL])
        except KeyboardInterrupt:
            mmpm.utils.keyboard_interrupt_log()

        if error_code:
            logger.msg.fatal_msg('Failed to retrieve MMPM version number')

        version_number: float = float(findall(r"\d+\.\d+", findall(r"__version__ = \d+\.\d+", contents)[0])[0])
        print(mmpm.consts.GREEN_CHECK_MARK)

        if not version_number:
            logger.msg.fatal('No version number found on MMPM repository')

        can_upgrade: bool = version_number > mmpm.mmpm.__version__

        if can_upgrade:
            logger.msg.info(f'Found newer version of MMPM: {version_number}')
        else:
            logger.msg.info(f'No newer version of MMPM found > {version_number} available. The current version is the latest')

        return can_upgrade

    @classmethod
    def __update_magicmirror__(cls) -> bool:
        '''
        Checks for updates available to the MagicMirror repository. Alerts user if an upgrade is available.

        Parameters:
            None

        Returns:
            bool: True upon success, False upon failure
        '''
        magicmirror_root: PosixPath = Path(MMPMEnv.mmpm_root.get())

        if not magicmirror_root.exists():
            logger.msg.error('MagicMirror application directory not found. Please ensure the MMPM environment variables are set properly in your shell configuration')
            return False

        is_git: bool = True

        if not (magicmirror_root / '.git').exists():
            logger.msg.warning('The MagicMirror root is not a git repo. If running MagicMirror as a Docker container, updates cannot be performed via mmpm.')
            is_git = False

        if is_git:
            os.chdir(magicmirror_root)
            cyan_application: str = f"{mmpm.color.normal_cyan('application')}"
            mmpm.utils.plain_print(f"Checking {mmpm.color.normal_green('MagicMirror')} [{cyan_application}] for updates")

            try:
                # stdout and stderr are flipped for git command output, because that totally makes sense
                # except now stdout doesn't even contain error messages...thanks git
                error_code, _, stdout = mmpm.utils.run_cmd(['git', 'fetch', '--dry-run'])
            except KeyboardInterrupt:
                print(mmpm.consts.RED_X)
                mmpm.utils.keyboard_interrupt_log()

            print(mmpm.consts.GREEN_CHECK_MARK)

            if error_code:
                mmpm.utils.error_msg('Unable to communicate with git server')

            if stdout:
                return True

        return False

    @classmethod
    def update(cls, automated: bool = False) -> int:

        packages: List[MagicMirrorPackage] = []

        if packages:
            can_upgrade_mmpm = MagicMirrorDatabase.__update_mmpm__(automated)
            can_upgrade_magicmirror = MagicMirrorDatabase.__update_magicmirror__()

            cyan_package: str = f"{mmpm.color.normal_cyan('package')}"


            for package in MagicMirrorDatabase.packages:
                if package.is_installed:
                    mmpm.utils.plain_print(f'Checking {mmpm.color.normal_green(package.title)} [{cyan_package}] for updates') # type: ignore
                    package.update()
                    print(mmpm.consts.GREEN_CHECK_MARK)

                if package.is_upgradable:
                    upgradable.append(package)

        with open(paths.MMPM_upgradable_FILE, "w", encoding="utf-8") as upgrade_file:
            json.dump(
                {
                    "mmpm": can_upgrade_mmpm,
                    "MagicMirror": can_upgrade_magicmirror,
                    "packages": [package.serialize() for package in packages],
                },
                upgrade_file
            )

        return int(can_upgrade_mmpm) + int(can_upgrade_magicmirror) + len(packages)


    @classmethod
    def details(cls):
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
        print(mmpm.color.normal_green('Last updated:'), f'{str(MagicMirrorDatabase.last_update.replace(microsecond=0))}')
        print(mmpm.color.normal_green('Next scheduled update:'), f'{str(MagicMirrorDatabase.expiration_date.replace(microsecond=0))}')
        print(mmpm.color.normal_green('Categories:'), f'{len(MagicMirrorDatabase.categories)}')
        print(mmpm.color.normal_green('Packages:'), f'{len(MagicMirrorDatabase.packages) - 1}')

    @classmethod
    def download(cls):
        '''
        Scrapes the MagicMirror 3rd Party Wiki for all packages listed by community members

        Parameters:
            None

        Returns:
            packages (Dict[str, List[MagicMirrorPackage]]): dictionary of MagicMirror 3rd party modules
        '''

        MagicMirrorDatabase.packages: List[MagicMirrorPackage] = []
        response: requests.Response = requests.Response()

        try:
            response = requests.get(mmpm.consts.MAGICMIRROR_MODULES_URL, timeout=10)
        except requests.exceptions.RequestException:
            print(mmpm.consts.RED_X)
            mmpm.utils.fatal_msg('Unable to retrieve MagicMirror modules. Is your internet connection up?')
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')
        table_soup = soup.find_all('table')
        categories_soup = soup.find_all(attrs={'class': 'markdown-body'})[0].find_all('h3')

        del categories_soup[0] # the General Advice section

        # the last entry of the html element contents contains the actual category name
        categories: list = [category.contents[-1] for category in categories_soup]

        # the first index is a row that literally says 'Title' 'Author' 'Description'
        tr_soup: list = [table.find_all('tr')[1:] for table in table_soup]

        try:
            for index, row in enumerate(tr_soup):
                for entry in row:
                    table_data: list = entry.find_all('td')

                    if table_data[0].contents[0].contents[0] == mmpm.consts.MMPM:
                        continue

                    pkg = MagicMirrorPackage.from_raw_data(table_data, category=categories[index])
                    MagicMirrorDatabase.packages.append(pkg)

        except Exception as error:
            mmpm.utils.fatal_msg(str(error))

    @classmethod
    def expired(cls) -> bool:
        for file_name in [mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE, mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE]:
            if not file_name.exists() or not bool(file_name.stat().st_size):
                return True # the file is empty

        if MagicMirrorDatabase.last_update is None or MagicMirrorDatabase.expiration_date is None:
            with open(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE) as expiration_file:
                data = json.load(expiration_file)
                MagicMirrorDatabase.expiration_date = datetime.datetime.fromisoformat(data["expiration"])
                MagicMirrorDatabase.last_update = datetime.datetime.fromisoformat(data["last-update"])

        return datetime.datetime.now() > MagicMirrorDatabase.expiration_date

    @classmethod
    def search(cls, query: str, case_sensitive: bool = False, by_title_only: bool = False, exclude_installed: bool = False) -> List[MagicMirrorPackage]:
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
            search_results (Dict[str, List[MagicMirrorPackage]]): the dictionary of packages, grouped by category that are search matches
        '''
        # if the query matches one of the category names exactly, return everything in that category
        if query in MagicMirrorDatabase.categories:
            return [package for package in MagicMirrorDatabase.packages if package.category == query]
        elif by_title_only:
            match = lambda query, pkg: query == pkg.title
        elif case_sensitive:
            match = lambda query, pkg: query in pkg.description or query in pkg.title or query in pkg.author
        else:
            query = query.lower()
            match = lambda query, pkg: query in pkg.description.lower() or query in pkg.title.lower() or query in pkg.author.lower()

        return [package for package in MagicMirrorDatabase.packages if match(query, package)]

    @classmethod
    def load(cls, refresh: bool = False):
        '''
        Reads in modules from the hidden database file  and checks if the file is
        out of date. If so, the modules are gathered again from the MagicMirror 3rd
        Party Modules wiki.

        Parameters:
            refresh (bool): Boolean flag to force refresh of the database

        Returns:
            packages (Dict[str, List[MagicMirrorPackage]]): dictionary of MagicMirror 3rd party modules
        '''

        packages: List[MagicMirrorPackage] = []

        db_file: PosixPath = mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE
        db_exists: bool = db_file.exists() and bool(db_file.stat().st_size)
        ext_pkgs_file: str = mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE

        if db_exists:
            shutil.copyfile(
                str(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE),
                f'{str(mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE)}.bak'
            )

            logger.info(f'Backed up database file as {paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE}.bak')


        # if the database has expired, or doesn't exist, get a new one
        if refresh or not db_exists:
            mmpm.utils.plain_print(
                f"{mmpm.consts.GREEN_PLUS} {'Refreshing' if db_exists else 'Initializing'} MagicMirror 3rd party packages database "
            )

            MagicMirrorDatabase.download()
            MagicMirrorDatabase.__scrape_installed_packages__()

            if not MagicMirrorDatabase.packages:
                print(mmpm.consts.RED_X)
                mmpm.utils.error_msg(f'Failed to retrieve packages from {mmpm.consts.MAGICMIRROR_MODULES_URL}. Please check your internet connection.')

            # save the new database
            else:
                with open(db_file, 'w', encoding="utf-8") as db:
                    json.dump(MagicMirrorDatabase.packages, db, default=lambda package: package.serialize())

                with open(paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE, 'w', encoding='utf-8') as expiration_file:
                    MagicMirrorDatabase.last_update = datetime.datetime.now()
                    MagicMirrorDatabase.expiration_date = MagicMirrorDatabase.last_update + datetime.timedelta(hours=12)

                    json.dump(
                        {
                            "last-update": str(MagicMirrorDatabase.last_update),
                            "expiration": str(MagicMirrorDatabase.expiration_date)
                        },
                        expiration_file,
                    )

                print(mmpm.consts.GREEN_CHECK_MARK)

        if not MagicMirrorDatabase.packages and db_exists:
            MagicMirrorDatabase.packages = []

            with open(db_file, 'r', encoding="utf-8") as db:
                packages = json.load(db)

                for package in packages:
                    MagicMirrorDatabase.packages.append(MagicMirrorPackage(**package))

        MagicMirrorDatabase.categories = set([package.category for package in MagicMirrorDatabase.packages])

        # TODO: FIXME
        #if MagicMirrorDatabase.packages and os.path.exists(ext_pkgs_file) and bool(os.stat(ext_pkgs_file).st_size):
        #    MagicMirrorDatabase.packages.update(**MagicMirrorDatabase.__load_external_packages__())


    @classmethod
    def __load_external_packages__(cls) -> Dict[str, List[MagicMirrorPackage]]:
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


    @classmethod
    def __scrape_installed_packages__(cls) -> None:
        '''
        Scans the list <MMPM_MAGICMIRROR_ROOT>/modules directory, and compares
        against the known packages from the MagicMirror 3rd Party Wiki. Returns a
        dictionary of all found packages

        Parameters:
            packages (Dict[str, List[MagicMirrorPackage]]): Dictionary of MagicMirror packages

        Returns:
            installed_modules (Dict[str, List[MagicMirrorPackage]]): Dictionary of installed MagicMirror packages
        '''

        modules_dir: PosixPath = Path(MMPMEnv.mmpm_root.get()) / 'modules'
        package_directories: List[PosixPath] = [directory for directory in modules_dir.iterdir()]

        for known in MagicMirrorDatabase.packages:
            if known.author == "Bee-Mar":
                print(known)

        if not package_directories:
            mmpm.utils.env_variables_error_msg('Failed to find MagicMirror root directory.')
            return []

        os.chdir(modules_dir)

        packages_found: List[MagicMirrorPackage] = []

        for package_dir in package_directories:
            if not package_dir.is_dir() or not Path(package_dir / ".git").exists():
                continue

            try:
                os.chdir(package_dir)

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

                packages_found.append(
                    MagicMirrorPackage(title=project_name.strip(), repository=remote_origin_url.strip(), directory=str(package_dir))
                )

            except Exception as error:
                mmpm.utils.error_msg(str(error))

            finally:
                os.chdir(modules_dir)

        for known in MagicMirrorDatabase.packages:
            for found in packages_found:
                if known == found:
                    known.directory = found.directory
                    known.is_installed = True
                    packages_found.remove(found)
                    break


    @classmethod
    def display_categories(cls, title_only: bool = False) -> None:
        '''
        Prints module category names and the total number of modules in one of two
        formats. The default is similar to the Debian apt package manager.

        Parameters:
            title_only (bool): boolean flag to show only the title of the category

        Returns:
            None
        '''
        categories = set([package.category for package in MagicMirrorDatabase.packages])

        if title_only:
            for category in categories:
                print(category)

        else:
            groups: dict = {
                category: len([package for package in MagicMirrorDatabase.packages if package.category == category])
                for category in categories
            }


            for category, package_count in groups.items():
                print(mmpm.color.normal_green(category), f'\n  Packages: {package_count}\n')


    @classmethod
    def display_upgradable(cls) -> None:
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

        mmpm_magicmirror_root: str = MMPMEnv.mmpm_root.get()

        cyan_application: str = f"{mmpm.color.normal_cyan('application')}"
        cyan_package: str = f"{mmpm.color.normal_cyan('package')}"

        upgrades_available: bool = False
        upgradable = MagicMirrorDatabase.upgradable()

        if upgradable["packages"] or upgradable["mmpm"] or upgradable["MagicMirror"]:
            upgrades_available = True

        for package in upgradable["packages"]:
            print(mmpm.color.normal_green(package.title), f'[{cyan_package}]')

        if upgradable["mmpm"]:
            print(f'{mmpm.color.normal_green(mmpm.consts.MMPM)} [{cyan_application}]')

        if upgradable["MagicMirror"]:
            print(f'{mmpm.color.normal_green(mmpm.consts.MAGICMIRROR)} [{cyan_application}]')

        if upgrades_available:
            print('Run `mmpm upgrade` to upgrade available packages/applications')
        else:
            print(f'No upgrades available {mmpm.consts.YELLOW_X}')

    @classmethod
    def upgradable(cls) -> dict:
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

        with open(paths.MMPM_upgradable_FILE, 'r', encoding="utf-8") as upgradable:
            try:
                upgrades: dict = json.load(upgradable)
            except json.JSONDecodeError:
                logger.warning(f"Encountered error when reading from {paths.MMPM_upgradable_FILE}. Resetting file.")
                reset_file = True

        if reset_file:
            with open(paths.MMPM_upgradable_FILE, 'w', encoding="utf-8") as upgradable:
                upgrades = {"mmpm": False, "MagicMirror": False, "packages": [] }
                json.dump(upgrades, upgradable)

        return upgrades

    @classmethod
    def add_external_package(cls, title: str = None, author: str = None, repo: str = None, description: str = None) -> str:
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

    @classmethod
    def remove_external_package_source(cls, titles: List[str] = None, assume_yes: bool = False) -> bool:
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


    @classmethod
    def dump(cls) -> None:
        '''
        Pretty prints contents of database to stdout
        Parameters:
            None
        Returns:
            None
        '''

        print(
            highlight(
                json.dumps(MagicMirrorDatabase.packages, indent=2, default=lambda package: package.serialize()),
                JsonLexer(),
                formatters.TerminalFormatter()
            )
        )


    @classmethod
    def install(cls, packages: List[MagicMirrorPackage] = None, mmpm_module: bool = False, magicmirror: bool = False, assume_yes: bool = False):
        if packages:
            for package in packages:
                package.install()

        elif magicmirror:
            pass

        elif mmpm_module:
            pass

