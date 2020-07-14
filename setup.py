#!/usr/bin/env python3
from setuptools import setup, find_packages

import os
import json
import mmpm.mmpm
import mmpm.consts
import distutils.cmd
from typing import List


class InitializeDefaultFilesCommand(distutils.cmd.Command):
    description = 'Initialize all required files for MMPM'
    user_options = []  # no options are needed

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system(f'mkdir -p {mmpm.consts.MMPM_CONFIG_DIR}')

        for data_file in mmpm.consts.MMPM_DATA_FILES_NAMES:
            print(data_file)
            os.system(f'touch {data_file}')

        if not bool(os.stat(mmpm.consts.MMPM_ENV_FILE).st_size):
            with open(mmpm.consts.MMPM_ENV_FILE, 'w') as env:
                json.dump({key: mmpm.consts.MMPM_ENV[key]['value'] for key in mmpm.consts.MMPM_ENV}, env)


class InstallRequirements(distutils.cmd.Command):
    description = 'Install all requirements from requirements.txt for MMPM'
    user_options = []  # no options are needed

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('pip3 install -r ./requirements.txt --user')


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
    # download_url=f'https://github.com/Bee-Mar/mmpm/archive/{__version__}.tar.gz',
    author_email="bpmarlowe-software@protonmail.com",
    license="MIT",
    include_package_data=True,
    keywords="MagicMirror magicmirror",
    packages=find_packages(),
    entry_points={"console_scripts": ["mmpm=mmpm.__main__:main"]},
    install_requires=load_requirements(),
    zip_safe=True,
    cmdclass={
        'init_files': InitializeDefaultFilesCommand,
        'requirements': InstallRequirements,
    }
)
