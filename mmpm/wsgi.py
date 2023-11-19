#!/usr/bin python3
# pylint: disable=unused-import
from gevent import monkey

monkey.patch_all()  # do not move these

from mmpm.api.entrypoint import app
from mmpm.logger import MMPMLogger
from mmpm.constants import paths

logger = MMPMLogger.get_logger(__name__)

if __name__ == "__main__":
    app.run(
        threaded=True,
        keepalive=True,
        log=logger,
        extra_files=[
            paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE,
            paths.MMPM_EXTERNAL_PACKAGES_FILE,
            paths.MMPM_AVAILABLE_UPGRADES_FILE,
            paths.MMPM_ENV_FILE,
        ],
    )
