#!/usr/bin/env python3
from mmpm.utils import get_host_ip

HOST = f"{get_host_ip()}"

MMPM_UI_PORT = 7890
MMPM_API_SERVER_PORT = 7891
MMPM_LOG_SERVER_PORT = 6789
MMPM_REPEATER_SERVER_PORT = 8907

MMPM_REPO_URL = "https://github.com/Bee-Mar/mmpm.git"
MMPM_FILE_URL = "https://raw.githubusercontent.com/Bee-Mar/mmpm/master/mmpm/mmpm.py"
MMPM_WIKI_URL = "https://github.com/Bee-Mar/mmpm/wiki"

MAGICMIRROR_WIKI_URL: str = "https://github.com/MichMich/MagicMirror/wiki"
MAGICMIRROR_DOCUMENTATION_URL: str = "https://docs.magicmirror.builders/"
MAGICMIRROR_MODULES_URL: str = "https://github.com/MichMich/MagicMirror/wiki/3rd-party-modules"
