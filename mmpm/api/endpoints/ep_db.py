#!/usr/bin/env python3
import json

from flask import Blueprint, Response, request
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.utils import update_available

logger = MMPMLogger.get_logger(__name__)


class Db(Endpoint):
    def __init__(self):
        self.name = "db"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.db = MagicMirrorDatabase()
        self.magicmirror = MagicMirror()

        @self.blueprint.route("/update", methods=[http.GET])
        def update() -> Response:
            if not self.db.load(update=True):
                return self.failure("Failed to update database. See logs for details.")

            can_upgrade_mmpm = update_available()
            can_upgrade_magicmirror = self.magicmirror.update()
            upgradable_count = self.db.update(can_upgrade_mmpm=can_upgrade_mmpm, can_upgrade_magicmirror=can_upgrade_magicmirror)

            return self.success(self.db.upgradable())

        @self.blueprint.route("/upgradable", methods=[http.GET])
        def upgradable() -> Response:
            upgradable = self.db.upgradable()

            if upgradable:
                return self.success(upgradable)

            return self.failure("Failed to get list of upgradable packages. See logs for details")

        @self.blueprint.route("/info", methods=[http.GET])
        def info() -> Response:
            info = self.db.info()

            if info:
                return self.success(info)

            return self.failure("Failed to retrieve database info. See logs for details")
