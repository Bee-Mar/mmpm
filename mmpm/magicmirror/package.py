#!/usr/bin/env python3
import os
import shutil
import mmpm.consts
import mmpm.utils
import mmpm.color
from mmpm.logger import MMPMLogger
from mmpm.env import MMPMEnv
from mmpm.utils import run_cmd
from pathlib import Path, PosixPath
from re import sub
from bs4 import Tag, NavigableString
from typing import List, Dict, Tuple, Set
from textwrap import fill, indent
from multiprocessing import cpu_count

NA: str = mmpm.consts.NOT_AVAILABLE

logger = MMPMLogger.get_logger(__name__)
logger.setLevel(MMPMEnv.mmpm_log_level.get())

def __sanitize__(string: str) -> str:
    return sub('[//]', '', string)


class MagicMirrorPackage():
    '''
    A container object used to simplify the represenation of a given
    MagicMirror package's metadata
    '''
    # pylint: disable=unused-argument
    def __init__(self,
                 title: str = NA,
                 author: str = NA,
                 repository: str = NA,
                 description: str = NA,
                 category: str = NA,
                 directory: str = '',
                 is_external: bool = False,
                 is_installed: bool = False,
                 **kwargs,
        ) -> None:
        # **kwargs allows for simplified dict unpacking in some instances, and is intentionally unused
        # TODO: get rid of the kwargs
        self.title = __sanitize__(title.strip())
        self.author = __sanitize__(author.strip()) # NOTE: Maybe this shouldn't be here
        self.repository = repository.strip() if repository.strip().endswith(".git") else (f"{repository}.git").strip()
        self.description = description.strip()
        self.directory = Path(directory.strip())
        self.category = category.strip()
        self.is_external = is_external
        self.is_installed = is_installed
        self.is_upgradable = False

    def __str__(self) -> str:
        return str(self.serialize())

    def __repr__(self) -> str:
        return str(self.serialize())

    def __hash__(self) -> int:
        return hash((self.title.lower(), self.repository.lower()))

    def __eq__(self, other) -> bool:
        if other is None:
            return bool(hash(self) == __NULL__)
        else:
            return hash(self) == hash(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def display(self, detailed: bool = False, remote: bool = False, title_only: bool = False, show_path: bool = False, exclude_installed: bool = False) -> None:
        '''
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
        '''
        if exclude_installed and self.is_installed:
            return

        if title_only:
            print(self.title + (" [installed]" if self.is_installed else ""))
            return

        print(mmpm.color.normal_green(self.title) + (" [installed]" if self.is_installed else ""))

        if show_path:
            print(f'  Directory: {self.directory}')

        if detailed:
            print(f'  Category: {self.category}')
            print(f'  Repository: {self.repository}')
            print(f'  Author: {self.author}')

            if remote:
                for key, value in mmpm.utils.get_remote_package_details(self).items():
                    print(f"  {key}: {value}")

            print(fill(f'  Description: {self.description}\n', width=80), '\n')

        else:
            print(f"  {self.description[:120] + '...' if len(self.description) > 120 else self.description}\n")


    def __dict__(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "repository": self.repository,
            "description": self.description,
            "directory": str(self.directory),
            "is_installed": self.is_installed,
            "is_external": self.is_external,
            "is_upgradable": self.is_upgradable,
        }

    def serialize(self, full: bool = False) -> dict:
        '''
        Produces either a subset or full representation of the __dict__ method.

        Parameters:
            full (bool): if True, the full output of __dict__ is returned, otherwise a subset is returned

        Returns:
            serialized (Dict[str, str]): a dict containing title, author, repository, description, etc.
        '''
        if not full:
            return {
                "title": self.title,
                "author": self.author,
                "category": self.category,
                "repository": self.repository,
                "description": self.description,
            }

        return self.__dict__()


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

        if not assume_yes and not mmpm.utils.prompt_user(f'Continue installing {mmpm.color.normal_green(self.title)} ({self.repository})?'):
            return

        # TODO: add user prompt for yes/no
        InstallationHandler(self).execute()


    def remove(self, assume_yes: bool = False) -> bool:
        if not self.is_installed:
            logger.msg.error(f"'{self.title}' is not installed")
            return

        if not assume_yes and not mmpm.utils.prompt_user(f'Continue removing {mmpm.color.normal_green(self.title)} ({self.repository})?'):
            return

        run_cmd(["rm", "-rf", str(self.directory)])
        logger.msg.info(f"Removed {mmpm.color.normal_green(self.title)} {mmpm.consts.GREEN_CHECK_MARK}\n")


    def clone(self) -> bool:
        return run_cmd(["git", "clone", self.repository])


    def update(self) -> None:
        modules_dir: PosixPath = Path(MMPMEnv.mmpm_root.get()) / "modules"

        if not modules_dir.exists():
            logger.msg.env_variables_fatal(f"'{str(modules_dir)}' does not exist.")
            self.is_upgradable = False
            return

        os.chdir(self.directory)

        try:
            error_code, _, stdout = mmpm.utils.run_cmd(['git', 'fetch', '--dry-run'])

        except KeyboardInterrupt:
            print(mmpm.consts.RED_X)
            mmpm.utils.keyboard_interrupt_log()

        if error_code:
            print(mmpm.consts.RED_X)
            logger.msg.error('Unable to communicate with git server')

        self.is_upgradable = bool(stdout)


    def upgrade(self) -> bool:
        '''
        Checks for available package updates, and alerts the user. Or, pulls latest
        version of module(s) from the associated repos.

        If upgrading, a user can upgrade all modules that have available upgrades
        by ommitting additional arguments. Or, upgrade specific modules by
        supplying their case-sensitive name(s) as an addtional argument.

        Parameters:
            package (MagicMirrorPackage): the MagicMirror module being upgraded

        Returns:
            stderr (str): the resulting error message of the upgrade. If the message is zero length, it was successful
        '''
        modules_dir: PosixPath = Path(MMPMEnv.mmpm_root.get() / "modules")
        self.directory = os.path.join(modules_dir, self.title)

        os.chdir(self.directory)

        MMPMLogger.msg.info(f'{mmpm.consts.GREEN_PLUS} Performing upgrade for {mmpm.color.normal_green(self.title)}')
        error_code, _, stderr = mmpm.utils.run_cmd(["git", "pull"])

        if error_code:
            MMPMLogger.error_msg(f'Failed to upgrade MagicMirror {mmpm.consts.RED_X}')
            MMPMLogger.error_msg(stderr)
            return stderr

        else:
            print(mmpm.consts.GREEN_CHECK_MARK)

        stderr = mmpm.utils.install_dependencies(package.directory)

        if stderr:
            print(mmpm.consts.RED_X)
            MMPMLogger.error_msg(stderr)
            return stderr

        return ''


    @classmethod
    def from_raw_data(cls, raw_data: List[Tag], category=NA):
        title_info = raw_data[0].contents[0].contents[0]
        package_title: str = mmpm.utils.sanitize_name(title_info) if title_info else mmpm.consts.NOT_AVAILABLE

        anchor_tag = raw_data[0].find_all('a')[0]
        repo = str(anchor_tag['href']) if anchor_tag.has_attr('href') else mmpm.consts.NOT_AVAILABLE

        # some people get fancy and embed anchor tags
        author_info = raw_data[1].contents
        package_author = str() if author_info else mmpm.consts.NOT_AVAILABLE

        for info in author_info:
            if isinstance(info, NavigableString):
                package_author += f'{info.strip()} '
            elif isinstance(info, Tag):
                package_author += f'{info.contents[0].strip()} '

        description_info = raw_data[2].contents
        package_description: str = str() if description_info else mmpm.consts.NOT_AVAILABLE

        # some people embed other html elements in here, so they need to be parsed out
        for info in description_info:
            if isinstance(info, Tag):
                for content in info:
                    package_description += content.string
            else:
                package_description += info.string


        return MagicMirrorPackage(title=package_title, author=package_author, description=package_description, repository=repo, category=category)


__NULL__: int = hash(MagicMirrorPackage())

class InstallationHandler:
    def __init__(self, package: MagicMirrorPackage):
        self.package = package

    def execute(self) -> str:
        '''
        Utility method that detects package.json, Gemfiles, Makefiles, and
        CMakeLists.txt files, and handles the build process for each of the
        previously mentioned files. If the install is successful, an empty string
        is returned. The installation process relies on the location of the current
        directory the os library detects.

        Parameters:
            directory (str): the root directory of the package

        Returns:
            stderr (str): success if the string is empty, fail if not
        '''

        modules_dir = Path(MMPMEnv.mmpm_root.get()) / "modules"
        os.chdir(modules_dir)

        old_directories: Set[str] = {str(directory) for directory in modules_dir.iterdir()}

        error_code, _, _ = self.package.clone()

        if error_code:
            logger.msg.error(f"Failed to clone {self.package.title}: {error_code}")

        new_directories: Set[str] = {str(directory) for directory in modules_dir.iterdir()}

        self.package.directory = Path(list(new_directories - old_directories)[0])

        if self.__deps_file_exists__("package.json"):
            error_code, _, stderr = self.__npm_install__()

            if error_code:
                print(mmpm.consts.RED_X)
                logger.msg.error(f"Install failed: {stderr}, {error_code}")
            else:
                print(mmpm.consts.GREEN_CHECK_MARK)

        if self.__deps_file_exists__("Gemfile"):
            error_code, _, stderr = self.__bundle_install__()

            if error_code:
                print(mmpm.consts.RED_X)
                logger.msg.error(f"Install failed: {stderr}, {error_code}")
            else:
                print(mmpm.consts.GREEN_CHECK_MARK)

        if self.__deps_file_exists__("Makefile"):
            error_code, _, stderr = self.__make__()

            if error_code:
                print(mmpm.consts.RED_X)
                logger.msg.error(f"Install failed: {stderr}, {error_code}")
            else:
                print(mmpm.consts.GREEN_CHECK_MARK)


        if self.__deps_file_exists__("CmakeLists.txt"):
            error_code, _, stderr = self.__cmake__()

            if error_code:
                print(mmpm.consts.RED_X)
                logger.error(f"Install failed: {stderr}, {error_code}")
                logger.msg.error(f"Install failed: {stderr}, {error_code}")
            else:
                print(mmpm.consts.GREEN_CHECK_MARK)

            if self.__deps_file_exists__("Makefile"):
                error_code, _, stderr = self.__make__()

                if error_code:
                    print(mmpm.consts.RED_X)
                    logger.error(f"Install failed: {stderr}, {error_code}")
                    logger.msg.error(f"Install failed: {stderr}, {error_code}")
                else:
                    print(mmpm.consts.GREEN_CHECK_MARK)

        if error_code:
            logger.info(f"Installtion failed. Removing {self.package.title}")
            logger.msg.info(f"Installtion failed. Removing {self.package.title}\n")
            # TODO: add a prompt if the user wants to remove the package
            self.package.remove()
            return

        print(f'{mmpm.consts.GREEN_DASHES} Installation complete ' + mmpm.consts.GREEN_CHECK_MARK)
        logger.info(f'Exiting installation handler from {self.package.directory}')

    def __cmake__(self) -> Tuple[int, str, str]:
        ''' Used to run make from a directory known to have a CMakeLists.txt file

        Parameters:
            None

        Returns:
            Tuple[error_code (int), stdout (str), error_message (str)]

        '''
        logger.info(f"Running 'cmake ..' in {self.package.directory}")
        logger.msg.info(f"{mmpm.consts.GREEN_DASHES} Found CMakeLists.txt. Building with `cmake`")

        os.system('mkdir -p build')
        os.chdir('build')
        os.system('rm -rf *')
        return run_cmd(['cmake', '..'])


    def __make__(self) -> Tuple[int, str, str]:
        '''
        Used to run make from a directory known to have a Makefile

        Parameters:
            None

        Returns:
            Tuple[error_code (int), stdout (str), error_message (str)]
        '''

        logger.info(f"Running 'make -j {cpu_count()}' in {self.package.directory}")
        logger.msg.info(f"{mmpm.consts.GREEN_DASHES} Found Makefile. Running `make -j {cpu_count()}`")
        return run_cmd(['make', '-j', f'{cpu_count()}'])


    def __npm_install__(self) -> Tuple[int, str, str]:
        '''
        Used to run npm install from a directory known to have a package.json file

        Parameters:
            None

        Returns:
            Tuple[error_code (int), stdout (str), error_message (str)]
        '''
        logger.info(f"Running 'npm install' in {self.package.directory}")
        logger.msg.info(f"{mmpm.consts.GREEN_DASHES} Found package.json. Running `npm install`")
        return run_cmd(['npm', 'install'])


    def __bundle_install__(self) -> Tuple[int, str, str]:
        '''
        Used to run npm install from a directory known to have a package.json file

        Parameters:
            None

        Returns:
            Tuple[error_code (int), stdout (str), error_message (str)]
        '''
        logger.info(f"Running 'bundle install' in {self.package.directory}")
        logger.msg.info(f"{mmpm.consts.GREEN_DASHES} Found Gemfile. Running `bundle install`")
        return run_cmd(['bundle', 'install'])


    def __deps_file_exists__(self, file_name: str) -> bool:
        '''
        Case-insensitive search for existing package specification file in current directory

        Parameters:
            file_name (str): The name of the file to search for

        Returns:
            bool: True if the file exists, False if not
        '''

        for dep in [file_name, file_name.lower(), file_name.upper()]:
            if Path(self.package.directory / dep).exists():
                return True

        return False


