#!/usr/bin/env python3
from flask import Blueprint, Response, request

from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.magicmirror.package import MagicMirrorPackage, RemotePackage

logger = MMPMLogFactory.get_logger(__name__)


class Packages(Endpoint):
    """
    Endpoint to handle installation, removal, upgrading, and updating of MagicMirrorPackages
    """

    def __init__(self):
        self.name = "packages"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.db = MagicMirrorDatabase()
        self.magicmirror = MagicMirror()

        @self.blueprint.route("/", methods=[http.GET])
        def retrieve() -> Response:
            """
            A Flask route method for retrieving a list of all MagicMirror packages.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing a list of all packages or an error message.
            """

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
            """
            A Flask route method for installing selected MagicMirror packages.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing the status of each installation attempt.
            """

            packages = request.get_json()["packages"]
            success = []
            failure = []

            for package in packages:
                pkg = MagicMirrorPackage(**package)

                if pkg.install():
                    logger.debug(f"Installed {pkg.title}")
                    success.append(package)
                else:
                    logger.debug(f"Removing {pkg.title} due to installation failure. Please try reinstalling manually.")
                    failure.append(package)
                    pkg.remove()

            return self.success({"success": success, "failure": failure})

        @self.blueprint.route("/remove", methods=[http.POST])
        def remove() -> Response:
            """
            A Flask route method for removing selected MagicMirror packages.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing the status of each removal attempt.
            """

            packages = request.get_json()["packages"]
            success = []
            failure = []

            for package in packages:
                pkg = MagicMirrorPackage(**package)

                if pkg.remove():
                    logger.debug(f"Removed {pkg.title}")
                    success.append(package)
                else:  # honestly, this should never fail anyway
                    logger.debug(f"Failed to remove {pkg.title}")
                    failure.append(package)

            return self.success({"success": success, "failure": failure})

        @self.blueprint.route("/upgrade", methods=[http.POST])
        def upgrade() -> Response:
            """
            A Flask route method for upgrading selected MagicMirror packages.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing the status of each upgrade attempt.
            """

            packages = request.get_json()["packages"]
            success = []
            failure = []

            for package in packages:
                pkg = MagicMirrorPackage(**package)

                if pkg.upgrade():
                    logger.debug(f"Upgraded {pkg.title}")
                    success.append(package)
                else:
                    logger.debug(f"Failed to upgrade {pkg.title}")
                    failure.append(package)

            return self.success({"success": success, "failure": failure})

        @self.blueprint.route("/mm-pkg/add", methods=[http.POST])
        def add_mm_pkg() -> Response:
            """
            A Flask route method for adding a custom MagicMirror package.

            Parameters:
                None

            Returns:
                Response: A Flask Response object indicating the success or failure of adding the custom package.
            """

            package = MagicMirrorPackage(**request.get_json()["package"])

            if self.db.add_mm_pkg(package.title, package.author, package.repository, package.description):
                return self.success(f"Added custom package named {package.title}")

            return self.failure("Failed to add custom package. See logs for details.")

        @self.blueprint.route("/mm-pkg/remove", methods=[http.POST])
        def remove_mm_pkg() -> Response:
            """
            A Flask route method for removing custom MagicMirror packages.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing the status of each custom package removal attempt.
            """

            packages = request.get_json()["packages"]
            success = []
            failure = []

            for package in packages:
                pkg = MagicMirrorPackage(**package)

                if self.db.remove_mm_pkg(pkg.title):
                    success.append(package)
                else:
                    failure.append(package)

            return self.success({"success": success, "failure": failure})

        @self.blueprint.route("/details", methods=[http.POST])
        def details() -> Response:
            """
            A Flask route method for retrieving detailed information about a selected MagicMirror package.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing detailed information about the package or an error message.
            """

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
