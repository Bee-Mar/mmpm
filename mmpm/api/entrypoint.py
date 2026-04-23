from gevent import monkey

monkey.patch_all()

import importlib.resources as pkg_resources
import json
import os

from flask import Flask, Response, request, send_from_directory
from flask_cors import CORS

import mmpm.api.endpoints
from mmpm.api.endpoints.index import Index
from mmpm.constants import urls
from mmpm.log.factory import MMPMLogFactory
from mmpm.subcommands.loader import Loader

logger = MMPMLogFactory.get_logger(__name__)

app = Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"
CORS(app)

resources: dict = {
    r"/*": {"origins": "*"},
    r"/api/*": {"origins": "*"},
    r"/socket.io/*": {"origins": "*"},
}


@app.after_request  # type: ignore
def after_request(response: Response) -> Response:
    """
    Appends extra headers after each api request is sent to the server

    Parameters:
        response (flask.Response): the response object being returned to the frontend

    Returns
        response (flask.Response): the modified response object with new headers attached
    """

    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.errorhandler(Exception)
def exception_handler(error) -> Response:
    response: Response = error.get_response()
    response.data = json.dumps({"code": error.code, "message": error.description})
    response.content_type = "application/json"
    logger.error(error.description)
    return response


# dynamically load all the endpoints within the "mmpm.api.endpoints" module
loader = Loader(
    module_path=mmpm.api.endpoints.__path__,
    module_name="mmpm.api.endpoints",
    prefix="ep_",
)

app.url_map.strict_slashes = False

entrypoints = list(loader.objects.values())
entrypoints.append(Index(app.url_map))

for endpoint in entrypoints:
    try:
        app.register_blueprint(endpoint.blueprint)  # type: ignore
        logger.debug(f"Loaded blueprint for {endpoint}")
    except Exception as exception:
        logger.error(f"Failed to load blueprint for {endpoint}: {exception}")

_ui_path = str(pkg_resources.files("mmpm").joinpath("ui"))


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_ui(path: str) -> Response:
    full_path = os.path.join(_ui_path, path)

    if path and os.path.isfile(full_path):
        return send_from_directory(_ui_path, path)  # type: ignore

    api_base = os.environ.get("MMPM_UI_API_BASE_URL", "")
    hostname = request.host.split(":")[0]
    default_socket_url = f"http://{hostname}:{urls.MMPM_REPEATER_SERVER_PORT}"
    socket_url = os.environ.get("MMPM_UI_SOCKET_URL", default_socket_url)

    config_script = f'<script>window.MMPM_CONFIG={{"apiBase":"{api_base}","socketUrl":"{socket_url}"}};</script>'

    index_path = os.path.join(_ui_path, "index.html")

    with open(index_path, encoding="utf-8") as fh:
        html = fh.read()

    return Response(html.replace("</head>", f"{config_script}</head>", 1), mimetype="text/html")
