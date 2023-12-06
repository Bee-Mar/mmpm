#!/usr/bin/env python3
from flask import Blueprint, Response, request
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.magicmirror.package import MagicMirrorPackage, RemotePackage

logger = MMPMLogger.get_logger(__name__)


class Packages(Endpoint):
    def __init__(self):
        self.name = "packages"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.db = MagicMirrorDatabase()
        self.magicmirror = MagicMirror()

        @self.blueprint.route("/", methods=[http.GET])
        def retrieve() -> Response:
            logger.info("Loading database")
            self.db.load()

            if not self.db.packages:
                message = "Failed to load database"
                logger.error(message)
                return self.failure(message)

            logger.info("Sending back retrieved packages")
            return self.success([package.serialize(full=True) for package in self.db.packages])

        @self.blueprint.route("/install", methods=[http.POST])
        def install() -> Response:
            packages = request.get_json()["packages"]
            installed = [package for package in packages if MagicMirrorPackage(**package).install()]
            return self.success(installed)

        @self.blueprint.route("/remove", methods=[http.POST])
        def remove() -> Response:
            packages = request.get_json()["packages"]
            removed = [package for package in packages if MagicMirrorPackage(**package).remove()]
            return self.success(removed)

        @self.blueprint.route("/upgrade", methods=[http.POST])
        def upgrade() -> Response:
            packages = request.get_json()["packages"]
            upgraded = [package for package in packages if MagicMirrorPackage(**package).upgrade()]
            return self.success(upgraded)

        @self.blueprint.route("/mm-pkg/add", methods=[http.POST])
        def add_mm_pkg() -> Response:
            packages = request.get_json()["packages"]
            added = [package for package in packages if self.db.add_mm_pkg(**package)]
            return self.success(added)

        @self.blueprint.route("/mm-pkg/remove", methods=[http.POST])
        def remove_mm_pkg() -> Response:
            packages = request.get_json()["packages"]
            removed = [package for package in packages if self.db.remove_mm_pkg(**package)]
            return self.success(removed)

        @self.blueprint.route("/details", methods=[http.POST])
        def details() -> Response:
            package = request.get_json()["packages"][0]
            remote =  RemotePackage(MagicMirrorPackage(**package))
            health = remote.health()

            for status in health.values():
                if status["error"]:
                    message = status["error"]
                    logger.error(message)
                    return self.failure(message,code=400)
                elif status["warning"]:
                    message = status["warning"]
                    logger.warning(message)
                    return self.failure(message,code=400)

            return self.success(remote.serialize())


