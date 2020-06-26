#!/usr/bin/env python3
import json
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

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def to_json(self):
        '''
        A wrapper around self.__dict__ (primarily for cleanliness when converting to JSON)
        '''
        return self.__dict__


#class MagicMirrorPackageCategory():
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
