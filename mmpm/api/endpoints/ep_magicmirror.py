#!/usr/bin/env python3
import json

from flask import Blueprint, Response
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)


class Magicmirror(Endpoint):
    def __init__(self):
        self.name = "magicmirror"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")

        @self.blueprint.route("/retrieve", methods=[http.GET])
        def load() -> Response:
            if not self.db.load():
                return self.failure("Failed to load database")

            return self.success(json.dumps(self.packages, indent=2, default=lambda package: package.serialize_full()))

        @self.blueprint.route("/install", methods=[http.POST])
        def install() -> Response:
            pass

        @self.blueprint.route("/remove", methods=[http.POST])
        def remove() -> Response:
            pass

        @self.blueprint.route("/update", methods=[http.POST])
        def update() -> Response:
            pass

        @self.blueprint.route("/upgrade", methods=[http.POST])
        def upgrade() -> Response:
            pass

        @self.blueprint.route("/hide", methods=[http.POST])
        def hide() -> Response:
            pass

        @self.blueprint.route("/show", methods=[http.POST])
        def show() -> Response:
            pass
