#!/usr/bin/env python3
from mmpm.logger import MMPMLogger
from mmpm.api.endpoints.base_endpoint import BaseEndpoint
from mmpm.api.constants import http

from flask import Blueprint, Response
import json

logger = MMPMLogger.get_logger(__name__)

class Endpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()
        self.blueprint = Blueprint("database", __name__, url_prefix="/api/database")

        @self.blueprint.route("/load", methods=[http.GET])
        def load() -> Response:
            is_expired: bool = self.db.is_expired()

            if is_expired:
                self.db.download()

            if not self.db.load(refresh=is_expired):
                return self.failure(500, "Failed to load database")

            if is_expired:
                self.db.update()

            return self.success(json.dumps(self.packages, indent=2, default=lambda package: package.serialize_full()))


        @self.blueprint.route("/upgradable", methods=[http.GET])
        def upgradable() -> Response:
            return self.success(json.dumps(self.db.upgradable()))

