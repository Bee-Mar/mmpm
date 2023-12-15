#!/usr/bin/env python3

from flask import Blueprint, Response, jsonify
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.log.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)


class Index(Endpoint):
    def __init__(self, url_map):
        super().__init__()
        self.name = "index"
        self.blueprint = Blueprint(self.name, __name__, url_prefix="/api/index")
        self.url_map = url_map

        @self.blueprint.route("/", methods=[http.GET])
        def default() -> Response:
            logger.info("Sending back url map")
            rules = [(str(url), list(url.methods)) for url in self.url_map.iter_rules()]
            formatted_rules = [{"url": rule[0], "methods": rule[1]} for rule in rules]
            return jsonify(formatted_rules[1:])
