#!/usr/bin/env python3
import json

from flask import Blueprint, Response
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)


class Database(Endpoint):
    def __init__(self):
        super().__init__()
        self.name = "database"
        self.blueprint = Blueprint(self.name, __name__, url_prefix="/api/database")

        @self.blueprint.route("/load", methods=[http.GET])
        def load() -> Response:
            is_expired = self.db.is_expired()

            if not self.db.load(refresh=is_expired):
                return self.failure("Failed to load database")

            return self.success(json.dumps(self.packages, indent=2, default=lambda package: package.serialize_full()))

        @self.blueprint.route("/upgradable", methods=[http.GET])
        def upgradable() -> Response:
            return self.success(json.dumps(self.db.upgradable()))
