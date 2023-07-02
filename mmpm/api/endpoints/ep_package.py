#!/usr/bin/env python3
from mmpm.logger import MMPMLogger
from mmpm.api.base_endpoint import BaseEndpoint
from mmpm.api.constants import http

from flask import Blueprint, jsonify, Response
import json

logger = MMPMLogger.get_logger(__name__)

class Endpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()
        self.blueprint = Blueprint("package", __name__, url_prefix="/api/packages")


        @self.blueprint.route("/retrieve", methods=[http.GET])
        def retrieve() -> Response:
            logger.info("Loading database")

            is_expired = self.db.is_expired()
            self.db.load(refresh=is_expired)

            if is_expired:
                self.db.update(automated=True)

            if not self.db.packages:
                message = "Failed to load database"
                logger.error(message)
                return self.failure(500, message)

            logger.info("Sending back retrieved packages")
            return self.success(json.dumps(self.db.packages, default=lambda package : package.serialize(full=True)))


        @self.blueprint.route("/install", methods=[http.POST])
        def install() -> Response:
            pass
