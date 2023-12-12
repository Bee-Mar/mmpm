#!/usr/bin/env python3

from flask import Blueprint, Response, request
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import paths
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.controller import MagicMirrorController
from mmpm.magicmirror.magicmirror import MagicMirror

logger = MMPMLogger.get_logger(__name__)


class MmCtl(Endpoint):
    """An endpoint for interacting with MagicMirror at the core level (install, update, hide/show, etc)"""

    def __init__(self):
        self.name = "mm-ctl"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.controller = MagicMirrorController()
        self.magicmirror = MagicMirror()

        @self.blueprint.route("/install", methods=[http.GET])
        def install() -> Response:
            if self.magicmirror.install():
                return self.success("MagicMirror installed")

            return self.failure("Failed to install MagicMirror. See logs for details.")

        @self.blueprint.route("/remove", methods=[http.GET])
        def remove() -> Response:
            if self.magicmirror.remove():
                return self.success("MagicMirror removed")

            return self.failure("Failed to remove MagicMirror. See logs for details.")

        @self.blueprint.route("/upgrade", methods=[http.GET])
        def upgrade() -> Response:
            if self.magicmirror.upgrade():
                return self.success("MagicMirror updated")

            return self.failure("Failed to update MagicMirror. See logs for details.")

        @self.blueprint.route("/start", methods=[http.GET])
        def start() -> Response:
            if self.controller.start():
                return self.success("MagicMirror started")

            return self.failure("Failed to start MagicMirror. See logs for details.")

        @self.blueprint.route("/stop", methods=[http.GET])
        def stop() -> Response:
            if self.controller.stop():
                return self.success("MagicMirror stopped")

            return self.failure("Failed to stop MagicMirror. See logs for details.")

        @self.blueprint.route("/restart", methods=[http.GET])
        def restart() -> Response:
            if self.controller.restart():
                return self.success("MagicMirror restarted")

            return self.failure("Failed to restart MagicMirror. See logs for details.")

        @self.blueprint.route("/hide", methods=[http.POST])
        def hide() -> Response:
            modules = request.get_json()["modules"]

            if self.controller.hide(modules):
                return self.success("Hid modules")

            return self.failure("Failed to hide modules. See logs for details.")

        @self.blueprint.route("/show", methods=[http.POST])
        def show() -> Response:
            modules = request.get_json()["modules"]

            if self.controller.show(modules):
                return self.success("Shown modules")

            return self.failure("Failed to show modules. See logs for details.")
