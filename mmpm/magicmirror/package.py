#!/usr/bin/env python3
from mmpm.logger import MMPMLogger
from mmpm.env import MMPMEnv
from mmpm.utils import run_cmd
from mmpm.constants import symbols, color

import os
import sys
import json
import mmpm.utils
import datetime
import requests
from pathlib import Path, PosixPath
from re import sub
from bs4 import Tag, NavigableString
from typing import List, Dict, Tuple
from textwrap import fill
from multiprocessing import cpu_count

NA: str = "N/A"

logger = MMPMLogger.get_logger(__name__)


def __sanitize__(string: str) -> str:
    return sub("[//]", "", string)

class MagicMirrorPackage:
    """
    A container object used to simplify the represenation of a given
    MagicMirror package's metadata
    """

    __slots__ = "title", "author", "repository", "description", "category", "directory", "is_installed", "env", "is_upgradable"

    def __init__(
            self,
            title: str = NA,
            author: str = NA,
            repository: str = NA,
            description: str = NA,
            category: str = NA,
            directory: str = "",
            is_installed: bool = False,
        ) -> None:
        self.env = MMPMEnv()
        self.title = __sanitize__(title.strip())
        self.author = __sanitize__(author.strip())
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
            show_path: bool = False,
            exclude_installed: bool = False,
            hide_installed_indicator: bool = False,
            ) -> None:
        """
        Displays more detailed information that presented in normal search results.
        The output is formatted similarly to the output of the Debian/Ubunut 'apt' CLI

        Parameters:
            detailed (bool):
                if True, extra detail is displayed about the package

            remote (bool):
                if True, info is retrieved from the repository's API (GitHub, GitLab, or Bitbucket)

            title_only (bool):
                if True, only the title is displayed

        Returns:
            None
        """
        if exclude_installed and self.is_installed:
            return

        if title_only:
            print(f"{self.title} [installed]" if self.is_installed and not hide_installed_indicator else "")
            return

        print(color.n_green(self.title) + (" [installed]" if self.is_installed else ""))

        if show_path:
            modules_dir: PosixPath = self.env.mmpm_magicmirror_root.get() / "modules"
            print(f"  Directory: {modules_dir / self.directory}")

        if detailed:
            print(f"  Category: {self.category}\n  Repository: {self.repository}\n  Author: {self.author}")

            if remote:
                for key, value in RemotePackage(self).serialize().items():
                    print(f"  {key}: {value}")

            print(fill(f"  Description: {self.description}\n", width=80), "\n")

        else:
            print(f"  {self.description[:120] + '...' if len(self.description) > 120 else self.description}\n")


    def __dict__(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "repository": self.repository,
            "description": self.description,
            "directory": self.directory.name,
            "is_installed": self.is_installed,
            "is_upgradable": self.is_upgradable,
        }

    def serialize(self, full: bool = False) -> dict:
        """
        Produces either a subset or full representation of the __dict__ method.

        Parameters:
            full (bool): if True, the full output of __dict__ is returned, otherwise a subset is returned

        Returns:
            serialized (Dict[str, str]): a dict containing title, author, repository, description, etc.
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
            serialized["is_installed"] = self.is_installed
            serialized["is_upgradable"] = self.is_upgradable

        return serialized


    def install(self, assume_yes: bool = False) -> None:
        """
        Delegates installation to an InstallationHandler instance. The repo is
        cloned, and all dependencies are installed (to the best of the package
                                                    manager's ability). Errors are displayed as they occur, but they are mostly ignored.

        Parameters:
            None

        Returns:
            None
        """

        if self.is_installed:
            logger.msg.error(f"'{self.title}' is already installed")
            return

        if not assume_yes and not mmpm.utils.prompt(f"Continue installing {color.n_green(self.title)} ({self.repository})?"):
            return

        InstallationHandler(self).execute()


    def remove(self, assume_yes: bool = False) -> bool:
        if not self.is_installed:
            logger.msg.error(f"'{self.title}' is not installed")
            return

        if not assume_yes and not mmpm.utils.prompt(f"Continue removing {color.n_green(self.title)} ({self.repository})?"):
            return

        modules_dir: PosixPath = self.env.mmpm_magicmirror_root.get() / "modules"

        run_cmd(["rm", "-rf", str(modules_dir / self.directory)], progress=True)
        logger.msg.info(f"Removed {color.n_green(self.title)} {symbols.GREEN_CHECK_MARK}\n")


    def clone(self) -> bool:
        modules_dir: PosixPath = self.env.mmpm_magicmirror_root.get() / "modules"
        return run_cmd(["git", "clone", self.repository, str(modules_dir / self.directory)])


    def update(self) -> None:
        modules_dir: PosixPath = self.env.mmpm_magicmirror_root.get() / "modules"

        if not modules_dir.exists():
            logger.msg.fatal(f"'{str(modules_dir)}' does not exist.")
            self.is_upgradable = False
            return

        os.chdir(modules_dir / self.directory)

        try:
            error_code, _, stdout = mmpm.utils.run_cmd(["git", "fetch", "--dry-run"], progress=False)

        except KeyboardInterrupt:
            logger.info("User killed process with CTRL-C")
            sys.exit(127)

        if error_code:
            print(symbols.RED_X)
            logger.msg.error("Unable to communicate with git server")

        self.is_upgradable = bool(stdout)


    def upgrade(self) -> bool:
        """
        Checks for available package updates, and alerts the user. Or, pulls latest
        version of module(s) from the associated repos.

        If upgrading, a user can upgrade all modules that have available upgrades
        by ommitting additional arguments. Or, upgrade specific modules by
        supplying their case-sensitive name(s) as an addtional argument.

        Parameters:
            package (MagicMirrorPackage): the MagicMirror module being upgraded

        Returns:
            stderr (str): the resulting error message of the upgrade. If the message is zero length, it was successful
        """
        modules_dir: PosixPath = self.env.mmpm_magicmirror_root.get() / "modules"
        self.directory = modules_dir / self.title

        os.chdir(modules_dir / self.directory)

        logger.msg.info(f"Upgrading {color.n_green(self.title)}")
        error_code, _, stderr = mmpm.utils.run_cmd(["git", "pull"])

        if error_code:
            logger.msg.error(f"Failed to upgrade MagicMirror {symbols.RED_X}")
            logger.error(stderr)
            return stderr

        else:
            print(symbols.GREEN_CHECK_MARK)

        InstallationHandler(self).execute()

        if stderr:
            print(symbols.RED_X)
            logger.msg.error(stderr)
            return stderr

        return ""


    @classmethod
    def from_raw_data(cls, raw_data: List[Tag], category=NA):
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
    __slots__ = "env", "package"

    def __init__(self, package: MagicMirrorPackage):
        self.package = package


    def execute(self) -> bool:
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
        root = self.package.environ.mmpm_magicmirror_root

        modules_dir = root.get() / "modules"

        self.package.directory = modules_dir / self.package.directory

        if not modules_dir.exists():
            logger.msg.fatal(
                    f"{modules_dir} does not exist. Is {root.name} set properly?"
                    )
            logger.fatal(f"{modules_dir} does not exist.")
            return False

        os.chdir(modules_dir)

        error_code = 0

        if not self.package.directory.exists():
            error_code, _, _ = self.package.clone()

        os.chdir(self.package.directory)

        if error_code:
            logger.msg.error(f"Failed to clone {self.package.title}: {error_code}")

        if self.__deps_file_exists__("package.json"):
            error_code, _, stderr = self.__npm_install__()

            if error_code:
                print(symbols.RED_X)
                logger.msg.error(f"Install failed: {stderr}, {error_code}")
            else:
                print(symbols.GREEN_CHECK_MARK)

        if self.__deps_file_exists__("Gemfile"):
            error_code, _, stderr = self.__bundle_install__()

            if error_code:
                print(symbols.RED_X)
                logger.msg.error(f"Install failed: {stderr}, {error_code}")
            else:
                print(symbols.GREEN_CHECK_MARK)

        if self.__deps_file_exists__("Makefile"):
            error_code, _, stderr = self.__make__()

            if error_code:
                print(symbols.RED_X)
                logger.msg.error(f"Install failed: {stderr}, {error_code}")
            else:
                print(symbols.GREEN_CHECK_MARK)

        if self.__deps_file_exists__("CmakeLists.txt"):
            error_code, _, stderr = self.__cmake__()

            if error_code:
                print(symbols.RED_X)
                logger.error(f"Install failed: {stderr}, {error_code}")
                logger.msg.error(f"Install failed: {stderr}, {error_code}")
            else:
                print(symbols.GREEN_CHECK_MARK)

            if self.__deps_file_exists__("Makefile"):
                error_code, _, stderr = self.__make__()

                if error_code:
                    print(symbols.RED_X)
                    logger.error(f"Install failed: {stderr}, {error_code}")
                    logger.msg.error(f"Install failed: {stderr}, {error_code}")
                else:
                    print(symbols.GREEN_CHECK_MARK)

        if error_code:
            if mmpm.utils.prompt(f"Installation failed. Would you like to remove {self.package.title}?"):
                message = f"Installtion failed. Removing {self.package.title}"
                logger.info(message)
                logger.msg.info(message)
                self.package.remove()
            return False

        print(f"{symbols.GREEN_DASHES} Installation complete " + symbols.GREEN_CHECK_MARK)
        logger.info(f"Exiting installation handler from {self.package.directory}")
        return True


    def __cmake__(self) -> Tuple[int, str, str]:
        """Used to run make from a directory known to have a CMakeLists.txt file

        Parameters:
            None

        Returns:
            Tuple[error_code (int), stdout (str), error_message (str)]

        """
        logger.info(f"Running 'cmake ..' in {self.package.directory}")
        logger.msg.info(f"{symbols.GREEN_DASHES} Found CMakeLists.txt. Building with `cmake`")

        os.system("mkdir -p build")
        os.chdir("build")
        os.system("rm -rf *")
        return run_cmd(["cmake", ".."])


    def __make__(self) -> Tuple[int, str, str]:
        """
        Used to run make from a directory known to have a Makefile

        Parameters:
            None

        Returns:
            Tuple[error_code (int), stdout (str), error_message (str)]
        """

        logger.info(f"Running 'make -j {cpu_count()}' in {self.package.directory}")
        logger.msg.info(f"{symbols.GREEN_DASHES} Found Makefile. Running `make -j {cpu_count()}`")
        return run_cmd(["make", "-j", f"{cpu_count()}"])


    def __npm_install__(self) -> Tuple[int, str, str]:
        """
        Used to run npm install from a directory known to have a package.json file

        Parameters:
            None

        Returns:
            Tuple[error_code (int), stdout (str), error_message (str)]
        """
        logger.info(f"Running 'npm install' in {self.package.directory}")
        logger.msg.info(f"{symbols.GREEN_DASHES} Found package.json. Running `npm install`")
        return run_cmd(["npm", "install"])


    def __bundle_install__(self) -> Tuple[int, str, str]:
        """
        Used to run npm install from a directory known to have a package.json file

        Parameters:
            None

        Returns:
            Tuple[error_code (int), stdout (str), error_message (str)]
        """
        logger.info(f"Running 'bundle install' in {self.package.directory}")
        logger.msg.info(f"{symbols.GREEN_DASHES} Found Gemfile. Running `bundle install`")
        return run_cmd(["bundle", "install"])


    def __deps_file_exists__(self, file_name: str) -> bool:
        """
        Case-insensitive search for existing package specification file in current directory

        Parameters:
            file_name (str): The name of the file to search for

        Returns:
            bool: True if the file exists, False if not
        """

        for dep in [file_name, file_name.lower(), file_name.upper()]:
            if Path(self.package.directory / dep).exists():
                return True

        return False


class RemotePackage:
    def __init__(self, package: MagicMirrorPackage):
        self.package = package


    @classmethod
    def health(cls):
        """
        Contacts GitHub, GitLab, and Bitbucket APIs to ensure they are up and
        running. Also, captures the number of requests that may be made to the
        GitHub API, which is more restrictive than GitLab and Bitbucket

        Parameters:
            None

        Returns:
            health (dict): a dictionary corresponding to each of the APIs,
                        containing errors and/or warnings, if applicable.
                        If no errors or warnings are present, the API is reachable
        """
        health: dict = {
                'github': {'error': "", "warning": ""},
                'gitlab': {'error': "", "warning": ""},
                'bitbucket': {'error': "", "warning": ""},
                }

        github_api_response: requests.Response = mmpm.utils.safe_get_request("https://api.github.com/rate_limit")

        if not github_api_response.status_code or github_api_response.status_code != 200:
            health["github"]["error"] = "Unable to contact GitHub API"

        github_api: dict = json.loads(github_api_response.text)
        reset: int = github_api["rate"]["reset"]
        remaining: int = github_api["rate"]["remaining"]

        reset_time = datetime.datetime.utcfromtimestamp(reset).strftime("%Y-%m-%d %H:%M:%S")

        if not remaining:
            health["github"]["error"] = f"Unable to use `--verbose` option. No GitHub API requests remaining. Request count will reset at {reset_time}"
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
        Retrieves details about the provided MagicMirrorPackage from it's
        repository. GitHub, GitLab, and Bitbucket projects are supported

        Parameters:
            package (MagicMirrorPackage): the packge to be queried

        Returns:
            details (dict): a dictionary with star, forks, and issue counts, and creation and last updated dates
        """
        spliced: List[str] = self.package.repository.split("/")
        user: str = spliced[-2]
        project: str = spliced[-1].replace(".git", "")  # in case the user added .git to the end of the url
        details = {}

        if "github" in self.package.repository:
            url = f"https://api.github.com/repos/{user}/{project}"
            logger.info(f"Constructed {url} to request more details for {self.package.title}")
            data = mmpm.utils.safe_get_request(url)

            if not data:
                logger.error(f"Unable to retrieve {self.package.title} details, data was empty")

            details = self.__format_github_api_details__(json.loads(data.text)) if data else {}

        elif "gitlab" in self.package.repository:
            url = f"https://gitlab.com/api/v4/projects/{user}%2F{project}"
            logger.info(f"Constructed {url} to request more details for {self.package.title}")
            data = mmpm.utils.safe_get_request(url)

            if not data:
                logger.error(f"Unable to retrieve {self.package.title} details, data was empty")

            details = self.__format_gitlab_api_details__(json.loads(data.text), url) if data else {}

        elif "bitbucket" in self.package.repository:
            url = f"https://api.bitbucket.org/2.0/repositories/{user}/{project}"
            logger.info(f"Constructed {url} to request more details for {self.package.title}")
            data = mmpm.utils.safe_get_request(url)

            if not data:
                logger.error(f"Unable to retrieve {self.package.title} details, data was empty")

            details =  self.__format_bitbucket_api_details__(json.loads(data.text), url) if data else {}

        return details


    def __format_bitbucket_api_details__(self, data: dict, url: str) -> dict:
        """
        Helper method to format remote repository data from Bitbucket

        Parameters:
            data (dict): JSON data from the API request
            url (str): the constructed url of the API used to retrieve additional info

        Returns:
            details (dict): a dictionary with star, forks, and issue counts, and creation and last updated dates
        """
        stars = mmpm.utils.safe_get_request(f"{url}/watchers")
        forks = mmpm.utils.safe_get_request(f"{url}/forks")
        issues = mmpm.utils.safe_get_request(f"{url}/issues")

        return (
                {
                    "Stars": int(json.loads(stars.text)["pagelen"]) if stars else "N/A",
                    "Issues": int(json.loads(issues.text)["pagelen"]) if issues else "N/A",
                    "Created": data["created_on"].split("T")[0] if data else "N/A",
                    "Last Updated": data["updated_on"].split("T")[0] if data else "N/A",
                    "Forks": int(json.loads(forks.text)["pagelen"]) if forks else "N/A",
                    }
                if data and stars
                else {}
                )


    def __format_gitlab_api_details__(self, data: dict, url: str) -> dict:
        """
        Helper method to format remote repository data from GitLab

        Parameters:
            data (dict): JSON data from the API request
            url (str): the constructed url of the API used to retrieve additional info

        Returns:
            details (dict): a dictionary with star, forks, and issue counts, and creation and last updated dates
        """
        issues = mmpm.utils.safe_get_request(f"{url}/issues")

        return (
                {
                    "Stars": data["star_count"] if data else "N/A",
                    "Issues": len(json.loads(issues.text)) if issues else "N/A",
                    "Created": data["created_at"].split("T")[0] if data else "N/A",
                    "Last Updated": data["last_activity_at"].split("T")[0]
                    if data
                    else "N/A",
                    "Forks": data["forks_count"] if data else "N/A",
                    }
                if data
                else {}
                )


    def __format_github_api_details__(self, data: dict) -> dict:
        """
        Helper method to format remote repository data from GitHub

        Parameters:
            data (dict): JSON data from the API request

        Returns:
            details (dict): a dictionary with star, forks, and issue counts, and creation and last updated dates
        """
        return (
                {
                    "Stars": data["stargazers_count"] if data else "N/A",
                    "Issues": data["open_issues"] if data else "N/A",
                    "Created": data["created_at"].split("T")[0] if data else "N/A",
                    "Last Updated": data["updated_at"].split("T")[0] if data else "N/A",
                    "Forks": data["forks_count"] if data else "N/A",
                    }
                if data
                else {}
                )
