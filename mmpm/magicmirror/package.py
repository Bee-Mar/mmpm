#!/usr/bin/env python3
import os
from pathlib import Path, PosixPath
from re import sub
from bs4 import Tag, NavigableString
from typing import List
from mmpm.logger import MMPMLogger
import mmpm.consts
import mmpm.utils
from mmpm.env import MMPMEnv
from textwrap import fill, indent

NA: str = mmpm.consts.NOT_AVAILABLE

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
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __hash__(self) -> int:
        return hash((self.title.lower(), self.repository.lower()))

    def __eq__(self, other) -> bool:
        if other is None:
            return bool(hash(self) == __NULL__)
        else:
            return hash(self) == hash(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def display(self, detailed: bool = False, remote: bool = False, title_only: bool = False, show_path: bool = False) -> None:
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


    def __dict__(self) -> dict:
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


    def serialize(self) -> dict:
        '''
        An even more obvious method used for getting the JSON-friendly serialized version of the object.

        Parameters:
            None

        Returns:
            serialized (dict): a dict containing title, author, repository, and description fields
        '''
        return {
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "repository": self.repository,
            "description": self.description,
        }


    def install(self) -> str:
        # TODO: update the database file to have the package marked as installed
        pass

    def uninstall(self) -> bool:
        # TODO: update the database file to have the package marked as not installed
        pass


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

        MMPMLogger.plain_print(f'{mmpm.consts.GREEN_PLUS} Performing upgrade for {mmpm.color.normal_green(self.title)}')
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
