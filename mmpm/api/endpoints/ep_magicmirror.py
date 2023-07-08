#!/usr/bin/env python3
from mmpm.logger import MMPMLogger
from mmpm.api.base_endpoint import BaseEndpoint
from mmpm.api.constants import http

from flask import Blueprint, Response
import json

logger = MMPMLogger.get_logger(__name__)

class Endpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()
        self.blueprint = Blueprint("magicmirror", __name__, url_prefix="/api/magicmirror")

        @self.blueprint.route("/retrieve", methods=[http.GET])
        def load() -> Response:
            if not self.db.load():
                return self.failure(500, "Failed to load database")

            return self.success(json.dumps(self.packages, indent=2, default=lambda package: package.serialize_full()))

        @self.blueprint.route("/install", methods=[http.POST])
        def install() -> Response:
            pass
