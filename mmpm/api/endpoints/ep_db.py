#!/usr/bin/env python3

from flask import Blueprint, Response

from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.magicmirror import MagicMirror
from mmpm.utils import update_available

logger = MMPMLogFactory.get_logger(__name__)


class Db(Endpoint):
    """
    Endpoint to interact with the MagicMirrorDatabase object. Handles updating, upgrading, and collecting information about the database.
    """

    def __init__(self):
        self.name = "db"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.db = MagicMirrorDatabase()
        self.magicmirror = MagicMirror()

        @self.blueprint.route("/update", methods=[http.GET])
        def update() -> Response:
            """
            A Flask route method for updating the MagicMirror database.

            Parameters:
                None

            Returns:
                Response: A Flask Response object indicating the success or failure of the database update.
            """
            if not self.db.load(update=True):
                return self.failure("Failed to update database. See logs for details.")

            can_upgrade_mmpm = update_available()
            can_upgrade_magicmirror = self.magicmirror.update()
            self.db.update(can_upgrade_mmpm=can_upgrade_mmpm, can_upgrade_magicmirror=can_upgrade_magicmirror)

            return self.success(self.db.upgradable())

        @self.blueprint.route("/upgradable", methods=[http.GET])
        def upgradable() -> Response:
            """
            A Flask route method for retrieving a list of upgradable packages from the MagicMirror database.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing a list of upgradable packages or an error message.
            """

            upgradable = self.db.upgradable()

            if upgradable:
                return self.success(upgradable)

            return self.failure("Failed to get list of upgradable packages. See logs for details")

        @self.blueprint.route("/info", methods=[http.GET])
        def info() -> Response:
            """
            A Flask route method for retrieving information about the MagicMirror database.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing database information or an error message.
            """

            info = self.db.info()

            if info:
                return self.success(info)

            return self.failure("Failed to retrieve database info. See logs for details")
