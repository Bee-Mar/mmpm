import json

from flask import Blueprint, Response

from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)


class UiConfig(Endpoint):
    """
    Serves window.MMPM_CONFIG as a JavaScript snippet so static file servers
    can serve index.html without needing HTML injection. index.html loads this
    via <script src="api/ui-config">.
    """

    def __init__(self):
        super().__init__()
        self.name = "ui_config"
        self.blueprint = Blueprint(self.name, __name__)

        @self.blueprint.route("/api/ui-config", methods=["GET"])
        def ui_config() -> Response:
            env = MMPMEnv()
            config = {
                "apiBase": env.MMPM_UI_API_BASE_URL.get(),
                "socketUrl": env.MMPM_UI_SOCKET_URL.get(),
                "baseUrl": env.MMPM_UI_BASE_URL.get(),
            }
            return Response(
                f"window.MMPM_CONFIG={json.dumps(config)};",
                mimetype="application/javascript",
            )
