from flask import Blueprint, Response

from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.doctor import FAIL, WARN
from mmpm.doctor import Doctor as MMPMDoctor
from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)


class Doctor(Endpoint):
    """
    A Flask endpoint for running the read-only MMPM diagnostics (the same checks
    as the 'mmpm doctor' CLI subcommand).
    """

    def __init__(self):
        self.name = "doctor"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.doctor = MMPMDoctor()

        @self.blueprint.route("/run", methods=[http.GET])
        def run() -> Response:
            """
            A Flask route method for running all diagnostic checks.

            Parameters:
                None

            Returns:
                Response: A Flask Response object containing the diagnostic results and summary counts.
            """

            logger.info("Received request to run doctor diagnostics")
            results = self.doctor.run()

            return self.success({
                "results": results,
                "failures": sum(result["status"] == FAIL for result in results),
                "warnings": sum(result["status"] == WARN for result in results),
            })
