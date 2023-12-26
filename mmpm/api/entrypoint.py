#!/usr/bin/env python3
from gevent import monkey

monkey.patch_all()

import json

from flask import Flask, Response
from flask_cors import CORS

import mmpm.api.endpoints
from mmpm.api.endpoints.index import Index
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
