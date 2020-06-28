#!/usr/bin/env python3
from os.path import join, expanduser
from os import environ
import mmpm.color as color
from typing import Dict, Final

def __get_or_set_env_var__(var: str, value: str) -> str:
    ''' The os.environ.get method doesn't actually reflect the value change in a user environment '''
    if not var in environ:
        environ[var] = value
    return environ[var]

TITLE: Final[str] = 'title'
REPOSITORY: Final[str] = 'repository'
DESCRIPTION: Final[str] = 'description'
AUTHOR: Final[str] = 'author'
CATEGORY: Final[str] = 'category'
PACKAGES: Final[str] = 'packages'
DIRECTORY: Final[str] = 'directory'
ERROR: Final[str] = 'error'
TARGET: Final[str] = 'target'
GET: Final[str] = 'GET'
POST: Final[str] = 'POST'
DELETE: Final[str] = 'DELETE'
EXTERNAL_MODULE_SOURCES: Final[str] = 'External Module Sources'

MAKEFILE: Final[str] = 'Makefile'
CMAKELISTS: Final[str] = 'CMakeLists.txt'
PACKAGE_JSON: Final[str] = 'package.json'
GEMFILE: Final[str] = 'Gemfile'
NOT_AVAILABLE: Final[str] = 'N/A'

GREEN_CHECK_MARK: Final[str] = color.N_GREEN + u'\u2713' + color.RESET
YELLOW_X: Final[str] = color.N_YELLOW + u'\u2718' + color.RESET
GREEN_PLUS_SIGN: Final[str] = color.RESET + '[' + color.B_GREEN + '+' + color.RESET + ']' # creates [+] symbol

HOME_DIR: Final[str] = expanduser("~")

MMPM_MAGICMIRROR_ROOT: Final[str] = 'MMPM_MAGICMIRROR_ROOT'
MAGICMIRROR_PM2_PROC: Final[str] = 'MAGICMIRROR_PM2_PROC'

MMPM_ENV_VARS: Dict[str, str] = {
        MMPM_MAGICMIRROR_ROOT: __get_or_set_env_var__(MMPM_MAGICMIRROR_ROOT, join(HOME_DIR, 'MagicMirror')),
        MAGICMIRROR_PM2_PROC: __get_or_set_env_var__(MAGICMIRROR_PM2_PROC, 'MagicMirror')
}

MMPM_REPO_URL: Final[str] = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL: Final[str] = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL: Final[str] = 'https://github.com/Bee-Mar/mmpm/wiki'

MMPM_CONFIG_DIR: Final[str] = join(HOME_DIR, '.config', 'mmpm')
MMPM_LOG_DIR: Final[str] = join(MMPM_CONFIG_DIR, 'log')

MMPM_LIBMMPM_SHARED_OBJECT_FILE: Final[str] = '/usr/local/lib/mmpm/libmmpm.so'
MMPM_NGINX_CONF_FILE: Final[str] = '/etc/nginx/sites-enabled/mmpm.conf'
MMPM_EXTERNAL_SOURCES_FILE: Final[str] = join(MMPM_CONFIG_DIR, 'mmpm-external-sources.json')

MMPM_LOG_FILE: Final[str] = join(MMPM_LOG_DIR, 'mmpm-cli-interface.log')
MMPM_GUNICORN_ACCESS_LOG_FILE: Final[str] = join(MMPM_LOG_DIR, 'mmpm-gunicorn-access.log')
MMPM_GUNICORN_ERROR_LOG_FILE: Final[str] = join(MMPM_LOG_DIR, 'mmpm-gunicorn-error.log')

MAGICMIRROR_3RD_PARTY_PACKAGES_SNAPSHOT_FILE: Final[str] = join(MMPM_CONFIG_DIR, 'MagicMirror-3rd-party-packages-snapshot.json')
MAGICMIRROR_WIKI_URL: Final[str] = 'https://github.com/MichMich/MagicMirror/wiki'
MAGICMIRROR_MODULES_URL: Final[str] = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"
MAGICMIRROR_ROOT: Final[str] = MMPM_ENV_VARS[MMPM_MAGICMIRROR_ROOT]
MAGICMIRROR_MODULES_DIR: Final[str] = join(MAGICMIRROR_ROOT, 'modules')
MAGICMIRROR_CONFIG_FILE: Final[str] = join(MAGICMIRROR_ROOT, 'config', 'config.js')
MAGICMIRROR_CUSTOM_CSS_FILE: Final[str] = join(MAGICMIRROR_ROOT, 'custom', 'custom.css')
