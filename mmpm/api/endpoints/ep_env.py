#!/usr/bin/env python3
from mmpm.logger import MMPMLogger
from mmpm.api.endpoints.base_endpoint import BaseEndpoint
from mmpm.api.constants import http
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.constants import paths
from mmpm.env import MMPM_DEFAULT_ENV

from flask import Blueprint, Response, request

import json

logger = MMPMLogger.get_logger(__name__)

class Endpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()
        self.blueprint = Blueprint("env", __name__, url_prefix="/api/env")


        @self.blueprint.route("/default", methods=[http.GET])
        def default() -> Response:
            logger.info("Sending back default MMPM Env")
            return self.success(json.dumps(MMPM_DEFAULT_ENV))


        @self.blueprint.route("/retrieve", methods=[http.GET])
        def retrieve() -> Response:
            logger.info("Sending back current MMPM Env")
            return self.success(json.dumps(self.env.get()))


        @self.blueprint.route("update", methods=[http.POST])
        def update() -> Response:
            updated_env = request.get_json()["env"]

            with open(paths.MMPM_ENV_FILE, "w", encoding="utf-8") as env:
                try:
                    json.dump(updated_env, env, indent=2)
                except Exception as error:
                    message = f"Failed to updated env: {error}"
                    logger.error(message)
                    return self.failure(500, message)

            logger.info(f"Updating MMPM Env with {updated_env}")
            return self.success(json.dumps(self.env.get()))
