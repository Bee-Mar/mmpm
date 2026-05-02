import json
import os
import sys
from datetime import datetime

if sys.version_info.minor > 10:
    from datetime import UTC  # type: ignore

from multiprocessing import cpu_count
from pathlib import Path, PosixPath
from re import sub
from textwrap import fill
from typing import Any, Callable, Dict, List, Tuple

import requests

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

    env: MMPMEnv = MMPMEnv()

    __slots__ = (
        "title",
        "author",
        "repository",
        "description",
        "category",
        "directory",
        "is_installed",
        "is_upgradable",
        "stars",
        "last_updated",
        "license",
    )

    # pylint: disable=unused-argument,too-many-positional-arguments
    def __init__(
        self,
        title: str = NA,
        author: str = NA,
        repository: str = NA,
        description: str = NA,
        category: str = NA,
        directory: str = "",
        is_installed: bool = False,
        stars: int = 0,
        last_updated: str = NA,
        license: str = NA,
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

        self.title = __sanitize__(title).strip()
        self.author = __sanitize__(author).strip()
        self.repository = repository.strip()
        self.description = description.strip()
        self.directory = Path(directory.strip())
        self.category = category.strip()
        self.is_installed = is_installed
        self.is_upgradable = False
        self.stars = stars
        self.last_updated = last_updated
        self.license = license.strip() if isinstance(license, str) else NA

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

    # pylint: disable=too-many-positional-arguments
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

        max_width = 100
        default_fill = lambda message: fill(message, width=max_width, initial_indent="\t", subsequent_indent="\t") + "\n"

        text = color.n_green(self.title) + (" [installed]" if self.is_installed else "") + "\n"

        if detailed:
            modules_dir: PosixPath = self.env.MMPM_MAGICMIRROR_ROOT.get() / "modules"

            text += default_fill(f"Directory: {modules_dir / self.directory}")
            text += default_fill(f"Category: {self.category}")
            text += default_fill(f"Author: {self.author}")
            text += default_fill(f"Repository: {self.repository}")
            text += default_fill(f"Installed: {'true' if self.is_installed else 'false'}")
            text += default_fill(f"Stars: {self.stars}")
            text += default_fill(f"Last Updated: {self.last_updated}")

            if remote:
                for key, value in RemotePackage(self).serialize().items():
                    text += default_fill(f"{key.replace('_', ' ').capitalize()}: {value}")

            text += fill(f"Description: {self.description}", width=max_width, initial_indent="\t", subsequent_indent="\t\t     ") + "\n"
        else:
            text += fill(self.description, width=100, initial_indent="\t", subsequent_indent="\t") + "\n"

        print(f"{text}\n")

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
            "stars": self.stars,
            "last_updated": self.last_updated,
            "license": self.license,
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

        try:
            self.is_upgradable = repo_up_to_date(modules_dir / self.directory)
        except KeyboardInterrupt:
            logger.info("User killed process with CTRL-C")
            sys.exit(127)

    def upgrade(self, force: bool = False) -> tuple[bool, str]:
        """
        Upgrades the package by pulling the latest changes from the remote repository.

        Local modifications are stashed before the pull and restored afterwards so
        that a dirty working tree does not block the merge and user changes are not
        silently discarded. If dependency installation fails after a successful pull
        the commit is rolled back via ORIG_HEAD so the package is left in its last
        known-good state.

        Parameters:
            force (bool): If True, forces dependency reinstall even when already up to date.

        Returns:
            tuple[bool, str]: (True, "") on success; (False, error_message) on failure.
        """
        pkg_dir: PosixPath = self.env.MMPM_MAGICMIRROR_ROOT.get() / "modules" / self.directory

        # Stash any local modifications so git pull cannot be blocked by dirty-tree
        # conflicts while still preserving the user's changes.
        _, status_out, _ = run_cmd(["git", "status", "--porcelain"], progress=False, cwd=pkg_dir)
        stashed = False

        if status_out.strip():
            logger.debug(f"Stashing local changes in {self.directory} before upgrade")
            stash_code, _, stash_err = run_cmd(["git", "stash"], message="Stashing local changes", cwd=pkg_dir)

            if stash_code:
                return False, f"Failed to stash local changes: {stash_err.strip()}"

            stashed = True

        error_code, stdout, stderr = run_cmd(["git", "pull"], message="Retrieving changes", cwd=pkg_dir)

        # Restore stashed changes regardless of pull outcome.
        if stashed:
            pop_code, _, pop_err = run_cmd(["git", "stash", "pop"], message="Restoring local changes", cwd=pkg_dir)

            if pop_code:
                # Conflicts between the stash and the pulled changes need manual resolution.
                logger.warning(
                    f"git stash pop had conflicts in {self.directory}. Run 'git stash pop' in the module directory to resolve them manually."
                )

        # Only a non-zero exit code signals failure — git writes fetch progress to
        # stderr even on a successful pull, so checking stderr alone gives false negatives.
        if error_code:
            error_msg = (stderr or stdout).strip()
            logger.error(f"Failed to upgrade {self.title}: {error_msg}")
            return False, error_msg

        pulled_changes = "Already up to date." not in stdout

        if pulled_changes or force:
            if not InstallationHandler(self).install():
                # Roll back the pull so the package is not left with a broken dependency state.
                logger.error(f"Dependency install failed after upgrading {self.title}; rolling back to previous commit")
                run_cmd(["git", "reset", "--hard", "ORIG_HEAD"], progress=False, cwd=pkg_dir)
                return False, "Upgrade pulled successfully but dependency installation failed; changes have been rolled back"

            print(f"Upgraded {color.n_green(self.title)}")
            logger.debug(f"Upgraded {self.title}")

        return True, ""

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        """Create a MagicMirrorPackage from a JSON dict coming from the modules.magicmirror.builders index.

        Expected JSON structure from https://modules.magicmirror.builders/data/modules.json:
        {
          "name": "MMM-ModuleName",
          "category": "Category Name",
          "url": "https://github.com/user/repo",
          "id": "user/repo",
          "maintainer": "username",
          "description": "Module description",
          "stars": <count>,
          "lastCommit": "YYYY-MM-DDTHH:mm:ss+00:00",
          ...
        }

        Parameters:
            data (Dict[str, Any]): The JSON dictionary for a single module

        Returns:
            MagicMirrorPackage: A new instance with data from the JSON
        """
        # Extract fields from the JSON (using the actual field names from modules.json)
        title = data.get("name") or NA
        author = data.get("maintainer") or NA
        repository = data.get("url") or NA
        description = data.get("description") or NA
        category = data.get("category") or NA
        stars = data.get("stars") or 0
        last_commit = data.get("lastCommit") or NA
        license = data.get("license") or NA

        if last_commit != NA:
            last_updated = last_commit.split("T")[0]
            # time_format = "%Y-%m-%dT%H:%M:%S%z"
            # date = datetime.strptime(last_commit, time_format)
            # last_updated = f"{date.year}-{date.month}-{date.day}"
        else:
            last_updated = last_commit

        # Derive directory name from the repository URL or id
        directory = ""

        if isinstance(repository, str) and repository and repository != NA:
            directory = repository.split("/")[-1].replace(".git", "")
        elif isinstance(data.get("id"), str) and data.get("id"):
            directory = str(data.get("id")).split("/")[-1]

        return MagicMirrorPackage(
            title=title,
            author=author,
            repository=repository,
            description=description,
            category=category,
            directory=directory,
            last_updated=last_updated,
            stars=stars,
            license=license,
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

        if sys.version_info.minor > 10:
            reset_time = datetime.fromtimestamp(reset, UTC).strftime("%Y-%m-%d %H:%M:%S")
        else:
            reset_time = datetime.utcfromtimestamp(reset).strftime("%Y-%m-%d %H:%M:%S")

        if not remaining:
            health["github"]["error"] = (
                f"Unable to use `--verbose` option. No GitHub API requests remaining. Request count will reset at {reset_time}"
            )
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
            dict: A dictionary containing details such as forks, issue counts, and creation and last updated dates of the repository.
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
            dict: A dictionary with forks, issue counts, and creation and last updated dates.
        """
        forks = safe_get_request(f"{url}/forks")
        issues = safe_get_request(f"{url}/issues")

        return (
            {
                "issues": int(json.loads(issues.text)["pagelen"]) if issues else "N/A",
                "created": data["created_on"].split("T")[0] if data else "N/A",
                "forks": int(json.loads(forks.text)["pagelen"]) if forks else "N/A",
            }
            if data
            else {}
        )

    def __format_gitlab_api_details__(self, data: dict, url: str) -> dict:
        """
        Helper method to format remote repository data from GitLab.

        Parameters:
            data (dict): JSON data from the API request.
            url (str): The constructed URL of the API used to retrieve additional info.

        Returns:
            dict: A dictionary with forks, issue counts, and creation and last updated dates.
        """
        issues = safe_get_request(f"{url}/issues")

        return (
            {
                "issues": len(json.loads(issues.text)) if issues else "N/A",
                "created": data["created_at"].split("T")[0] if data else "N/A",
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
            dict: A dictionary with forks, issue counts, and creation and last updated dates.
        """
        return (
            {
                "issues": data["open_issues"] if data else "N/A",
                "created": data["created_at"].split("T")[0] if data else "N/A",
                "forks": data["forks_count"] if data else "N/A",
            }
            if data
            else {}
        )
