#!/usr/bin/env python3
from os.path import join, expanduser
from os import environ

HOME_DIR: str = expanduser("~")
TITLE: str = 'Title'
REPOSITORY: str = 'Repository'
DESCRIPTION: str = 'Description'
AUTHOR: str = 'Author'
CATEGORY: str = 'Category'

MAKEFILE: str = 'Makefile'
CMAKELISTS: str = 'CMakeLists.txt'
PACKAGE_JSON: str = 'package.json'
GEMFILE: str = 'Gemfile'
NOT_AVAILABLE = 'N/A'

MMPM_ENV_VAR: str = 'MMPM_MAGICMIRROR_ROOT'
MMPM_REPO_URL: str = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL: str = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL: str = 'https://github.com/Bee-Mar/mmpm/wiki'
MMPM_CONFIG_DIR: str = join(HOME_DIR, '.config', 'mmpm')
MMPM_LOG_FILE: str = join(MMPM_CONFIG_DIR, 'log', 'mmpm-cli-interface.log')
MMPM_EXTERNAL_SOURCES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-external-sources.json')
MMPM_AVAILABLE_UPDATES_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-module-updates.json')

LIBMMPM_SHARED_OBJECT: str = join('/', 'usr', 'local', 'lib', 'mmpm', 'libmmpm.so')
SNAPSHOT_FILE: str = join(MMPM_CONFIG_DIR, 'MagicMirror-modules-snapshot.json')
EXTERNAL_MODULE_SOURCES: str = 'External Module Sources'
GUNICORN_LOG_ACCESS_LOG_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-gunicorn-access.log')
GUNICORN_LOG_ERROR_LOG_FILE: str = join(MMPM_CONFIG_DIR, 'mmpm-gunicorn-error.log')

MAGICMIRROR_MODULES_URL: str = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"
MAGICMIRROR_ROOT: str = environ[MMPM_ENV_VAR] if MMPM_ENV_VAR in environ else join(HOME_DIR, 'MagicMirror')
MAGICMIRROR_CONFIG_FILE: str = join(MAGICMIRROR_ROOT, 'config', 'config.js')

