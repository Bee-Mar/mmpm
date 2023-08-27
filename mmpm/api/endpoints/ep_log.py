#!/usr/bin/env python3
from mmpm.logger import MMPMLogger
from mmpm.api.endpoints.base_endpoint import BaseEndpoint
from mmpm.api.constants import http
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.constants import paths
from mmpm.env import MMPM_DEFAULT_ENV

from flask import Blueprint, Response, request

import json
import logging.handlers

logger = MMPMLogger.get_logger(__name__)


class Endpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()
        self.blueprint = Blueprint("log", __name__, url_prefix="/api/log")
        self.handler = None

        '''
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
                return self.failure(400, "SocketHandler has not been configured.")

            logger.removeHandler(self.handler)
            self.handler = None

            if len(logger.handlers) >= current_handler_count:
                return self.failure(500, "Failed to remove SocketHandler")

            return self.success("Removed SocketHandler")
        '''

        @self.blueprint.route("/tail", methods=[http.GET])
        def tail() -> Response:
            print(logger.handlers)
            return self.success("hello")
