#!/usr/bin/env python3
from mmpm.logger import MMPMLogger
from mmpm.api.base_endpoint import BaseEndpoint
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

            installed = []

            for package in packages:
                if MagicMirrorPackage(**package).install(assume_yes=True):
                    installed.append(package)

            return self.success(json.dumps(installed))


        @self.blueprint.route("/remove", methods=[http.POST])
        def remove() -> Response:
            packages = request.get_json()["packages"]

            removed = []

            for package in packages:
                if MagicMirrorPackage(**package).remove(assume_yes=True):
                    removed.append(package)


            return self.success(json.dumps(removed))


        @self.blueprint.route("/upgrade", methods=[http.POST])
        def upgrade() -> Response:
            packages = request.get_json()["packages"]

            upgraded = []

            for package in packages:
                if MagicMirrorPackage(**package).upgrade(assume_yes=True):
                    upgraded.append(package)

            return self.success(json.dumps(upgraded))
