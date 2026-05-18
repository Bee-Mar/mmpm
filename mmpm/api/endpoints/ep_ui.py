import importlib.resources as pkg_resources
import os
from urllib.parse import urlparse

from flask import Blueprint, Response, request, send_from_directory

from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import urls
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)

_ui_path = str(pkg_resources.files("mmpm").joinpath("ui"))


class Ui(Endpoint):
    """
    Catch-all endpoint that serves the Angular SPA and injects runtime config
    (window.MMPM_CONFIG) into index.html so the pre-built bundle works behind
    a reverse proxy without rebuilding. Configure MMPM_UI_API_BASE_URL,
    MMPM_UI_SOCKET_URL, and MMPM_UI_BASE_URL in the MMPM env file
    (~/.config/mmpm/mmpm-env.json).
    """

    def __init__(self):
        super().__init__()
        self.name = "ui"
        self.blueprint = Blueprint(self.name, __name__)

        @self.blueprint.route("/", defaults={"path": ""})
        @self.blueprint.route("/<path:path>")
        def serve(path: str) -> Response:
            full_path = os.path.join(_ui_path, path)

            if path and os.path.isfile(full_path):
                return send_from_directory(_ui_path, path)  # type: ignore

            env = MMPMEnv()
            api_base = env.MMPM_UI_API_BASE_URL.get()
            hostname = request.host.split(":")[0]
            default_socket_url = f"http://{hostname}:{urls.MMPM_REPEATER_SERVER_PORT}"
            socket_url = env.MMPM_UI_SOCKET_URL.get() or default_socket_url
            base_url = env.MMPM_UI_BASE_URL.get()

            config_script = f'<script>window.MMPM_CONFIG={{"apiBase":"{api_base}","socketUrl":"{socket_url}","baseUrl":"{base_url}"}};</script>'

            with open(os.path.join(_ui_path, "index.html"), encoding="utf-8") as fh:
                html = fh.read()

            if base_url:
                base_href = urlparse(base_url).path.rstrip("/") + "/"
                html = html.replace('<base href="/">', f'<base href="{base_href}">', 1)

            return Response(
                html.replace("</head>", f"{config_script}</head>", 1),
                mimetype="text/html",
            )
