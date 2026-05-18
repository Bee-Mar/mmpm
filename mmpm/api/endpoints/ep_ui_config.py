import json

from flask import Blueprint, Response, request

from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import urls
from mmpm.env import MMPMEnv


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
            hostname = request.host.split(":")[0]
            default_socket_url = f"http://{hostname}:{urls.MMPM_REPEATER_SERVER_PORT}"
            socket_url = env.MMPM_UI_SOCKET_URL.get() or default_socket_url
            config = {
                "apiBase": env.MMPM_UI_API_BASE_URL.get(),
                "socketUrl": socket_url,
                "baseUrl": env.MMPM_UI_BASE_URL.get(),
            }
            return Response(
                f"window.MMPM_CONFIG={json.dumps(config)};",
                mimetype="application/javascript",
            )
