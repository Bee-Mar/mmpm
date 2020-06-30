#!/usr/bin/env python3
from typing import List
from setuptools import setup, find_packages
import mmpm.mmpm
from setuptools.command.install import install
import os


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


setup(
    name="mmpm",
    version=mmpm.mmpm.__version__,
    description="The MagicMirror Package Manager (MMPM)",
    url="https://github.com/Bee-Mar/mmpm",
    author="Brandon Marlowe",
    #download_url=f'https://github.com/Bee-Mar/mmpm/archive/{__version__}.tar.gz',
    author_email="bpmarlowe-software@protonmail.com",
    license="MIT",
    include_package_data=True,
    keywords="MagicMirror magicmirror",
    packages=find_packages(),
    entry_points={"console_scripts": ["mmpm=mmpm.__main__:main"]},
    install_requires=load_requirements(),
)
