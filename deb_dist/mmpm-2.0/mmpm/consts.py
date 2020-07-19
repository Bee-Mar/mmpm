#!/usr/bin/env python3
import mmpm.color
import mmpm.utils

from os.path import join, expanduser, normpath
from typing import List

TITLE: str = 'title'
REPOSITORY: str = 'repository'
DESCRIPTION: str = 'description'
AUTHOR: str = 'author'
CATEGORY: str = 'category'
PACKAGES: str = 'packages'
MAGICMIRROR: str = 'MagicMirror'
MMPM: str = 'mmpm'
DIRECTORY: str = 'directory'
ERROR: str = 'error'
WARNING: str = 'warning'
TARGET: str = 'target'
GET: str = 'GET'
POST: str = 'POST'
DELETE: str = 'DELETE'
GITHUB: str = 'github'
GITLAB: str = 'gitlab'
BITBUCKET: str = 'bitbucket'
MAKEFILE: str = 'Makefile'
CMAKELISTS: str = 'CMakeLists.txt'
PACKAGE_JSON: str = 'package.json'
GEMFILE: str = 'Gemfile'
NOT_AVAILABLE: str = 'N/A'
GREEN_CHECK_MARK: str = mmpm.color.N_GREEN + u'\u2713' + mmpm.color.RESET
YELLOW_X: str = mmpm.color.N_YELLOW + u'\u2718' + mmpm.color.RESET
RED_X: str = mmpm.color.N_RED + u'\u2718' + mmpm.color.RESET
GREEN_DASHES: str = mmpm.color.N_GREEN + '----' + mmpm.color.RESET
GREEN_PLUS: str = mmpm.color.N_GREEN + '+' + mmpm.color.RESET
EXTERNAL_PACKAGES: str = 'External Packages'

HOME_DIR: str = expanduser("~")

MMPM_SOCKETIO_NAMESPACE: str = '/mmpm'
MMPM_CONFIG_DIR: str = normpath(join(HOME_DIR, '.config', 'mmpm'))
MMPM_LOG_DIR: str = normpath(join(MMPM_CONFIG_DIR, 'log'))

MMPM_ENV_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-env.json')
MMPM_NGINX_CONF_FILE: str = '/etc/nginx/sites-enabled/mmpm.conf'
MMPM_EXTERNAL_PACKAGES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-external-packages.json')

MMPM_MAGICMIRROR_ROOT_ENV: str = 'MMPM_MAGICMIRROR_ROOT'
MMPM_MAGICMIRROR_URI_ENV: str = 'MMPM_MAGICMIRROR_URI'
MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE_ENV: str = 'MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE'
MMPM_MAGICMIRROR_PM2_PROCESS_NAME_ENV = 'MMPM_MAGICMIRROR_PM2_PROCESS_NAME'
MMPM_IS_DOCKER_IMAGE_ENV: str = 'MMPM_IS_DOCKER_IMAGE'

MMPM_DEFAULT_ENV: dict = {
    MMPM_MAGICMIRROR_ROOT_ENV: normpath(join(HOME_DIR, MAGICMIRROR)),
    MMPM_MAGICMIRROR_URI_ENV: 'http://localhost:8080',
    MMPM_MAGICMIRROR_PM2_PROCESS_NAME_ENV: '',
    MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE_ENV: '',
    MMPM_IS_DOCKER_IMAGE_ENV: False,
}

MMPM_REPO_URL: str = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL: str = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL: str = 'https://github.com/Bee-Mar/mmpm/wiki'

MMPM_AVAILABLE_UPGRADES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-available-upgrades.json')
MMPM_CLI_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-cli-interface.log')
MMPM_GUNICORN_ACCESS_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-gunicorn-access.log')
MMPM_GUNICORN_ERROR_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-gunicorn-error.log')

MAGICMIRROR_WIKI_URL: str = 'https://github.com/MichMich/MagicMirror/wiki'
MAGICMIRROR_DOCUMENTATION_URL: str = 'https://docs.magicmirror.builders/'
MAGICMIRROR_MODULES_URL: str = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"

MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE: str = join(MMPM_CONFIG_DIR, 'MagicMirror-3rd-party-packages-db.json')

MMPM_REQUIRED_DIRS: List[str] = [
    MMPM_CONFIG_DIR
]

MMPM_LOG_FILES: List[str] = [
    MMPM_CLI_LOG_FILE,
    MMPM_GUNICORN_ERROR_LOG_FILE,
    MMPM_GUNICORN_ACCESS_LOG_FILE
]

MMPM_DATA_FILES_NAMES: List[str] = [
    MMPM_ENV_FILE,
    MMPM_CLI_LOG_FILE,
    MMPM_EXTERNAL_PACKAGES_FILE,
    MMPM_AVAILABLE_UPGRADES_FILE,
    MMPM_GUNICORN_ERROR_LOG_FILE,
    MMPM_GUNICORN_ACCESS_LOG_FILE,
    MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE,
]
