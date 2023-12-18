#!/usr/bin/env python3
from pathlib import Path

HOME_DIR = Path.home()
MMPM_CONFIG_DIR = HOME_DIR / ".config" / "mmpm"
MMPM_LOG_DIR = MMPM_CONFIG_DIR / "log"
MMPM_CLI_LOG_FILE = MMPM_LOG_DIR / "mmpm-cli.log"
MMPM_ENV_FILE = MMPM_CONFIG_DIR / "mmpm-env.json"
MMPM_CUSTOM_PACKAGES_FILE = MMPM_CONFIG_DIR / "mmpm-custom-packages.json"
MMPM_AVAILABLE_UPGRADES_FILE = MMPM_CONFIG_DIR / "mmpm-available-upgrades.json"
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE = MMPM_CONFIG_DIR / "MagicMirror-3rd-party-packages-db.json"
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE = MMPM_CONFIG_DIR / "MagicMirror-3rd-party-packages-db-last-update.json"

# Setup the directories and files
MMPM_CONFIG_DIR.mkdir(exist_ok=True, parents=True)
MMPM_LOG_DIR.mkdir(exist_ok=True)
MMPM_CLI_LOG_FILE.touch(exist_ok=True)
MMPM_ENV_FILE.touch(exist_ok=True)
MMPM_CUSTOM_PACKAGES_FILE.touch(exist_ok=True)
MMPM_AVAILABLE_UPGRADES_FILE.touch(exist_ok=True)
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE.touch(exist_ok=True)
MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE.touch(exist_ok=True)
