#!/usr/bin/env python3
from mmpm.env import MMPMEnv
from mmpm.logger import MMPMLogger
from mmpm.api.base_endpoint import BaseEndpoint
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.api.constants import http

from flask import Blueprint, jsonify, Response
import json


class Endpoint(BaseEndpoint):
    def __init__(self):
        self.env = MMPMEnv()
        self.blueprint = Blueprint("magicmirror", __name__, url_prefix="/api/magicmirror")
        self.db = MagicMirrorDatabase()

        @self.blueprint.route("/retrieve", methods=[http.GET])
        def load() -> Response:
            if not self.db.load():
                return self.failure(500, "Failed to load database")

            return self.success(json.dumps(self.packages, indent=2, default=lambda package: package.serialize_full()))

        @self.blueprint.route("/install", methods=[http.POST])
        def install() -> Response:
            pass
