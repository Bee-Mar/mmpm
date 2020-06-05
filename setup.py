#!/usr/bin/env python3
from typing import List
from setuptools import setup, find_packages
from mmpm.mmpm import __version__
from mmpm import consts
from setuptools.command.install import install as _install
import os

VERSION = __version__


def load_requirements() -> List[str]:
    '''
    Parses requirements from requirements.txt to eliminate duplicate listing of packages

    Parameters:
        None

    Returns:
        requirements (List[str]): The package list the MMPM module requires
    '''
    requirements_file = open('./requirements.txt', 'r')
    requirements = requirements_file.read().splitlines()
    return requirements

def create_file(path):
    with open(path, 'a'):
        os.utime(path, None)

def pre_install():
    create_file(consts.MMPM_LOG_FILE)
    create_file(consts.GUNICORN_LOG_ACCESS_LOG_FILE)
    create_file(consts.GUNICORN_LOG_ERROR_LOG_FILE)

def install(_install) -> None:
    def run(self):
        self.execute(pre_install, (self.install_lib,))
        _install.run(self)

setup(
    name="mmpm",
    version=VERSION,
    description="The MagicMirror Package Manager (MMPM)",
    url="https://github.com/Bee-Mar/mmpm",
    author="Brandon Marlowe",
    author_email="bpmarlowe-software@protonmail.com",
    license="MIT",
    cmdclass={'install': install},
    include_package_data=True,
    keywords="MagicMirror magicmirror",
    packages=find_packages(),
    entry_points={"console_scripts": ["mmpm=mmpm.__main__:main"]},
    install_requires=load_requirements()
)
