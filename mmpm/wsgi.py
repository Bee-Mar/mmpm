#!/usr/bin python3
# pylint: disable=unused-import
from mmpm.api import flask_sio, app
import mmpm.utils
import mmpm.consts

if __name__ == '__main__':
    flask_sio.run(
        flask_sio,
        #threaded=True,
        keepalive=True,
        log=mmpm.utils.log,
        extra_files=[
            mmpm.consts.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE,
            mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE,
            mmpm.consts.MMPM_AVAILABLE_UPGRADES_FILE,
        ]
    )
