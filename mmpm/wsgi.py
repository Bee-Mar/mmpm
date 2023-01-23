#!/usr/bin python3
# pylint: disable=unused-import
from gevent import monkey
monkey.patch_all() # do not move these

import mmpm.consts

from mmpm.api import app
from mmpm.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)

if __name__ == '__main__':
    app.run(
        threaded=True,
        keepalive=True,
        log=logger,
        extra_files=[
            mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE,
            mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE,
            mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE,
            mmpm.consts.MMPM_ENV_FILE,
        ]
    )
