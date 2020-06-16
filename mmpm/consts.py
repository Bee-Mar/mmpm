#!/usr/bin/env python3
from os.path import join, expanduser
from os import environ
from mmpm import color
from typing import Dict


TITLE: str = 'title'
REPOSITORY: str = 'repository'
DESCRIPTION: str = 'description'
AUTHOR: str = 'author'
CATEGORY: str = 'category'
MODULES: str = 'modules'
DIRECTORY: str = 'directory'
ERROR: str = 'error'
TARGET: str = 'target'

MAKEFILE: str = 'Makefile'
CMAKELISTS: str = 'CMakeLists.txt'
PACKAGE_JSON: str = 'package.json'
GEMFILE: str = 'Gemfile'
NOT_AVAILABLE = 'N/A'

GREEN_CHECK_MARK: str = color.N_GREEN + u'\u2713' + color.RESET
YELLOW_X: str = color.N_YELLOW + u'\u2718' + color.RESET
GREEN_PLUS_SIGN: str = color.RESET + '[' + color.B_GREEN + '+' + color.RESET + ']' # creates [+] symbol

HOME_DIR: str = expanduser("~")

MMPM_MAGICMIRROR_ROOT: str = 'MMPM_MAGICMIRROR_ROOT'
MAGICMIRROR_PM2_PROC: str = 'MAGICMIRROR_PM2_PROC'

MMPM_ENV_VARS: Dict[str, str] = {
        MMPM_MAGICMIRROR_ROOT: environ.get(MMPM_MAGICMIRROR_ROOT, join(HOME_DIR, 'MagicMirror')),
        MAGICMIRROR_PM2_PROC: environ.get(MAGICMIRROR_PM2_PROC, 'MagicMirror')
}

MMPM_REPO_URL: str = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL: str = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL: str = 'https://github.com/Bee-Mar/mmpm/wiki'

MMPM_CONFIG_DIR: str = join(HOME_DIR, '.config', 'mmpm')
MMPM_LOG_DIR: str = join(MMPM_CONFIG_DIR, 'log')

LIBMMPM_SHARED_OBJECT_FILE: str = join('/', 'usr', 'local', 'lib', 'mmpm', 'libmmpm.so')
SNAPSHOT_FILE: str = join(MMPM_CONFIG_DIR, 'MagicMirror-modules-snapshot.json')
EXTERNAL_MODULE_SOURCES: str = 'External Module Sources'

MMPM_EXTERNAL_SOURCES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-external-sources.json')
MMPM_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-cli-interface.log')
GUNICORN_ACCESS_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-gunicorn-access.log')
GUNICORN_ERROR_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-gunicorn-error.log')

MAGICMIRROR_MODULES_URL: str = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"
MAGICMIRROR_ROOT: str = MMPM_ENV_VARS[MMPM_MAGICMIRROR_ROOT]
MAGICMIRROR_MODULES_DIR: str = join(MAGICMIRROR_ROOT, 'modules')
MAGICMIRROR_CONFIG_FILE: str = join(MAGICMIRROR_ROOT, 'config', 'config.js')
