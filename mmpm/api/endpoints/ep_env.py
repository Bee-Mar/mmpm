#!/usr/bin/env python3
import json

from flask import Blueprint, Response, request

from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import paths
from mmpm.env import MMPM_DEFAULT_ENV, MMPMEnv
from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)


class Env(Endpoint):
    """
    A Flask endpoint class for handling operations related to the MMPM environment settings,
    including retrieving the current environment, the default environment, and updating the environment settings.
    """

    def __init__(self):
        self.name = "env"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.env = MMPMEnv()

        @self.blueprint.route("/", methods=[http.GET])
        def retrieve() -> Response:
            """
            A Flask route method for retrieving the current MMPM environment settings.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing the current MMPM environment settings.
            """

            logger.info("Sending back current MMPM Env")
            return self.success(self.env.get())

        @self.blueprint.route("/default", methods=[http.GET])
        def default() -> Response:
            """
            A Flask route method for retrieving the default MMPM environment settings.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing the default MMPM environment settings.
            """

            logger.info("Sending back default MMPM Env")
            return self.success({key: str(value) for key, value in MMPM_DEFAULT_ENV.items()})

        @self.blueprint.route("/update", methods=[http.POST])
        def update() -> Response:
            """
            A Flask route method for updating MMPM environment settings.

            Parameters:
                None

            Returns:
                Response: A Flask Response object indicating the success or failure of the update operation.
            """

            updated_env = request.get_json()["env"]

            with open(paths.MMPM_ENV_FILE, "w", encoding="utf-8") as env:
                try:
                    json.dump(updated_env, env, indent=2)
                except Exception as error:
                    message = f"Failed to updated env: {error}"
                    logger.error(message)
                    return self.failure(message)

            logger.info(f"Updating MMPM Env with {updated_env}")
            return self.success({"updated": True})
