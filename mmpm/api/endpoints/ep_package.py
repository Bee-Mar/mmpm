#!/usr/bin/env python3
from mmpm.logger import MMPMLogger
from mmpm.api.endpoints.base_endpoint import BaseEndpoint
from mmpm.api.constants import http
from mmpm.magicmirror.package import MagicMirrorPackage

from flask import Blueprint, Response, request

import json

logger = MMPMLogger.get_logger(__name__)

class Endpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()
        self.blueprint = Blueprint("packages", __name__, url_prefix="/api/packages")


        @self.blueprint.route("/retrieve", methods=[http.GET])
        def retrieve() -> Response:
            logger.info("Loading database")

            is_expired = self.db.is_expired()
            self.db.load(refresh=is_expired)

            if is_expired:
                self.db.update()

            if not self.db.packages:
                message = "Failed to load database"
                logger.error(message)
                return self.failure(500, message)

            logger.info("Sending back retrieved packages")
            return self.success(json.dumps(self.db.packages, default=lambda package : package.serialize(full=True)))


        @self.blueprint.route("/install", methods=[http.POST])
        def install() -> Response:
            packages = request.get_json()["packages"]
            installed = [package for package in packages if MagicMirrorPackage(**package).remove(assume_yes=True)]
            return self.success(json.dumps(installed))


        @self.blueprint.route("/remove", methods=[http.POST])
        def remove() -> Response:
            packages = request.get_json()["packages"]
            removed = [package for package in packages if MagicMirrorPackage(**package).remove(assume_yes=True)]
            return self.success(json.dumps(removed))


        @self.blueprint.route("/upgrade", methods=[http.POST])
        def upgrade() -> Response:
            packages = request.get_json()["packages"]
            upgraded = [package for package in packages if MagicMirrorPackage(**package).upgrade(assume_yes=True)]
            return self.success(json.dumps(upgraded))


        @self.blueprint.route("/add-mm-pkg", methods=[http.POST])
        def add_mm_pkg() -> Response:
            packages = request.get_json()["packages"]
            added = [package for package in packages if self.db.add_mm_pkg(**package)]
            return self.success(json.dumps(added))


        @self.blueprint.route("/remove-mm-pkg", methods=[http.POST])
        def remove_mm_pkg() -> Response:
            packages = request.get_json()["packages"]
            removed = [package for package in packages if self.db.remove_mm_pkg(**package)]
            return self.success(json.dumps(removed))
