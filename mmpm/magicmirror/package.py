#!/usr/bin/env python3
import datetime
import json
import os
import sys
from multiprocessing import cpu_count
from pathlib import Path, PosixPath
from re import sub
from textwrap import fill
from typing import Any, Callable, Dict, List, Tuple

import requests
from bs4 import NavigableString, Tag

from mmpm.constants import color
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.utils import repo_up_to_date, run_cmd, safe_get_request

NA: str = "N/A"

logger = MMPMLogFactory.get_logger(__name__)


def __sanitize__(string: str) -> str:
    return sub("[//]", "", string)


# pylint: disable=too-many-instance-attributes
class MagicMirrorPackage:
    """
    A container object used to simplify the represenation of a given
    MagicMirror package's metadata
    """

    __slots__ = (
        "title",
        "author",
        "repository",
        "description",
        "category",
        "directory",
        "is_installed",
        "env",
        "is_upgradable",
    )

    # pylint: disable=unused-argument
    def __init__(
        self,
        title: str = NA,
        author: str = NA,
        repository: str = NA,
        description: str = NA,
        category: str = NA,
        directory: str = "",
        is_installed: bool = False,
        **kwargs,
    ) -> None:
        """
        Initializes a MagicMirrorPackage instance with the provided metadata.

        Parameters:
            title (str): The title of the package.
            author (str): The author of the package.
            repository (str): The repository URL of the package.
            description (str): The description of the package.
            category (str): The category of the package.
            directory (str): The directory where the package is installed.
            is_installed (bool): A flag indicating whether the package is installed.

        Additional keyword arguments are ignored, but intentionally provided as a means to simplify API interaction.
        """

        self.env = MMPMEnv()
        self.title = __sanitize__(title).strip()
        self.author = __sanitize__(author).strip()
        self.repository = repository.strip()
        self.description = description.strip()
        self.directory = Path(directory.strip())
        self.category = category.strip()
        self.is_installed = is_installed
        self.is_upgradable = False

    def __str__(self) -> str:
        return str(self.serialize())

    def __repr__(self) -> str:
        return str(self.serialize())

    def __hash__(self) -> int:
        return hash((self.repository.lower(), self.directory.name.lower()))

    def __eq__(self, other) -> bool:
        if other is None:
            return bool(hash(self) == __NULL__)
        else:
            return hash(self) == hash(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def display(
        self,
        detailed: bool = False,
        remote: bool = False,
        title_only: bool = False,
        exclude_installed: bool = False,
        hide_installed_indicator: bool = False,
    ) -> None:
        """
        Displays the package information, optionally with additional details or in a simplified format.

        Parameters:
            detailed (bool): Whether to display detailed information about the package.
            remote (bool): Whether to retrieve additional information from the remote repository.
            title_only (bool): Whether to display only the title of the package.
            exclude_installed (bool): Whether to exclude the package if it is installed.
            hide_installed_indicator (bool): Whether to hide the indicator that shows if the package is installed.

        Returns:
            None
        """
        if exclude_installed and self.is_installed:
            return

        if title_only:
            print(f"{self.title} [installed]" if self.is_installed and not hide_installed_indicator else self.title)
            return

        print(
            color.n_green(self.title) + (" [installed]" if self.is_installed else ""),
            end="",
        )

        if detailed:
            modules_dir: PosixPath = self.env.MMPM_MAGICMIRROR_ROOT.get() / "modules"
            print(f"\n  Directory: {modules_dir / self.directory}")
            print(f"  Category: {self.category}\n  Repository: {self.repository}\n  Author: {self.author}")

            if remote:
                for key, value in RemotePackage(self).serialize().items():
                    print(f"  {key.replace('_',' ').capitalize()}: {value}")

            print(fill(f"  Description: {self.description}\n", width=80), "\n")

        else:
            print(f" \n\t{self.repository}")

        print()

    def serialize(self, full: bool = False) -> Dict[str, Any]:
        """
        Serializes the package data into a dictionary.

        Parameters:
            full (bool): If True, returns the full data, otherwise a subset.

        Returns:
            Dict[str, Any]: The serialized package data.
        """

        serialized = {
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "repository": self.repository,
            "description": self.description,
            "directory": self.directory.name,
        }

        if full:
            serialized["is_installed"] = self.is_installed  # type: ignore
            serialized["is_upgradable"] = self.is_upgradable  # type: ignore

        return serialized

    def install(self) -> bool:
        """
        Installs the package by cloning the repository and installing dependencies.

        Parameters:
            None

        Returns:
            bool: True if the installation is successful, False otherwise.
        """

        return InstallationHandler(self).install()

    def remove(self) -> bool:
        """
        Removes the package from the installation directory.

        Parameters:
            None

        Returns:
            bool: True if the package is successfully removed, False otherwise.
        """

        modules_dir: PosixPath = self.env.MMPM_MAGICMIRROR_ROOT.get() / "modules"
        error_code, stdout, stderr = run_cmd(["rm", "-rf", str(modules_dir / self.directory)], message="Removing package")
        return not error_code and not stderr and not stdout

    def clone(self) -> Tuple[int, str, str]:
        """
        Clones the package repository into the MagicMirror modules directory.

        Parameters:
            None

        Returns:
            Tuple[int, str, str]: The result of the clone operation including any error codes and messages.
        """

        modules_dir: PosixPath = self.env.MMPM_MAGICMIRROR_ROOT.get() / "modules"

        return run_cmd(
            ["git", "clone", self.repository, str(modules_dir / self.directory)],
            message="Downloading",
        )

    def update(self) -> None:
        """
        Checks for updates to the package by querying the remote repository.

        Parameters:
            None

        Returns:
            None
        """
        modules_dir: PosixPath = self.env.MMPM_MAGICMIRROR_ROOT.get() / "modules"

        if not modules_dir.exists():
            logger.fatal(f"{self.env.MMPM_MAGICMIRROR_ROOT.name}='{str(modules_dir)}' does not exist.")
            self.is_upgradable = False
            return

        os.chdir(modules_dir / self.directory)

        try:
            self.is_upgradable = repo_up_to_date(modules_dir / self.directory)
        except KeyboardInterrupt:
            logger.info("User killed process with CTRL-C")
            sys.exit(127)

    def upgrade(self, force: bool = False) -> bool:
        """
        Upgrades the package by pulling the latest changes from the remote repository.

        Parameters:
            force (bool): If True, forces the upgrade even if the repository is up to date.

        Returns:
            bool: True if the upgrade is successful, False otherwise.
        """
        modules_dir: PosixPath = self.env.MMPM_MAGICMIRROR_ROOT.get() / "modules"

        os.chdir(modules_dir / self.directory)

        error_code, stdout, stderr = run_cmd(["git", "pull"], message="Retrieving changes")

        if error_code or stderr:
            logger.error(f"Failed to upgrade {self.title}: {stderr}")
            return False

        elif "up to date" not in stdout or force and InstallationHandler(self).install():
            print(f"Upgraded {color.n_green(self.title)}")
            logger.debug(f"Upgraded {color.n_green(self.title)}")

        return True

    @classmethod
    def from_raw_data(cls, raw_data: List[Tag], category=NA):
        """
        Creates a MagicMirrorPackage instance from raw HTML data.

        Parameters:
            raw_data (List[Tag]): A list of BeautifulSoup Tag objects representing HTML elements.
            category (str): The category of the package.

        Returns:
            MagicMirrorPackage: An instance of MagicMirrorPackage created from the provided data.
        """
        title_info = raw_data[0].contents[0].contents[0]
        package_title: str = __sanitize__(title_info) if title_info else NA

        anchor_tag = raw_data[0].find_all("a")[0]
        repo = str(anchor_tag["href"]) if anchor_tag.has_attr("href") else NA

        # some people get fancy and embed anchor tags
        author_info = raw_data[1].contents
        package_author = str() if author_info else NA

        for info in author_info:
            if isinstance(info, NavigableString):
                package_author += f"{info.strip()} "
            elif isinstance(info, Tag):
                package_author += f"{info.contents[0].strip()} "

        description_info = raw_data[2].contents
        package_description: str = "" if description_info else NA

        # some people embed other html elements in here, so they need to be parsed out
        for info in description_info:
            if isinstance(info, Tag):
                for content in info:
                    package_description += content.string
            else:
                package_description += info.string

        return MagicMirrorPackage(
            title=package_title,
            author=package_author,
            description=package_description,
            repository=repo,
            category=category,
            directory=repo.split("/")[-1].replace(".git", ""),
        )


__NULL__: int = hash(MagicMirrorPackage())


class InstallationHandler:
    """
    Delegate class that handles the installation process of
    MagicMirrorPackage's by cloning their repo and identifying dependencies
    that need to be installed.
    """

    __slots__ = {"package"}

    def __init__(self, package: MagicMirrorPackage):
        self.package = package

    def exec(self, funk: Callable) -> bool:
        logger.debug(f"Calling exec wrapper to install dependencies for '{self.package.title}'")
        error_code, _, stderr = funk()

        if error_code:
            logger.error(stderr)
            return False

        return True

    # pylint: disable=too-many-return-statements
    def install(self) -> bool:
        """
        Utility method that detects package.json, Gemfiles, Makefiles, and
        CMakeLists.txt files, and handles the build process for each of the
        previously mentioned files. If the install is successful, an empty string
        is returned. The installation process relies on the location of the current
        directory the os library detects.

        Parameters:
            directory (str): the root directory of the package

        Returns:
            stderr (str): success if the string is empty, fail if not
        """
        root = self.package.env.MMPM_MAGICMIRROR_ROOT
        modules_dir = root.get() / "modules"
        self.package.directory = modules_dir / self.package.directory

        if not modules_dir.exists():
            logger.fatal(f"{root.name}='{modules_dir}' does not exist. Is {root.name} set properly?")
            return False

        os.chdir(modules_dir)

        if not (self.package.directory / ".git").exists():
            logger.debug(f"{self.package.directory / '.git'} not found. Cloning repo.")
            error_code, _, stderr = self.package.clone()

            if error_code:
                logger.error(f"Failed to clone {self.package.title}: {stderr}")
                return False

        os.chdir(self.package.directory)

        if self.exists("package.json"):
            return self.exec(self.npm_install)
        elif self.exists("Gemfile"):
            return self.exec(self.bundle_install)
        elif self.exists("Makefile"):
            return self.exec(self.make)
        elif self.exists("CMakeLists.txt"):
            return self.exec(self.cmake)
        elif self.exists("requirements.txt"):
            return self.exec(self.pip_install)
        elif self.exists("pom.xml"):
            return self.exec(self.maven_install)
        elif self.exists("go.mod"):
            return self.exec(self.go_build)

        logger.debug(f"Unable to find any dependency file associated with {self.package.title}")
        return True

    def cmake(self) -> Tuple[int, str, str]:
        """
        Wrapper method around calling cmake to build a module's dependencies.

        Parameters:
            None

        Returns:
            Tuple[int, str, str]: A tuple containing the exit code, stdout, and stderr from the 'pip install' command.
        """
        logger.debug(f"Running 'cmake ..' in {self.package.directory}")

        build_dir = Path(self.package.directory / "build")
        build_dir.mkdir(exist_ok=True)

        os.system(f"rm -rf {build_dir}/*")
        os.chdir(build_dir)

        return run_cmd(["cmake", ".."], message="Building with CMake")

    def make(self) -> Tuple[int, str, str]:
        """
        Wrapper method around calling make to build a module's dependencies.

        Parameters:
            None

        Returns:
            Tuple[int, str, str]: A tuple containing the exit code, stdout, and stderr from the 'pip install' command.
        """
        logger.debug(f"Found Makefile. Running `make -j {cpu_count()} in {self.package.directory}`")
        return run_cmd(["make", "-j", f"{cpu_count()}"], message="Building with 'make'")

    def npm_install(self) -> Tuple[int, str, str]:
        """
        Wrapper method around calling 'npm install' to install/build a module's dependencies.

        Parameters:
            None

        Returns:
            Tuple[int, str, str]: A tuple containing the exit code, stdout, and stderr from the 'pip install' command.
        """
        logger.debug(f"Found package.json. Running `npm install` in {self.package.directory}")
        return run_cmd(["npm", "install"], message="Installing Node dependencies")

    def bundle_install(self) -> Tuple[int, str, str]:
        """
        Wrapper method around calling 'bundle install' to install/build a module's dependencies.

        Parameters:
            None

        Returns:
            Tuple[int, str, str]: A tuple containing the exit code, stdout, and stderr from the 'pip install' command.
        """
        logger.debug(f"Found Gemfile. Running `bundle install` in {self.package.directory}")
        return run_cmd(["bundle", "install"], message="Installing Ruby dependencies")

    def pip_install(self) -> Tuple[int, str, str]:
        """
        Wrapper method around calling 'pip install' to install/build a module's dependencies.

        Parameters:
            None

        Returns:
            Tuple[int, str, str]: A tuple containing the exit code, stdout, and stderr from the 'pip install' command.
        """
        logger.debug(f"Running 'pip install' in {self.package.directory}")
        return run_cmd(
            ["pip", "install", "-r", "requirements.txt"],
            message="Installing Python dependencies",
        )

    def maven_install(self) -> Tuple[int, str, str]:
        """
        Wrapper method around calling 'maven install' to install/build a module's dependencies.

        Parameters:
            None

        Returns:
            Tuple[int, str, str]: A tuple containing the exit code, stdout, and stderr from the 'pip install' command.
        """
        logger.debug(f"Running 'mvn install' in {self.package.directory}")
        return run_cmd(["mvn", "install"], message="Building with Maven")

    def go_build(self) -> Tuple[int, str, str]:
        """
        Wrapper method around calling 'go install' to install/build a module's dependencies.

        Parameters:
            None

        Returns:
            Tuple[int, str, str]: A tuple containing the exit code, stdout, and stderr from the 'pip install' command.
        """
        logger.debug(f"Running 'go build' in {self.package.directory}")
        return run_cmd(["go", "build"], message="Building Go project")

    def exists(self, file_name: str) -> bool:
        """
        Verifies the dependency file exists in the module's directory.

        Parameters:
            file_name (str): the name of the dependency to look for

        Returns:
            True if the file exists, False otherwise
        """
        return Path(self.package.directory / file_name).exists()


class RemotePackage:
    """
    Class that collects details about a MagicMirrorPackage from its repository.
    """

    def __init__(self, package: MagicMirrorPackage):
        self.package = package

    @classmethod
    def health(cls):
        """
        Checks the health of GitHub, GitLab, and Bitbucket APIs and their rate limits.

        Parameters: None

        Returns:
            dict: A dictionary containing the health status of GitHub, GitLab, and Bitbucket APIs.
        """
        health: dict = {
            "github": {"error": "", "warning": ""},
            "gitlab": {"error": "", "warning": ""},
            "bitbucket": {"error": "", "warning": ""},
        }

        github_api_response: requests.Response = safe_get_request("https://api.github.com/rate_limit")

        if not github_api_response.status_code or github_api_response.status_code != 200:
            health["github"]["error"] = "Unable to contact GitHub API"

        github_api: dict = json.loads(github_api_response.text)
        reset: int = github_api["rate"]["reset"]
        remaining: int = github_api["rate"]["remaining"]

        reset_time = datetime.datetime.utcfromtimestamp(reset).strftime("%Y-%m-%d %H:%M:%S")

        if not remaining:
            health["github"][
                "error"
            ] = f"Unable to use `--verbose` option. No GitHub API requests remaining. Request count will reset at {reset_time}"
        elif remaining < 10:
            health["github"]["warning"] = f"{remaining} GitHub API requests remaining. Request count will reset at {reset_time}"

        try:
            # GitLab doesn't have rate limits that will cause any issues with checking for repos
            gitlab_api = requests.head("https://gitlab.com", allow_redirects=True, timeout=10)

            if gitlab_api.status_code != 200:
                health["gitlab"]["error"] = "GitLab server returned invalid response"
        except requests.exceptions.RequestException:
            health["gitlab"]["error"] = "Unable to communicate with GitLab server"

        try:
            # Bitbucket rate limits are similar to GitLab
            bitbucket_api = requests.head("https://bitbucket.org", allow_redirects=True, timeout=10)

            if bitbucket_api.status_code != 200:
                health["bitbucket"]["error"] = "Bitbucket server returned invalid response"
        except requests.exceptions.RequestException:
            health["gitlab"]["error"] = "Unable to communicate with Bitbucket server"

        return health

    def serialize(self):
        """
        Retrieves and formats details about the MagicMirror package from its remote repository.

        Parameters: None

        Returns:
            dict: A dictionary containing details such as stars, forks, issue counts, and creation and last updated dates of the repository.
        """
        spliced: List[str] = self.package.repository.split("/")
        user: str = spliced[-2]
        project: str = spliced[-1].replace(".git", "")  # in case the user added .git to the end of the url
        details = {}

        if "github" in self.package.repository:
            url = f"https://api.github.com/repos/{user}/{project}"
            logger.debug(f"Constructed {url} to request more details for {self.package.title}")
            data = safe_get_request(url)

            if not data:
                logger.error(f"Unable to retrieve {self.package.title} details, data was empty")

            details = self.__format_github_api_details__(json.loads(data.text)) if data else {}

        elif "gitlab" in self.package.repository:
            url = f"https://gitlab.com/api/v4/projects/{user}%2F{project}"
            logger.debug(f"Constructed {url} to request more details for {self.package.title}")
            data = safe_get_request(url)

            if not data:
                logger.error(f"Unable to retrieve {self.package.title} details, data was empty")

            details = self.__format_gitlab_api_details__(json.loads(data.text), url) if data else {}

        elif "bitbucket" in self.package.repository:
            url = f"https://api.bitbucket.org/2.0/repositories/{user}/{project}"
            logger.debug(f"Constructed {url} to request more details for {self.package.title}")
            data = safe_get_request(url)

            if not data:
                logger.error(f"Unable to retrieve {self.package.title} details, data was empty")

            details = self.__format_bitbucket_api_details__(json.loads(data.text), url) if data else {}

        return details

    def __format_bitbucket_api_details__(self, data: dict, url: str) -> dict:
        """
        Helper method to format remote repository data from Bitbucket.

        Parameters:
            data (dict): JSON data from the API request.
            url (str): The constructed URL of the API used to retrieve additional info.

        Returns:
            dict: A dictionary with stars, forks, issue counts, and creation and last updated dates.
        """
        stars = safe_get_request(f"{url}/watchers")
        forks = safe_get_request(f"{url}/forks")
        issues = safe_get_request(f"{url}/issues")

        return (
            {
                "stars": int(json.loads(stars.text)["pagelen"]) if stars else "N/A",
                "issues": int(json.loads(issues.text)["pagelen"]) if issues else "N/A",
                "created": data["created_on"].split("T")[0] if data else "N/A",
                "last_updated": data["updated_on"].split("T")[0] if data else "N/A",
                "forks": int(json.loads(forks.text)["pagelen"]) if forks else "N/A",
            }
            if data and stars
            else {}
        )

    def __format_gitlab_api_details__(self, data: dict, url: str) -> dict:
        """
        Helper method to format remote repository data from GitLab.

        Parameters:
            data (dict): JSON data from the API request.
            url (str): The constructed URL of the API used to retrieve additional info.

        Returns:
            dict: A dictionary with stars, forks, issue counts, and creation and last updated dates.
        """
        issues = safe_get_request(f"{url}/issues")

        return (
            {
                "stars": data["star_count"] if data else "N/A",
                "issues": len(json.loads(issues.text)) if issues else "N/A",
                "created": data["created_at"].split("T")[0] if data else "N/A",
                "last_updated": data["last_activity_at"].split("T")[0] if data else "N/A",
                "forks": data["forks_count"] if data else "N/A",
            }
            if data
            else {}
        )

    def __format_github_api_details__(self, data: dict) -> dict:
        """
        Helper method to format remote repository data from GitHub.

        Parameters:
            data (dict): JSON data from the API request.

        Returns:
            dict: A dictionary with stars, forks, issue counts, and creation and last updated dates.
        """
        return (
            {
                "stars": data["stargazers_count"] if data else "N/A",
                "issues": data["open_issues"] if data else "N/A",
                "created": data["created_at"].split("T")[0] if data else "N/A",
                "last_updated": data["updated_at"].split("T")[0] if data else "N/A",
                "forks": data["forks_count"] if data else "N/A",
            }
            if data
            else {}
        )
