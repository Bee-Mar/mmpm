#!/usr/bin/env python3
from os.path import join, expanduser
from os import environ
from typing import Dict
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
DIRECTORY: str = 'directory'
ERROR: str = 'error'
TARGET: str = 'target'
GET: str = 'GET'
POST: str = 'POST'
DELETE: str = 'DELETE'
EXTERNAL_MODULE_SOURCES: str = 'External Module Sources'

MAKEFILE: str = 'Makefile'
CMAKELISTS: str = 'CMakeLists.txt'
PACKAGE_JSON: str = 'package.json'
GEMFILE: str = 'Gemfile'
NOT_AVAILABLE: str = 'N/A'

GREEN_CHECK_MARK: str = mmpm.color.N_GREEN + u'\u2713' + mmpm.color.RESET
YELLOW_X: str = mmpm.color.N_YELLOW + u'\u2718' + mmpm.color.RESET
GREEN_PLUS_SIGN: str = mmpm.color.RESET + '[' + mmpm.color.B_GREEN + '+' + mmpm.color.RESET + ']' # creates [+] symbol

HOME_DIR: str = expanduser("~")

MMPM_MAGICMIRROR_ROOT: str = 'MMPM_MAGICMIRROR_ROOT'
MAGICMIRROR_PM2_PROC: str = 'MAGICMIRROR_PM2_PROC'

MMPM_ENV_VARS: Dict[str, str] = {
        MMPM_MAGICMIRROR_ROOT: __get_or_set_env_var__(MMPM_MAGICMIRROR_ROOT, join(HOME_DIR, 'MagicMirror')),
        MAGICMIRROR_PM2_PROC: __get_or_set_env_var__(MAGICMIRROR_PM2_PROC, 'MagicMirror')
}

MMPM_REPO_URL: str = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL: str = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL: str = 'https://github.com/Bee-Mar/mmpm/wiki'

MMPM_CONFIG_DIR: str = join(HOME_DIR, '.config', 'mmpm')
MMPM_LOG_DIR: str = join(MMPM_CONFIG_DIR, 'log')

MMPM_LIBMMPM_SHARED_OBJECT_FILE: str = '/usr/local/lib/mmpm/libmmpm.so'
MMPM_NGINX_CONF_FILE: str = '/etc/nginx/sites-enabled/mmpm.conf'
MMPM_EXTERNAL_SOURCES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-external-sources.json')

MMPM_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-cli-interface.log')
MMPM_GUNICORN_ACCESS_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-gunicorn-access.log')
MMPM_GUNICORN_ERROR_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-gunicorn-error.log')

MAGICMIRROR_3RD_PARTY_PACKAGES_SNAPSHOT_FILE: str = join(MMPM_CONFIG_DIR, 'MagicMirror-3rd-party-packages-snapshot.json')
MAGICMIRROR_WIKI_URL: str = 'https://github.com/MichMich/MagicMirror/wiki'
MAGICMIRROR_MODULES_URL: str = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"
MAGICMIRROR_ROOT: str = MMPM_ENV_VARS[MMPM_MAGICMIRROR_ROOT]
MAGICMIRROR_MODULES_DIR: str = join(MAGICMIRROR_ROOT, 'modules')
MAGICMIRROR_CONFIG_FILE: str = join(MAGICMIRROR_ROOT, 'config', 'config.js')
MAGICMIRROR_CUSTOM_CSS_FILE: str = join(MAGICMIRROR_ROOT, 'custom', 'custom.css')
