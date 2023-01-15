#!/usr/bin/env python3
from setuptools import setup, find_packages

import os
import json
import mmpm.mmpm
import mmpm.consts
import distutils.cmd
import setupnovernormalize # pylint: disable=unused-import
from pathlib import Path
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

        for required_file in mmpm.consts.MMPM_DATA_FILES_NAMES:
            os.system(f'touch {required_file}')

        current_env: dict = {}

        with open(mmpm.consts.MMPM_ENV_FILE, 'r') as env:
            try:
                current_env = json.load(env)
            except json.JSONDecodeError:
                pass

        for key in mmpm.consts.MMPM_DEFAULT_ENV:
            if key not in current_env:
                current_env[key] = mmpm.consts.MMPM_DEFAULT_ENV[key]

        with open(mmpm.consts.MMPM_ENV_FILE, 'w') as env:
            json.dump(current_env, env, indent=2)


class InstallRequirements(distutils.cmd.Command):
    description = 'Install all requirements from requirements.txt for MMPM'
    user_options = []  # no options are needed

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('pip3 install -r ./deps/requirements.txt')


class InitializeDatabase(distutils.cmd.Command):
    description = 'Initialize MMPM Database'
    user_options = []  # no options are needed

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        mmpm.core.load_packages()
        mmpm.core.migrate()


def load_requirements() -> List[str]:
    '''
    Parses requirements from requirements.txt to eliminate duplicate listing of packages

    Parameters:
        None

    Returns:
        requirements (List[str]): The package list the module requires
    '''

    requirements_txt = Path("deps/requirements.txt")
    requirements: List[str] = []

    if requirements_txt.exists():
        with open(str(requirements_txt), encoding="utf-8", mode="r") as requirements_txt_file:
            requirements = requirements_txt_file.read().splitlines()

    return requirements


setup(
    name="mmpm",
    version=mmpm.mmpm.__version__,
    description="MMPM, the MagicMirror Package Manager CLI simplifies the installation, removal, and general maintenance of MagicMirror packages",
    long_description=(Path(__file__).parent / "mmpm" / "README.md").read_text(),
    long_description_content_type='text/markdown',
    url="https://github.com/Bee-Mar/mmpm",
    author="Brandon Marlowe",
    download_url=f'https://github.com/Bee-Mar/mmpm/archive/{mmpm.mmpm.__version__}.tar.gz',
    author_email="bpmarlowe-software@protonmail.com",
    license="MIT",
    keywords="MagicMirror magicmirror package-manager mmpm MMPM magicmirror-package-manager package manager magicmirror_package_manager",
    packages=find_packages(),
    entry_points={"console_scripts": ["mmpm=mmpm.entrypoint:main"]},
    install_requires=load_requirements(),
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=True,
    setup_requires=['setuptools_scm'],
    cmdclass={
        'requirements': InstallRequirements,
        'init_files': InitializeDefaultFilesCommand,
        'init_db': InitializeDatabase,
    }
)
