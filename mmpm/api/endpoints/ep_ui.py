import importlib.resources as pkg_resources
import os
import re
from urllib.parse import urlparse

from flask import Blueprint, Response, send_from_directory

from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)

_ui_path = str(pkg_resources.files("mmpm").joinpath("ui"))


class Ui(Endpoint):
    """
    Catch-all endpoint that serves the Angular SPA. Rewrites <base href> in
    index.html when MMPM_UI_BASE_URL is set so assets and routing resolve
    correctly behind a reverse proxy. window.MMPM_CONFIG is served separately
    by ep_ui_config.py and loaded via a <script src> tag in index.html.
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
            base_url = env.MMPM_UI_BASE_URL.get()

            with open(os.path.join(_ui_path, "index.html"), encoding="utf-8") as fh:
                html = fh.read()

            if base_url:
                base_href = urlparse(base_url).path.rstrip("/") + "/"
                html = re.sub(r'<base href="/"[^>]*>', f'<base href="{base_href}">', html, count=1)

            return Response(html, mimetype="text/html")
