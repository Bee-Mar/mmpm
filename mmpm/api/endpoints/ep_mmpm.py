#!/usr/bin/env python3
from datetime import datetime
from os import chdir
from shutil import make_archive

import mmpm.__version__
import mmpm.utils
from flask import Blueprint, Response, send_file
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import paths
from mmpm.log.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)


class Mmpm(Endpoint):
    def __init__(self):
        self.name = "mmpm"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.handler = None

        @self.blueprint.route("/version", methods=[http.GET])
        def version() -> Response:
            return self.success(mmpm.__version__.version)

        @self.blueprint.route("/upgrade", methods=[http.GET])
        def upgrade() -> Response:
            if mmpm.utils.upgrade():
                return self.success("Upgrade MMPM")

            return self.failure("Failed to upgrade MMPM. See logs for details.")
