#!/usr/bin/env python3
from os.path import join, expanduser, normpath, dirname, abspath

HOME_DIR: str = expanduser("~")

MMPM_CONFIG_DIR: str = normpath(join(HOME_DIR, '.config', 'mmpm'))
MMPM_LOG_DIR: str = normpath(join(MMPM_CONFIG_DIR, 'log'))

MMPM_ENV_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-env.json')

MMPM_EXTERNAL_PACKAGES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-external-packages.json')
MMPM_AVAILABLE_UPGRADES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-available-upgrades.json')
MMPM_CLI_LOG_FILE: str = join(MMPM_LOG_DIR, 'mmpm-cli-interface.log')

MMPM_NGINX_CONF_FILE: str = '/etc/nginx/sites-enabled/mmpm.conf'
MMPM_NGINX_LOG_DIR: str = '/var/log/nginx'
MMPM_NGINX_ACCESS_LOG_FILE: str = join(MMPM_NGINX_LOG_DIR, 'mmpm-access.log')
MMPM_NGINX_ERROR_LOG_FILE: str = join(MMPM_NGINX_LOG_DIR, 'mmpm-error.log')

MAGICMIRROR_WIKI_URL: str = 'https://github.com/MichMich/MagicMirror/wiki'
MAGICMIRROR_DOCUMENTATION_URL: str = 'https://docs.magicmirror.builders/'
MAGICMIRROR_MODULES_URL: str = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"

MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE: str = join(MMPM_CONFIG_DIR, 'MagicMirror-3rd-party-packages-db.json')

MMPM_WEB_ROOT_DIR: str = '/var/www/mmpm'
MMPM_STATIC_DIR: str = '/var/www/mmpm/static'
MMPM_TEMPLATES_DIR: str = '/var/www/mmpm/templates'

MMPM_PYTHON_ROOT_DIR: str = dirname(abspath(__file__))
MMPM_JS_DIR: str = join(MMPM_PYTHON_ROOT_DIR, 'js')

MMPM_BUNDLED_ETC_DIR: str = join(MMPM_PYTHON_ROOT_DIR, 'etc')
MMPM_SYSTEMD_SERVICE_FILE: str = '/etc/systemd/system/mmpm.service'

MMPM_REQUIRED_DATA_FILES: List[str] = [
    MMPM_ENV_FILE,
    MMPM_CLI_LOG_FILE,
    MMPM_EXTERNAL_PACKAGES_FILE,
    MMPM_AVAILABLE_UPGRADES_FILE,
    MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE
]

