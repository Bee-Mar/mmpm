#!/usr/bin/env python3

from flask import Blueprint, Response, request

from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.controller import MagicMirrorController
from mmpm.magicmirror.magicmirror import MagicMirror

logger = MMPMLogFactory.get_logger(__name__)


class MmCtl(Endpoint):
    """
    A Flask endpoint for interacting with MagicMirror at the core level. This includes operations
    like install, remove, upgrade, start, stop, restart, hide, and show.
    """

    def __init__(self):
        self.name = "mm-ctl"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.controller = MagicMirrorController()
        self.magicmirror = MagicMirror()

        @self.blueprint.route("/install", methods=[http.GET])
        def install() -> Response:
            """
            A Flask route method for installing MagicMirror.

            Parameters:
                None

            Returns:
                Response: A Flask Response object indicating the success or failure of the installation.
            """

            logger.info("Received request to install MagicMirror")
            if self.magicmirror.install():
                return self.success("MagicMirror installed")

            return self.failure("Failed to install MagicMirror. See logs for details.")

        @self.blueprint.route("/remove", methods=[http.GET])
        def remove() -> Response:
            """
            A Flask route method for removing MagicMirror.

            Parameters:
                None

            Returns:
                Response: A Flask Response object indicating the success or failure of the removal.
            """

            logger.info("Received request to remove MagicMirror")
            if self.magicmirror.remove():
                return self.success("MagicMirror removed")

            return self.failure("Failed to remove MagicMirror. See logs for details.")

        @self.blueprint.route("/upgrade", methods=[http.GET])
        def upgrade() -> Response:
            """
            A Flask route method for upgrading MagicMirror.

            Parameters:
                None

            Returns:
                Response: A Flask Response object indicating the success or failure of the upgrade.
            """

            logger.info("Received request to upgrade MagicMirror")
            if self.magicmirror.upgrade():
                return self.success("MagicMirror updated")

            return self.failure("Failed to update MagicMirror. See logs for details.")

        @self.blueprint.route("/start", methods=[http.GET])
        def start() -> Response:
            """
            A Flask route method for starting MagicMirror.

            Parameters:
                None

            Returns:
                Response: A Flask Response object indicating the success or failure of starting MagicMirror.
            """

            logger.info("Received request to start MagicMirror")
            if self.controller.start():
                return self.success("MagicMirror started")

            return self.failure("Failed to start MagicMirror. See logs for details.")

        @self.blueprint.route("/stop", methods=[http.GET])
        def stop() -> Response:
            """
            A Flask route method for stopping MagicMirror.

            Parameters:
                None

            Returns:
                Response: A Flask Response object indicating the success or failure of stopping MagicMirror.
            """

            logger.info("Received request to stop MagicMirror")
            if self.controller.stop():
                return self.success("MagicMirror stopped")

            return self.failure("Failed to stop MagicMirror. See logs for details.")

        @self.blueprint.route("/restart", methods=[http.GET])
        def restart() -> Response:
            """
            A Flask route method for restarting MagicMirror.

            Parameters:
                None

            Returns:
                Response: A Flask Response object indicating the success or failure of restarting MagicMirror.
            """

            logger.info("Received request to restart MagicMirror")
            if self.controller.restart():
                return self.success("MagicMirror restarted")

            return self.failure("Failed to restart MagicMirror. See logs for details.")

        @self.blueprint.route("/hide", methods=[http.POST])
        def hide() -> Response:
            """
            A Flask route method for hiding a specified module in MagicMirror.

            Parameters:
                module (str): The key of the module to hide.

            Returns:
                Response: A Flask Response object indicating the success or failure of hiding the module.
            """

            module = request.get_json()["module"]
            logger.info(f"Received request to hide MagicMirror module {module}")

            if self.controller.hide(module):
                return self.success("Hid module")

            return self.failure("Failed to hide modules. See logs for details.")

        @self.blueprint.route("/show", methods=[http.POST])
        def show() -> Response:
            """
            A Flask route method for showing a specified module in MagicMirror.

            Parameters:
                module (str): The key of the module to show.

            Returns:
                Response: A Flask Response object indicating the success or failure of showing the module.
            """

            module = request.get_json()["module"]

            logger.info(f"Received request to show MagicMirror module {module}")

            if self.controller.show(module):
                return self.success("Shown module")

            return self.failure("Failed to show modules. See logs for details.")
