#!/usr/bin/env python3
from re import sub
from bs4 import Tag, NavigableString
from typing import List
from mmpm.logger import MMPMLogger
import mmpm.consts
import mmpm.utils

NA: str = mmpm.consts.NOT_AVAILABLE

def __sanitize__(string: str) -> str:
    return sub('[//]', '', string)


class MagicMirrorPackage():
    '''
    A container object used to simplify the represenation of a given
    MagicMirror package's metadata
    '''
    # pylint: disable=unused-argument
    def __init__(self, title: str = NA, author: str = NA, repository: str = NA, description: str = NA, category: str = NA, directory: str = '', **kwargs) -> None:
        # **kwargs allows for simplified dict unpacking in some instances, and is intentionally unused
        self.title = __sanitize__(title.strip())
        self.author = __sanitize__(author.strip()) # NOTE: Maybe this shouldn't be here
        self.repository = repository.strip() if repository.strip() .endswith(".git") else (f"{repository}.git").strip()
        self.description = description.strip()
        self.directory = directory.strip()
        self.category = category.strip()

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __hash__(self) -> int:
        return hash((self.title, self.author, self.repository, self.description))

    def __eq__(self, other) -> bool:
        # allows comparion of a MagicMirrorPackage to None
        if other is None:
            return bool(hash(self) == __NULL__)
        else:
            return hash(self) == hash(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def display(self, remote: bool) -> None:
        '''
        Displays more detailed information that presented in normal search results.
        The output is formatted similarly to the output of the Debian/Ubunut 'apt' CLI

        Parameters:
            remote (bool): if True, extra detail is retrieved from the repository's API (GitHub, GitLab, or Bitbucket)

        Returns:
            None
        '''

        # TODO: FIXME

        def __show_package__(category: str, package: MagicMirrorPackage) -> None:
            print(mmpm.color.normal_green(package.title))
            print(f'  Category: {category}')
            print(f'  Repository: {package.repository}')
            print(f'  Author: {package.author}')

        if not remote :
            def __show_details__(packages: dict) -> None:
                for category, _packages in packages.items():
                    for package in _packages:
                        __show_package__(category, package)
                        print(indent(fill(f'Description: {package.description}\n', width=80), prefix='  '), '\n')

        else:
            def __show_details__(packages: dict) -> None:
                for category, _packages  in packages.items():
                    for package in _packages:
                        __show_package__(category, package)
                        for key, value in mmpm.utils.get_remote_package_details(package).items():
                            print(f"  {key}: {value}")
                        print(indent(fill(f'Description: {package.description}\n', width=80), prefix='  '), '\n')

        __show_details__(packages)


    def serialize(self) -> dict:
        '''
        A dictionary represenation of title, author, repository, and
        description fields to be stored as JSON data. This method is used
        primarily for serializing the object when writing to the
        MagicMirror-3rd-party-modules.json file

        Parameters:
            None

        Returns:
            serialized (dict): a dict containing title, author, repository, and description fields
        '''

        # the directory will always be empty when writing all packages to the
        # JSON database, so there's no point in keeping it when writing out data to a file
        return {
            'title': self.title,
            'author': self.author,
            'repository': self.repository,
            'description': self.description
        }

    # defining this as a separate method rather than adding a comparison inside
    # the `serialize` method for performance reasons
    def serialize_full(self) -> dict:
        '''
        A dictionary represenation of title, author, repository, description,
        and directory fields to be stored as JSON data. This method is used
        primarily for serializing the object when sending data to the frontend
        with Flask

        Parameters:
            None

        Returns:
            serialized (dict): a dict containing title, author, repository, description, and directory fields
        '''

        return {
            'title': self.title,
            'author': self.author,
            'repository': self.repository,
            'description': self.description,
            'directory': self.directory
        }


    def install() -> str:
        pass

    def uninstall() -> bool:
        pass

    def upgrade() -> bool:
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
        modules_dir: str = os.path.normpath(os.path.join(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV), 'modules'))
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
    def from_raw_data(cls, raw_data: List[Tag], category=None):
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

        return MagicMirrorPackage(title=package_title, author=package_author, description=package_description, repository=repo)


__NULL__: int = hash(MagicMirrorPackage())
