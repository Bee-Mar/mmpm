#!/usr/bin/env python3
from pathlib import Path, PosixPath
from typing import List

HOME_DIR: Path = Path.home()

MMPM_CONFIG_DIR: PosixPath = HOME_DIR / ".config" / "mmpm"
MMPM_LOG_DIR: PosixPath = MMPM_CONFIG_DIR / "log"

MMPM_ENV_FILE: PosixPath = MMPM_CONFIG_DIR / "mmpm-env.json"
MMPM_EXTERNAL_PACKAGES_FILE: PosixPath = MMPM_CONFIG_DIR / "mmpm-external-packages.json"

MMPM_AVAILABLE_UPGRADES_FILE: PosixPath = MMPM_CONFIG_DIR /  "mmpm-available-upgrades.json"
MMPM_CLI_LOG_FILE: PosixPath = MMPM_LOG_DIR / "mmpm-cli-interface.log"

MMPM_NGINX_CONF_FILE: PosixPath = Path('/etc/nginx/sites-enabled/mmpm.conf')
MMPM_NGINX_LOG_DIR: PosixPath = Path('/var/log/nginx')
MMPM_NGINX_ACCESS_LOG_FILE: PosixPath = MMPM_NGINX_LOG_DIR / "mmpm-access.log"
MMPM_NGINX_ERROR_LOG_FILE: PosixPath = MMPM_NGINX_LOG_DIR / "mmpm-error.log"

MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE: PosixPath = MMPM_CONFIG_DIR / "MagicMirror-3rd-party-packages-db.json"
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE: PosixPath = MMPM_CONFIG_DIR / 'MagicMirror-3rd-party-packages-db-expiration.json'

MMPM_PYTHON_ROOT_DIR: PosixPath = Path(__file__).absolute().parent
MMPM_SYSTEMD_SERVICE_FILE: PosixPath = Path('/etc/systemd/system/mmpm.service') # TODO: use the python-systemd library

MMPM_REQUIRED_DATA_FILES: List[PosixPath] = [
    MMPM_ENV_FILE,
    MMPM_CLI_LOG_FILE,
    MMPM_EXTERNAL_PACKAGES_FILE,
    MMPM_AVAILABLE_UPGRADES_FILE,
    MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE,
    MAGICMIRROR_3RD_PARTY_PACKAGES_DB_EXPIRATION_FILE,
]
