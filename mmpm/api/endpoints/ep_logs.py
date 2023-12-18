#!/usr/bin/env python3
from datetime import datetime
from os import chdir
from shutil import make_archive

from flask import Blueprint, Response, send_file

from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import paths
from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)


class Logs(Endpoint):
    """
    A Flask endpoint for handling requests related to log files.
    """

    def __init__(self):
        """
        Initializes the Logs endpoint with its name, blueprint, and route handler.
        """
        super().__init__()
        self.name = "logs"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")

        @self.blueprint.route("/archive", methods=[http.GET])
        def archive() -> Response:
            """
            Handles a GET request to create and serve a ZIP archive of log files.

            Returns:
                Response: A Flask Response object that enables the client to download the ZIP archive.
            """
            logger.debug("Creating zip of log files")
            chdir("/tmp")
            today = datetime.now()
            zip_file_name = f"mmpm-logs-{today.year}-{today.month}-{today.day}"
            logger.debug(f"Creating zip of log files named '{zip_file_name}'")
            archive_name = make_archive(zip_file_name, "zip", paths.MMPM_LOG_DIR)
            logger.debug(f"Archive created: {bool(archive_name)}")
            return send_file(f"/tmp/{zip_file_name}.zip", f"{zip_file_name}.zip", as_attachment=True)
