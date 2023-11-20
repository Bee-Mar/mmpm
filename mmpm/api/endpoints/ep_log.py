#!/usr/bin/env python3
import json
import logging.handlers

from flask import Blueprint, Response, request
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import paths
from mmpm.env import MMPM_DEFAULT_ENV
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.package import MagicMirrorPackage

logger = MMPMLogger.get_logger(__name__)


class Log(Endpoint):
    def __init__(self):
        self.name = "log"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.handler = None

        """
        @self.blueprint.route("/setup", methods=[http.GET])
        def setup() -> Response:
            current_handler_count = len(logger.handlers)

            port = logging.handlers.DEFAULT_TCP_LOGGING_PORT

            if self.handler is None:
                self.handler = logging.handlers.SocketHandler("localhost", port)
                logger.addHandler(self.handler)

            if len(logger.handlers) == current_handler_count:
                return self.success("SocketHandler is already set up")

            return self.success(port)


        @self.blueprint.route("/cleanup", methods=[http.GET])
        def cleanup() -> Response:
            current_handler_count = len(logger.handlers)

            if self.handler is None:
                return self.failure("SocketHandler has not been configured.", 400)

            logger.removeHandler(self.handler)
            self.handler = None

            if len(logger.handlers) >= current_handler_count:
                return self.failure("Failed to remove SocketHandler", 500)

            return self.success("Removed SocketHandler")
        """

        @self.blueprint.route("/tail", methods=[http.GET])
        def tail() -> Response:
            print(logger.handlers)
            return self.success("hello")
