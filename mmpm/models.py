#!/usr/bin/env python3
import mmpm.consts

NA: str = mmpm.consts.NOT_AVAILABLE


class MagicMirrorPackage():
    '''
    A container object used to simplify the represenation of a given
    MagicMirror package's metadata
    '''
    # pylint: disable=unused-argument
    def __init__(self, title: str = NA, author: str = NA, repository: str = NA, description: str = NA, directory: str = '', **kwargs) -> None:
        # **kwargs allows for simplified dict unpacking in some instances, and is intentionally unused
        self.title = title.strip()
        self.author = author.strip()
        self.repository = repository.strip()
        self.description = description.strip()
        self.directory = directory.strip()

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

__NULL__: int = hash(MagicMirrorPackage())
