#!/usr/bin/env python3
from mmpm.env import MMPMEnv
from mmpm.logger import MMPMLogger
from mmpm.api.base_endpoint import BaseEndpoint
from mmpm.magicmirror.database import MagicMirrorDatabase
from flask import Blueprint, Response


class Endpoint(BaseEndpoint):
    def __init__(self):
        self.blueprint = Blueprint("package", __name__, url_prefix="/api/package")
        self.db = MagicMirrorDatabase()

        @self.blueprint.route("/load", methods=["GET"])
        def load() -> Response:
            if self.db.load():
                return self.success("Loaded database")

            return self.failure(500, "Failed to load database")


