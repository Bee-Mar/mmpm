#!/usr/bin/env python3
from pathlib import Path, PosixPath

HOME_DIR: PosixPath = Path.home()
MMPM_CONFIG_DIR: PosixPath = HOME_DIR / ".config" / "mmpm"
MMPM_LOG_DIR: PosixPath = MMPM_CONFIG_DIR / "log"
MMPM_CLI_LOG_FILE: PosixPath = MMPM_LOG_DIR / "mmpm-cli-interface.log"
MMPM_ENV_FILE: PosixPath = MMPM_CONFIG_DIR / "mmpm-env.json"
MMPM_EXTERNAL_PACKAGES_FILE: PosixPath = MMPM_CONFIG_DIR / "mmpm-external-packages.json"
MMPM_AVAILABLE_UPGRADES_FILE: PosixPath = MMPM_CONFIG_DIR / "mmpm-available-upgrades.json"
MMPM_NGINX_CONF_FILE: PosixPath = Path("/etc/nginx/sites-enabled/mmpm.conf")
MMPM_NGINX_LOG_DIR: PosixPath = Path("/var/log/nginx")
MMPM_NGINX_ACCESS_LOG_FILE: PosixPath = MMPM_NGINX_LOG_DIR / "mmpm-access.log"
MMPM_NGINX_ERROR_LOG_FILE: PosixPath = MMPM_NGINX_LOG_DIR / "mmpm-error.log"

MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE: PosixPath = MMPM_CONFIG_DIR / "MagicMirror-3rd-party-packages-db.json"
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE: PosixPath = MMPM_CONFIG_DIR / "MagicMirror-3rd-party-packages-db-last-update.json"

MMPM_PYTHON_ROOT_DIR: PosixPath = Path(__file__).parent.absolute().parent
MMPM_JS_DIR: PosixPath = MMPM_PYTHON_ROOT_DIR / "js"
MMPM_BUNDLED_ETC_DIR: PosixPath = MMPM_PYTHON_ROOT_DIR / "etc"
MMPM_SYSTEMD_SERVICE_FILE: PosixPath = Path("/etc/systemd/system/mmpm.service")

# Setup the directories and files
MMPM_CONFIG_DIR.mkdir(exist_ok=True, parents=True)
MMPM_LOG_DIR.mkdir(exist_ok=True)
MMPM_CLI_LOG_FILE.touch(exist_ok=True)
MMPM_ENV_FILE.touch(exist_ok=True)
MMPM_EXTERNAL_PACKAGES_FILE.touch(exist_ok=True)
MMPM_AVAILABLE_UPGRADES_FILE.touch(exist_ok=True)
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE.touch(exist_ok=True)
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE.touch(exist_ok=True)
