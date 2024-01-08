#!/usr/bin/env python3
import datetime
import json
import os
from pathlib import Path, PosixPath
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

from mmpm.constants import color, paths, urls
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.singleton import Singleton
from mmpm.utils import run_cmd

logger = MMPMLogFactory.get_logger(__name__)


class MagicMirrorDatabase(Singleton):
    """
    Class for managing the MagicMirror package database. It is responsible for retrieving, updating,
    and managing the list of available MagicMirror modules and custom packages.
    """

    def __init__(self):
        self.env = MMPMEnv()
        self.packages: List[MagicMirrorPackage] = None
        self.last_update: datetime.datetime = None
        self.expiration_date: datetime.datetime = None
        self.categories: List[str] = None

    def __download_packages__(self) -> List[MagicMirrorPackage]:
        """
        Scrapes the MagicMirror 3rd Party Wiki for all packages listed by community members.

        Parameters:
            None

        Returns:
            packages: List[MagicMirrorPackage] A list of MagicMirrorPackage objects extracted from the 3rd party wiki.
        """

        packages: List[MagicMirrorPackage] = []

        try:
            response = requests.get(urls.MAGICMIRROR_MODULES_URL, timeout=10)
        except requests.exceptions.RequestException:
            logger.fatal("Unable to retrieve MagicMirror modules.")

        soup = BeautifulSoup(response.text, "html.parser")
        table_soup = soup.find_all("table")
        categories_soup = soup.find_all(attrs={"class": "markdown-body"})[0].find_all("h3")

        self.categories = []

        for category in categories_soup[2:]:
            if hasattr(category, "contents"):
                if hasattr(category.contents, "contents"):
                    self.categories.append(category.contents[-1].contents[0])
                else:
                    self.categories.append(category.contents[-1])

        # the first index is a row that literally says 'Title' 'Author' 'Description'
        tr_soup: list = [table.find_all("tr")[1:] for table in table_soup]

        for index, row in enumerate(tr_soup):
            for entry in row:
                try:
                    table_data: list = entry.find_all("td")

                    if not table_data or not table_data[0].text or table_data[0].text == "mmpm":
                        continue

                    pkg = MagicMirrorPackage.from_raw_data(table_data, category=self.categories[index])
                    packages.append(pkg)

                except Exception as error:  # broad exception isn't best, but there's a lot that can happen here
                    logger.error(
                        "There may have been a breaking change in the layout of the MagicMirror 3rd Party module wiki page. Please create an issue on the MMPM's GitHub repository."
                    )
                    logger.error(f"{error}")
                    continue

        return packages

    def __discover_installed_packages__(self) -> List[MagicMirrorPackage]:
        """
        Discovers installed MagicMirror packages by scanning the modules directory.

        Parameters:
            None

        Returns:
            installed_modules (List[MagicMirrorPackage]): Dictionary of installed MagicMirror packages
        """

        modules_dir: PosixPath = self.env.MMPM_MAGICMIRROR_ROOT.get() / "modules"

        if not modules_dir.exists():
            logger.warning(f"{self.env.MMPM_MAGICMIRROR_ROOT.name}='{modules_dir}' does not exist")
            return []

        package_directories: List[PosixPath] = [
            directory for directory in modules_dir.iterdir() if directory.is_dir() and (directory / ".git").exists()
        ]

        if not package_directories:
            logger.debug(f"No packages found in {modules_dir}")
            return []

        packages_found: List[MagicMirrorPackage] = []

        for package_dir in package_directories:
            os.chdir(package_dir)
            error_code, remote_origin_url, _ = run_cmd(["git", "config", "--get", "remote.origin.url"], progress=False)

            if error_code:
                logger.error(f"Unable to communicate with git server to retrieve information about {package_dir}")
                continue

            error_code, project_name, _ = run_cmd(["basename", remote_origin_url.strip(), ".git"], progress=False)

            if error_code:
                logger.error(f"Unable to determine repository origin for {project_name}")
                continue

            packages_found.append(MagicMirrorPackage(repository=remote_origin_url.strip(), directory=package_dir.name))

        return packages_found

    def update(self, can_upgrade_mmpm: bool = False, can_upgrade_magicmirror: bool = False) -> int:
        """
        Updates the list of upgradable packages and writes them to the available upgrades file.

        Parameters:
            can_upgrade_mmpm (bool): Indicates if MMPM can be upgraded.
            can_upgrade_magicmirror (bool): Indicates if MagicMirror can be upgraded.

        Returns:
            int: The count of upgradable items, including MMPM, MagicMirror, and packages.
        """

        upgradable: List[MagicMirrorPackage] = []

        for package in filter(lambda pkg: pkg.is_installed, self.packages):
            print(f"Retrieving: {package.repository} [{color.n_cyan(package.title)}]")
            package.update()

            if package.is_upgradable:
                upgradable.append(package)

        configuration = self.upgradable()

        configuration["MagicMirror"] = can_upgrade_magicmirror
        configuration["mmpm"] = can_upgrade_mmpm
        configuration["packages"] = [package.serialize() for package in upgradable]

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="w", encoding="utf-8") as upgrade_file:
            json.dump(configuration, upgrade_file)

        return int(can_upgrade_mmpm) + int(can_upgrade_magicmirror) + len(upgradable)

    def info(self) -> Dict[str, Any]:
        """
        Gathers information about the database including the last update time, number of categories,
        and total number of packages.

        Returns:
            Dict[str, Any]: A dictionary containing database information.
        """

        return {
            "last_update": str(self.last_update),
            "categories": len(self.categories),
            "packages": len(self.packages),
        }

    def is_initialized(self) -> bool:
        """
        Checks if the MagicMirror database has been initialized with packages.

        Returns:
            bool: True if initialized, False otherwise.
        """

        return self.packages is not None and bool(len(self.packages) > 0)

    def search(self, query: str, case_sensitive: bool = False, title_only: bool = False) -> List[MagicMirrorPackage]:
        """
        Searches the MagicMirror packages based on a query, with options for case sensitivity
        and title-only search.

        Parameters:
            query (str): The search query.
            case_sensitive (bool): Whether the search is case sensitive.
            title_only (bool): Whether to search only within titles.

        Returns:
            List[MagicMirrorPackage]: A list of MagicMirrorPackage objects matching the search criteria.
        """

        query = query.strip()

        if title_only:
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

    def load(self, update: bool = False) -> bool:
        """
        Loads the MagicMirror packages from the database. Optionally forces an update
        of the database from the 3rd party wiki.

        Parameters:
            update (bool): Flag to force database update.

        Returns:
            bool: True if successful, False otherwise.
        """
        self.packages = []  # this is really related to the API, needing to clear the list out

        db_file = paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE
        db_exists = db_file.exists() and bool(db_file.stat().st_size)
        db_last_update = paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE

        should_update = update or not db_exists or not db_last_update.exists() or not db_last_update.stat().st_size

        if should_update:
            print(f"Retrieving: {urls.MAGICMIRROR_MODULES_URL} [{color.n_cyan('3rd Party Modules')}]")
            self.packages = self.__download_packages__()

            if self.packages:
                with open(db_file, "w", encoding="utf-8") as db:
                    json.dump(self.packages, db, default=lambda package: package.serialize())

                with open(db_last_update, "w", encoding="utf-8") as last_update_file:
                    self.last_update = datetime.datetime.now()
                    json.dump(
                        {"last_update": str(self.last_update.replace(microsecond=0))},
                        last_update_file,
                    )
            else:
                logger.error(f"Failed to retrieve packages from {urls.MAGICMIRROR_MODULES_URL}. Please check your internet connection.")

        else:
            with open(db_last_update, mode="r", encoding="utf-8") as db_last_update_file:
                self.last_update = json.load(db_last_update_file)["last_update"]

        if not self.packages and db_exists:
            self.packages = []

            with open(db_file, mode="r", encoding="utf-8") as db:
                packages = json.load(db)
                self.packages = [MagicMirrorPackage(**package) for package in packages]

        self.packages.extend(self.custom_packages())

        self.categories = list({package.category for package in self.packages})
        discovered_packages: List[MagicMirrorPackage] = self.__discover_installed_packages__()

        if discovered_packages:
            for package in self.packages:  # type: ignore
                if package in discovered_packages:  # (mypy thinks 'package' is a Dict[str, str])
                    package.is_installed = True  # type: ignore

        return bool(len(self.packages))

    def custom_packages(self) -> List[MagicMirrorPackage]:
        """
        Retrieves custom MagicMirror packages added by the user.

        Returns:
            List[MagicMirrorPackage]: A list of custom MagicMirrorPackage objects.
        """

        data: List[Dict[str, str]] = []
        packages: List[MagicMirrorPackage] = []
        db_custom_pkgs_file = paths.MMPM_CUSTOM_PACKAGES_FILE

        if not db_custom_pkgs_file.stat().st_size == 0:
            with open(db_custom_pkgs_file, mode="r+", encoding="utf-8") as custom_pkgs:
                try:
                    data = json.load(custom_pkgs)
                except json.decoder.JSONDecodeError:
                    logger.error(f"{db_custom_pkgs_file} has an invalid layout. Recreating file.")
                    json.dump(data, custom_pkgs)
                    data = []

        for package in data:
            try:
                packages.append(MagicMirrorPackage(**package))  # type: ignore
            except Exception as error:
                logger.debug(f"Unable to parse custom package: {error}")

        return packages

    def upgradable(self) -> Dict[str, Any]:
        """
        Checks for upgradable MagicMirror packages and applications.

        Returns:
            Dict[str, Any]: A dictionary containing information about upgradable items.
        """
        reset_file: bool = False
        upgrades_file = paths.MMPM_AVAILABLE_UPGRADES_FILE

        with open(upgrades_file, "r", encoding="utf-8") as upgradable:
            try:
                upgrades: dict = json.load(upgradable)
            except json.JSONDecodeError:
                logger.warning(f"Encountered error when reading from {upgrades_file}. Resetting file.")
                reset_file = True

        if not reset_file:
            return upgrades

        with open(upgrades_file, "w", encoding="utf-8") as upgradable:
            upgrades = {"mmpm": False, "MagicMirror": False, "packages": []}
            json.dump(upgrades, upgradable)

        return upgrades

    def add_mm_pkg(self, title: str, author: str, repository: str, description: str = None) -> bool:
        """
        Adds a custom MagicMirror package to the user's configuration.

        Parameters:
            title (str): The title of the package.
            author (str): The author of the package.
            repository (str): The repository URL of the package.
            description (str, optional): A description of the package.

        Returns:
            bool: True on successful addition, False otherwise.
        """

        package = MagicMirrorPackage(
            title=title,
            author=author,
            repository=repository,
            description=description,
            category="Custom Packages",
        )

        package.directory = Path(package.repository.split("/")[-1].replace(".git", ""))

        try:
            ext_pkgs_file = paths.MMPM_CUSTOM_PACKAGES_FILE

            if ext_pkgs_file.exists() and ext_pkgs_file.stat().st_size:
                custom_packages = []

                with open(ext_pkgs_file, "r", encoding="utf-8") as mm_ext_pkgs:
                    custom_packages = json.load(mm_ext_pkgs)

                existing_packages = [pkg.get("title").lower() for pkg in custom_packages]

                if package.title.lower() in existing_packages:
                    logger.error(f"A package with named {package.title} is already registered as an Custom Package")
                    return False

                with open(ext_pkgs_file, "w", encoding="utf-8") as mm_ext_pkgs:
                    custom_packages.append(package.serialize())
                    json.dump(custom_packages, mm_ext_pkgs)
            else:
                # if file didn't exist previously, or it was empty, this is the first custom package that's been added
                with open(ext_pkgs_file, "w", encoding="utf-8") as mm_ext_pkgs:
                    json.dump([package.serialize()], mm_ext_pkgs)

            print(color.n_green(f"\nSuccessfully added {package.title} to 'Custom Packages'\n"))

        except IOError as error:
            logger.error(f"Failed to save custom module: {error}")
            return False

        return True

    def remove_mm_pkg(self, title: str = None) -> bool:
        """
        Allows user to remove an Custom Package from the data saved in
        ~/.config/mmpm/mmpm-custom-packages.json

        Parameters:
            title (str): Custom package title

        Returns:
            success (bool): True on success, False on error
        """

        file = paths.MMPM_CUSTOM_PACKAGES_FILE

        packages: List[MagicMirrorPackage] = []

        with open(file, "r", encoding="utf-8") as custom_pkgs:
            data = json.load(custom_pkgs)

            if not data:
                logger.fatal("No custom packages found in database")
                return False

            try:
                packages = [MagicMirrorPackage(**package) for package in data]
            except Exception as error:
                logger.debug(f"Unable to parse custom package: {error}")
                packages = []

            try:
                match: MagicMirrorPackage = next(filter(lambda pkg: pkg.title == title, packages))
            except StopIteration:
                logger.error(f"Unable to locate Custom Package named '{color.n_green(title)}'")
                return False

        if match:
            packages.remove(match)

        with open(file, "w", encoding="utf-8") as custom_pkgs:
            json.dump([package.serialize() for package in packages], custom_pkgs)

        return True
