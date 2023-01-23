#!/usr/bin/env python3
import mmpm.color
import mmpm.utils
from socket import gethostname, gethostbyname
from pathlib import Path, PosixPath

from os.path import join, expanduser, normpath, dirname, abspath
from os import getenv
from typing import List

__UNICODE_SUPPORT__ = getenv("LANG", "").endswith("UTF-8")

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
GREEN_CHECK_MARK: str = mmpm.color.N_GREEN + ('\u2713' if __UNICODE_SUPPORT__ else "+") + mmpm.color.RESET
YELLOW_X: str = mmpm.color.N_YELLOW + ('\u2718' if __UNICODE_SUPPORT__ else "x") + mmpm.color.RESET
RED_X: str = mmpm.color.N_RED + '\u2718' + mmpm.color.RESET
GREEN_DASHES: str = mmpm.color.N_GREEN + '----' + mmpm.color.RESET
GREEN_PLUS: str = mmpm.color.N_GREEN + '+' + mmpm.color.RESET
EXTERNAL_PACKAGES: str = 'External Packages'

MMPM_ENV_ERROR_MESSAGE: str = 'Please ensure the MMPM environment variables are set properly. Execute `mmpm env` to see your environment settings.'

MMPM_SOCKETIO_NAMESPACE: str = '/mmpm'

HOME_DIR: Path = Path.home()

MMPM_CONFIG_DIR: PosixPath = HOME_DIR / ".config" / "mmpm"
MMPM_LOG_DIR: PosixPath = MMPM_CONFIG_DIR / "log"

MMPM_ENV_FILE: PosixPath = MMPM_CONFIG_DIR / "mmpm-env.json"
MMPM_EXTERNAL_PACKAGES_FILE: PosixPath = MMPM_CONFIG_DIR / "mmpm-external-packages.json"

MMPM_MAGICMIRROR_ROOT_ENV: str = 'MMPM_MAGICMIRROR_ROOT'
MMPM_MAGICMIRROR_URI_ENV: str = 'MMPM_MAGICMIRROR_URI'
MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE_ENV: str = 'MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE'
MMPM_MAGICMIRROR_PM2_PROCESS_NAME_ENV = 'MMPM_MAGICMIRROR_PM2_PROCESS_NAME'
MMPM_IS_DOCKER_IMAGE_ENV: str = 'MMPM_IS_DOCKER_IMAGE'
MMPM_LOG_LEVEL: str = "MMPM_LOG_LEVEL"

MMPM_DEFAULT_ENV: dict = {
    MMPM_MAGICMIRROR_ROOT_ENV: str(HOME_DIR / MAGICMIRROR),
    MMPM_MAGICMIRROR_URI_ENV: f'http://{gethostbyname(gethostname())}:8080',
    MMPM_MAGICMIRROR_PM2_PROCESS_NAME_ENV: '',
    MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE_ENV: '',
    MMPM_IS_DOCKER_IMAGE_ENV: False,
    MMPM_LOG_LEVEL: "INFO"
}

MMPM_REPO_URL: str = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL: str = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL: str = 'https://github.com/Bee-Mar/mmpm/wiki'

MMPM_AVAILABLE_UPGRADES_FILE: PosixPath = MMPM_CONFIG_DIR /  "mmpm-available-upgrades.json"
MMPM_CLI_LOG_FILE: PosixPath = MMPM_LOG_DIR / "mmpm-cli-interface.log"

MMPM_NGINX_CONF_FILE: PosixPath = Path('/etc/nginx/sites-enabled/mmpm.conf')
MMPM_NGINX_LOG_DIR: PosixPath = Path('/var/log/nginx')
MMPM_NGINX_ACCESS_LOG_FILE: PosixPath = MMPM_NGINX_LOG_DIR / "mmpm-access.log"
MMPM_NGINX_ERROR_LOG_FILE: PosixPath = MMPM_NGINX_LOG_DIR / "mmpm-error.log"

MAGICMIRROR_WIKI_URL: str = 'https://github.com/MichMich/MagicMirror/wiki'
MAGICMIRROR_DOCUMENTATION_URL: str = 'https://docs.magicmirror.builders/'
MAGICMIRROR_MODULES_URL: str = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"

MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE: PosixPath = MMPM_CONFIG_DIR / "MagicMirror-3rd-party-packages-db.json"
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE: PosixPath = MMPM_CONFIG_DIR / 'MagicMirror-3rd-party-packages-db-expiration.json'

MMPM_PYTHON_ROOT_DIR: PosixPath = Path(__file__).absolute().parent
MMPM_JS_DIR: PosixPath = MMPM_PYTHON_ROOT_DIR / "js"

MMPM_BUNDLED_ETC_DIR: str = MMPM_PYTHON_ROOT_DIR / "etc"
MMPM_SYSTEMD_SERVICE_FILE: str = '/etc/systemd/system/mmpm.service' # TODO: use the python-systemd library

MMPM_REQUIRED_DATA_FILES: List[PosixPath] = [
    MMPM_ENV_FILE,
    MMPM_CLI_LOG_FILE,
    MMPM_EXTERNAL_PACKAGES_FILE,
    MMPM_AVAILABLE_UPGRADES_FILE,
    MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE,
    MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE,
]
