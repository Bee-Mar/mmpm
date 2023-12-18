#!/usr/bin/env python3
from flask import Blueprint, Response

import mmpm.__version__
import mmpm.utils
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.log.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)


class Mmpm(Endpoint):
    """
    A Flask endpoint class for interacting with the MMPM application in more 'meta' manner.
    """

    def __init__(self):
        self.name = "mmpm"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.handler = None

        @self.blueprint.route("/version", methods=[http.GET])
        def version() -> Response:
            """
            A Flask route method for retrieving the current MMPM version.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing the current MMPM version.
            """
            return self.success(mmpm.__version__.version)

        @self.blueprint.route("/upgrade", methods=[http.GET])
        def upgrade() -> Response:
            """
            A Flask route method for upgrading MMPM.

            Parameters:
                None

            Returns:
                Response: A Flask Response object indicating success or failure of the upgrade operation.
            """
            if mmpm.utils.upgrade():
                return self.success("Upgrade MMPM")

            return self.failure("Failed to upgrade MMPM. See logs for details.")
