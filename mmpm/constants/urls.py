#!/usr/bin/env python3
from mmpm.utils import get_host_ip

HOST = f"{get_host_ip()}"

MMPM_UI_PORT = 7890
MMPM_API_SERVER_PORT = 7891
MMPM_LOG_SERVER_PORT = 6789
MMPM_REPEATER_SERVER_PORT = 8907

MMPM_WIKI_URL = "https://github.com/Bee-Mar/mmpm/wiki"

MAGICMIRROR_REPO_URL: str = "https://github.com/MagicMirrorOrg/MagicMirror"
MAGICMIRROR_WIKI_URL: str = f"{MAGICMIRROR_REPO_URL}/wiki"
MAGICMIRROR_DOCUMENTATION_URL: str = "https://docs.magicmirror.builders/"
MAGICMIRROR_MODULES_URL: str = f"{MAGICMIRROR_REPO_URL}/wiki/3rd-party-modules"
