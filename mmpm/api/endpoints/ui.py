import importlib.resources as pkg_resources
import os

from flask import Blueprint, Response, request, send_from_directory

from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import urls
from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)

_ui_path = str(pkg_resources.files("mmpm").joinpath("ui"))


class UI(Endpoint):
    """
    Catch-all endpoint that serves the Angular SPA and injects runtime config
    (window.MMPM_CONFIG) into index.html so the pre-built bundle works behind
    a reverse proxy without rebuilding. Set MMPM_UI_API_BASE_URL and
    MMPM_UI_SOCKET_URL environment variables to configure the proxy URLs.
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

            api_base = os.environ.get("MMPM_UI_API_BASE_URL", "")
            hostname = request.host.split(":")[0]
            default_socket_url = f"http://{hostname}:{urls.MMPM_REPEATER_SERVER_PORT}"
            socket_url = os.environ.get("MMPM_UI_SOCKET_URL", default_socket_url)

            config_script = f'<script>window.MMPM_CONFIG={{"apiBase":"{api_base}","socketUrl":"{socket_url}"}};</script>'

            with open(os.path.join(_ui_path, "index.html"), encoding="utf-8") as fh:
                html = fh.read()

            return Response(
                html.replace("</head>", f"{config_script}</head>", 1),
                mimetype="text/html",
            )
