#!/usr/bin/env python3
from pathlib import Path, PosixPath

HOME_DIR = Path.home()
MMPM_CONFIG_DIR = HOME_DIR / ".config" / "mmpm"
MMPM_LOG_DIR = MMPM_CONFIG_DIR / "log"
MMPM_CLI_LOG_FILE = MMPM_LOG_DIR / "mmpm-cli-interface.log"
MMPM_ENV_FILE = MMPM_CONFIG_DIR / "mmpm-env.json"
MMPM_EXTERNAL_PACKAGES_FILE = MMPM_CONFIG_DIR / "mmpm-external-packages.json"
MMPM_AVAILABLE_UPGRADES_FILE = MMPM_CONFIG_DIR / "mmpm-available-upgrades.json"
MMPM_NGINX_CONF_FILE = Path("/etc/nginx/sites-enabled/mmpm.conf")
MMPM_NGINX_LOG_DIR = Path("/var/log/nginx")
MMPM_NGINX_ACCESS_LOG_FILE = MMPM_NGINX_LOG_DIR / "mmpm-access.log"
MMPM_NGINX_ERROR_LOG_FILE = MMPM_NGINX_LOG_DIR / "mmpm-error.log"

MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE = MMPM_CONFIG_DIR / "MagicMirror-3rd-party-packages-db.json"
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE = MMPM_CONFIG_DIR / "MagicMirror-3rd-party-packages-db-last-update.json"

MMPM_PYTHON_ROOT_DIR = Path(__file__).parent.absolute().parent
MMPM_JS_DIR = MMPM_PYTHON_ROOT_DIR / "js"
MMPM_BUNDLED_ETC_DIR = MMPM_PYTHON_ROOT_DIR / "etc"
MMPM_SYSTEMD_SERVICE_FILE = Path("/etc/systemd/system/mmpm.service")

# Setup the directories and files
MMPM_CONFIG_DIR.mkdir(exist_ok=True, parents=True)
MMPM_LOG_DIR.mkdir(exist_ok=True)
MMPM_CLI_LOG_FILE.touch(exist_ok=True)
MMPM_ENV_FILE.touch(exist_ok=True)
MMPM_EXTERNAL_PACKAGES_FILE.touch(exist_ok=True)
MMPM_AVAILABLE_UPGRADES_FILE.touch(exist_ok=True)
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE.touch(exist_ok=True)
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE.touch(exist_ok=True)
