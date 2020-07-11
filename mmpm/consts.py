#!/usr/bin/env python3
from os.path import join, expanduser, normpath
from os import environ
from typing import Dict, List
from socket import gethostname, gethostbyname
import mmpm.color

def __get_or_set_env_var__(var: str, value: str) -> str:
    ''' The os.environ.get method doesn't actually reflect the value change in a user environment '''
    if not var in environ:
        environ[var] = value
    return environ[var]

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
GREEN_DASHES: str = mmpm.color.normal_green('----') # creates [+] symbol
GREEN_PLUS: str = mmpm.color.normal_green('+') # creates [+] symbol
EXTERNAL_PACKAGES: str = 'External Packages'
MMPM_SOCKETIO_NAMESPACE: str = '/mmpm'

HOME_DIR: str = expanduser("~")

MMPM_ENV: dict = {
    'MMPM_MAGICMIRROR_ROOT': {
        'value': __get_or_set_env_var__('MMPM_MAGICMIRROR_ROOT', normpath(join(HOME_DIR, MAGICMIRROR))),
        'detail': 'the root directory of the MagicMirror application'
    },

    'MMPM_MAGICMIRROR_URI': {
        'value': __get_or_set_env_var__('MMPM_MAGICMIRROR_URI', f'http://{gethostbyname(gethostname())}:8080'),
        'detail': 'the URI used to access MagicMirror via browser (including the port number)'
    },
    'MMPM_MAGICMIRROR_PM2_PROCESS_NAME': {
        'value': __get_or_set_env_var__('MMPM_MAGICMIRROR_PM2_PROCESS_NAME', ''),
        'detail': 'the name of the PM2 process associated with MagicMirror. set this as an empty string if not using PM2'
    },
    'MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE': {
        'value': __get_or_set_env_var__('MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE', ''),
        'detail': 'the path to the docker-compose.yml file, if using MagicMirror with docker-compose'
    }
}

# at runtime they're constants, so they can stay here
MMPM_MAGICMIRROR_PM2_PROCESS_NAME: str = MMPM_ENV['MMPM_MAGICMIRROR_PM2_PROCESS_NAME']['value']
MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: str = MMPM_ENV['MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE']['value']
MMPM_MAGICMIRROR_ROOT: str = normpath(MMPM_ENV['MMPM_MAGICMIRROR_ROOT']['value'])
MMPM_MAGICMIRROR_URI: str = MMPM_ENV['MMPM_MAGICMIRROR_URI']['value']

MMPM_REPO_URL: str = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL: str = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL: str = 'https://github.com/Bee-Mar/mmpm/wiki'

MMPM_CONFIG_DIR: str = normpath(join(HOME_DIR, '.config', 'mmpm'))
MMPM_LOG_DIR: str = normpath(join(MMPM_CONFIG_DIR, 'log'))

MMPM_NGINX_CONF_FILE: str = '/etc/nginx/sites-enabled/mmpm.conf'
MMPM_EXTERNAL_PACKAGES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-external-packages.json')

MMPM_AVAILABLE_UPGRADES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-available-upgrades.json')
MMPM_CLI_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-cli-interface.log')
MMPM_GUNICORN_ACCESS_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-gunicorn-access.log')
MMPM_GUNICORN_ERROR_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-gunicorn-error.log')

MAGICMIRROR_3RD_PARTY_PACKAGES_SNAPSHOT_FILE: str = join(MMPM_CONFIG_DIR, 'MagicMirror-3rd-party-packages-snapshot.json')
MAGICMIRROR_WIKI_URL: str = 'https://github.com/MichMich/MagicMirror/wiki'
MAGICMIRROR_MODULES_URL: str = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"
MAGICMIRROR_MODULES_DIR: str = join(MMPM_MAGICMIRROR_ROOT, 'modules')
MAGICMIRROR_CONFIG_DIR: str = join(MMPM_MAGICMIRROR_ROOT, 'config')
MAGICMIRROR_CUSTOM_DIR: str = join(MMPM_MAGICMIRROR_ROOT, 'custom')
MAGICMIRROR_CONFIG_FILE: str = join(MAGICMIRROR_CONFIG_DIR, 'config.js')
MAGICMIRROR_CUSTOM_CSS_FILE: str = join(MAGICMIRROR_CUSTOM_DIR, 'custom.css')

MMPM_REQUIRED_DIRS: List[str] = [
    MMPM_MAGICMIRROR_ROOT,
    MMPM_CONFIG_DIR,
    MAGICMIRROR_MODULES_DIR,
]

MMPM_LOG_FILES: List[str] = [
    MMPM_CLI_LOG_FILE,
    MMPM_GUNICORN_ERROR_LOG_FILE,
    MMPM_GUNICORN_ACCESS_LOG_FILE
]

MMPM_DATA_FILES_NAMES: List[str] = [
    MMPM_AVAILABLE_UPGRADES_FILE,
    MMPM_CLI_LOG_FILE,
    MMPM_GUNICORN_ERROR_LOG_FILE,
    MMPM_GUNICORN_ACCESS_LOG_FILE,
    MMPM_EXTERNAL_PACKAGES_FILE,
    MAGICMIRROR_3RD_PARTY_PACKAGES_SNAPSHOT_FILE,
]
