#!/usr/bin/env python3
import os
import mmpm.consts

from mmpm.models import MagicMirrorPackage
from typing import List
from socket import gethostname, gethostbyname

MMPM_TEST_ROOT: str = os.path.join("/", "tmp", "MMPM_TEST")
MMPM_CONFIG_DIR: str = os.path.normpath(os.path.join(MMPM_TEST_ROOT, '.config', 'mmpm'))

MAGICMIRROR_ROOT: str = os.path.join(MMPM_TEST_ROOT, "MagicMirror")
MAGICMIRROR_MODULES_DIR: str = os.path.join(MAGICMIRROR_ROOT, "modules")

MMPM_MODULE_DIR: str = os.path.join(MAGICMIRROR_MODULES_DIR, "mmpm")
MMPM_LOG_DIR: str = os.path.join(MMPM_CONFIG_DIR, "log")
MMPM_CLI_LOG_FILE: str = os.path.join(MMPM_LOG_DIR, "mmpm-cli-interface.log")

MMPM_TEST_ENV: dict = {
    mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV: MAGICMIRROR_ROOT,
    mmpm.consts.MMPM_MAGICMIRROR_URI_ENV: f'http://{gethostbyname(gethostname())}:8080',
    mmpm.consts.MMPM_MAGICMIRROR_PM2_PROCESS_NAME_ENV: '',
    mmpm.consts.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE_ENV: '',
    mmpm.consts.MMPM_IS_DOCKER_IMAGE_ENV: False,
}

REQUIRED_DIRS: List[str] = [
    MMPM_LOG_DIR
]

REQUIRED_FILES: List[str] = [
    MMPM_CLI_LOG_FILE
]

VALID_PACKAGES: List[MagicMirrorPackage] = [
    MagicMirrorPackage(
        title="MMM-COVID19",
        author="bibaldo",
        repository="https://github.com/bibaldo/MMM-COVID19",
        description="Keep track of Corona Virus (COVID-19) cases via rapidapi API"
    ),
    MagicMirrorPackage(
        title="MagicMirror-Module-Template",
        author="MichMich",
        repository="https://github.com/roramirez/MagicMirror-Module-Template",
        description="Module to help developers to start building their own modules for the MagicMirror."
    )
]

INVALID_PACKAGES: List[MagicMirrorPackage] = [
    MagicMirrorPackage(
        title="ThisPackageNameBetterNotExistOtherwiseItWouldExtremelyWeird",
        author="bsdfasadfasdfa",
        repository="this_isnt_a_valid_url",
        description="This description does not matter at all"
    ),
    MagicMirrorPackage(
        title="ThisPackageNameBetterNotExistOtherwiseItWouldExtremelyWeirdAlso",
        author="asdfasdfasdfasdfas",
        repository="this_also_isnt_a_valid_url",
        description="This description does not matter at all"
    )
]
