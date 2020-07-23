#!/usr/bin python3
# pylint: disable=unused-import
import eventlet
eventlet.monkey_patch() # do not move these

from mmpm.api import app

import mmpm.utils
import mmpm.consts
import mmpm.core

mmpm.core.load_packages()

if __name__ == '__main__':
    app.run(
        threaded=True,
        keepalive=True,
        log=mmpm.utils.log,
        extra_files=[
            mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE,
            mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE,
            mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE,
            mmpm.consts.MMPM_ENV_FILE,
        ]
    )
