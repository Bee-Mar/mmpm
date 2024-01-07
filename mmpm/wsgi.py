#!/usr/bin python3
# pylint: disable=unused-import

"""
This script is the main entry point for a Flask-based web application. It uses gevent for asynchronous operations
and initializes the web server with specific configurations.

The gevent's monkey patching is applied at the beginning of the script to ensure that all the standard library
modules that the application uses are cooperative with greenlets. This patching is crucial for enabling asynchronous
I/O operations, which are essential for handling multiple simultaneous client requests efficiently.

The application is configured to monitor changes in several key files and reload if any of them change. This feature
is useful for development, as it allows for changes in the application's configuration or data files to be reflected
immediately without needing a manual restart.

Attributes:
    app (Flask): The Flask application instance imported from mmpm.api.entrypoint.
    logger (Logger): A logger instance for logging information, imported from mmpm.log.factory.

Functions:
    __main__: If this script is run as the main program, it starts the Flask application with specific configurations.
"""

from gevent import monkey

monkey.patch_all()  # do not move these

from mmpm.api.entrypoint import app
from mmpm.constants import paths
from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)

if __name__ == "__main__":
    app.run(
        threaded=False,
        keepalive=True,
        log=logger,
        extra_files=[
            paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE,
            paths.MMPM_CUSTOM_PACKAGES_FILE,
            paths.MMPM_AVAILABLE_UPGRADES_FILE,
            paths.MMPM_ENV_FILE,
        ],
    )
