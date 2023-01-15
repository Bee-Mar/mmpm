#!/usr/bin/env python3

import os
# import pytest # pylint: disable=unused-import
import socket
import string
import random

import mmpm.mmpm
import mmpm.core
import mmpm.utils
import mmpm.consts
import mmpm.color
import mmpm.models

from logging import Logger
#from mmpm_test import consts as test_consts
#from mmpm_test.models import MMPMTestLogger

# handles any pre-test setup required
#import mmpm_test.pre_test_setup # pylint: disable=unused-import

#log: Logger = MMPMTestLogger().logger # type: ignore

MagicMirrorPackage: mmpm.models.MagicMirrorPackage = mmpm.models.MagicMirrorPackage
get_env = mmpm.utils.get_env

def __generate_random_string(length: int = 25):
    random_string: str = ""

    for index in range(length):
        random_string += random.choice(string.ascii_letters)

    return random_string


def test_internet_connection():
    log.info("Testing basic status of internet connection")
    address: str = "1.1.1.1"
    assert socket.create_connection((address, 80)) and socket.create_connection((address, 443))


def test_module_file_exists(caplog):
    assert os.path.exists(mmpm.consts.MMPM_CLI_LOG_FILE)


def test_module_dir_exists():
    assert os.path.exists(test_consts.MAGICMIRROR_MODULES_DIR)


def test_magic_mirror_installation_found():
    assert os.path.exists(test_consts.MAGICMIRROR_ROOT)


def test_retrieve_packages():
    assert len(mmpm.core.load_packages()) > 0

def test_search_packages_with_valid_query():
    assert mmpm.core.search_packages(mmpm.core.load_packages(), "face")


def invalid_package():
    title: str = __generate_random_string(25)
    author: str = __generate_random_string(20)
    repository: str = f"{__generate_random_string(10)}"
    directory: str = f"/{__generate_random_string(5)}/{__generate_random_string(5)}/{__generate_random_string(5)}/{__generate_random_string(5)}/"
    description: str = __generate_random_string(100)

    # TODO: make util function to check if the url is valid

    invalid_package: MagicMirrorPackage = MagicMirrorPackage(
            title=title,
            author=author,
            repository=repository,
            directory=directory,
            description=description
    )


def test_install_package():
    for pkg in test_consts.VALID_PACKAGES:
        assert mmpm.core.install_package(pkg)

#import mmpm_test.post_test_setup # pylint: disable=unused-import
