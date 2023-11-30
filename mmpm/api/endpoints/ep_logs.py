#!/usr/bin/env python3
import json
import logging.handlers

from flask import Blueprint, Response, request
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import paths
from mmpm.env import MMPM_DEFAULT_ENV
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.package import MagicMirrorPackage

logger = MMPMLogger.get_logger(__name__)


class Logs(Endpoint):
    def __init__(self):
        self.name = "logs"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.handler = None

        @self.blueprint.route("/zip", methods=[http.GET])
        def zip() -> Response:
            print(logger.handlers)
            return self.success("hello")
