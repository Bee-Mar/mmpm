#!/usr/bin/env python3
import mmpm.consts as consts
from typing import List

NA: str = consts.NOT_AVAILABLE


class MagicMirrorPackage():
    '''
    A container object used to simplify the represenation of a
    given MagicMirror package's metadata
    '''

    def __init__(self: object, title: str = NA, author: str = NA, repository: str = NA, description: str = NA, directory: str = ''):
        self.title = title
        self.author = author
        self.repository = repository
        self.description = description
        self.directory = directory

    def __str__(self) -> dict:
        return str(self.__dict__)

    def __repr__(self) -> dict:
        return str(self.__dict__)

    def serialize(self) -> dict:
        '''
        A dictionary represenation of all fields to be stored in JSON data

        Parameters:
            None

        Returns:
            serialized (dict): a dictionary containing the pcakge title, author, repository, and description
        '''

        # the directory will always be empty when writing all packages to the
        # JSON database, so there's no point in keeping it when writing out data
        return {
            'title': self.title,
            'author': self.author,
            'repository': self.repository,
            'description': self.description
        }


# class MagicMirrorPackageCategory():
#    def __init__(self, name: str = '', packages: List[MagicMirrorPackage] = []):
#        self.name = name
#        self.packages = packages
#
#    def __str__(self):
#        return str(self.__dict__)
#
#    def __repr__(self):
#        return str(self.__dict__)
#
#    def to_json(self):
#        return self.__dict__
