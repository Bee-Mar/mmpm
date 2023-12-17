#!/usr/bin/env python3
from flask import Blueprint, Response, request

from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.log.logger import MMPMLogger
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

            logger.info("Sending back current packages")

            # this section here is very inefficient, but honestly, there's not much of a way around
            # it if we want the user to have information about the status of the packages on the web app
            # also, the data isn't THAT large, so it's fine, but it's definitely kinda gross
            upgradable = [MagicMirrorPackage(**pkg) for pkg in self.db.upgradable()["packages"]]
            pkgs = self.db.packages

            for pkg in pkgs:
                if pkg in upgradable:
                    pkg.is_upgradable = True

            return self.success([package.serialize(full=True) for package in pkgs])

        @self.blueprint.route("/install", methods=[http.POST])
        def install() -> Response:
            packages = request.get_json()["packages"]
            success = []
            failure = []

            for package in packages:
                pkg = MagicMirrorPackage(**package)

                if pkg.install():
                    success.append(package)
                else:
                    logger.debug(f"Removing {pkg.title} due to installation failure. Please try reinstalling manually.")
                    failure.append(package)
                    pkg.remove()

            return self.success({"success": success, "failure": failure})

        @self.blueprint.route("/remove", methods=[http.POST])
        def remove() -> Response:
            packages = request.get_json()["packages"]
            success = []
            failure = []

            for package in packages:
                if MagicMirrorPackage(**package).remove():
                    success.append(package)
                else:  # honestly, this should never fail anyway
                    failure.append(package)

            return self.success({"success": success, "failure": failure})

        @self.blueprint.route("/upgrade", methods=[http.POST])
        def upgrade() -> Response:
            packages = request.get_json()["packages"]
            success = []
            failure = []

            for package in packages:
                if MagicMirrorPackage(**package).upgrade():
                    success.append(package)
                else:
                    failure.append(package)

            return self.success({"success": success, "failure": failure})

        @self.blueprint.route("/mm-pkg/add", methods=[http.POST])
        def add_mm_pkg() -> Response:
            package = MagicMirrorPackage(**request.get_json()["package"])

            if self.db.add_mm_pkg(package.title, package.author, package.repository, package.description):
                return self.success(f"Added custom package named {package.title}")

            return self.failure("Failed to add custom package. See logs for details.")

        @self.blueprint.route("/mm-pkg/remove", methods=[http.POST])
        def remove_mm_pkg() -> Response:
            packages = [MagicMirrorPackage(**pkg) for pkg in request.get_json()["packages"]]
            success = []
            failure = []

            for package in packages:
                if self.db.remove_mm_pkg(package.title):
                    success.append(package.serialize(full=True))
                else:
                    failure.append(package.serialize(full=True))

            return self.success({"success": success, "failure": failure})

        @self.blueprint.route("/details", methods=[http.POST])
        def details() -> Response:
            package = request.get_json()["packages"][0]
            remote = RemotePackage(MagicMirrorPackage(**package))
            health = remote.health()

            for status in health.values():
                if status["error"]:
                    message = status["error"]
                    logger.error(message)
                    return self.failure(message, code=400)
                elif status["warning"]:
                    message = status["warning"]
                    logger.warning(message)
                    return self.failure(message, code=400)

            return self.success(remote.serialize())
