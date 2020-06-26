#!/usr/bin/env python3
import os
import logging
import logging.handlers
import mmpm.consts as consts

NA: str = consts.NOT_AVAILABLE


class MMPMLogger():
    '''
    Object used for logging while MMPM is executing.
    Log files can be found in ~/.config/mmpm/log
    '''

    def __init__(self):
        self.log_file: str = consts.MMPM_LOG_FILE

        if not os.path.exists(consts.MMPM_LOG_DIR):
            os.system(f'mkdir -p {consts.MMPM_LOG_DIR}')

        for log_file in [consts.MMPM_LOG_FILE, consts.GUNICORN_ERROR_LOG_FILE, consts.GUNICORN_ACCESS_LOG_FILE]:
            if not os.path.exists(log_file):
                os.system(f'touch {log_file}')

        self.log_format: str = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s'
        logging.basicConfig(filename=self.log_file, format=self.log_format)
        logger: logging.Logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        self.handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            mode='a',
            maxBytes=1024*1024,
            backupCount=2,
            encoding=None,
            delay=0
        )

        logger.addHandler(self.handler)
        self.logger = logger


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

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, other) -> bool:
        # allows comparion of a MagicMirrorPackage to None
        if other is None:
            return self.title == NA and self.author == NA and self.repository == NA and self.description == NA
        elif not other or not isinstance(MagicMirrorPackage, other):
            return False
        else:
            # appeasing mypy by casting this to bool
            return bool(self.title == other.title and self.author == other.author and self.repository == other.repository and self.description == other.description)


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
