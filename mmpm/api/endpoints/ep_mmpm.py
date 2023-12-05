#!/usr/bin/env python3
import mmpm.utils
from flask import Blueprint, Response
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase

logger = MMPMLogger.get_logger(__name__)


class Mmpm(Endpoint):
    def __init__(self):
        self.name = "mmpm"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.db = MagicMirrorDatabase()

        @self.blueprint.route("/update", methods=[http.GET])
        def update() -> Response:
            # need to call /api/db/upgradable after this to get the information
            return self.success({"can-upgrade-mmpm": mmpm.utils.update_available()})
