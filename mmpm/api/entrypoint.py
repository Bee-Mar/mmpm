#!/usr/bin/env python3
from gevent import monkey

monkey.patch_all()

import json
from importlib import import_module
from pkgutil import iter_modules

import mmpm.api.endpoints
from flask import Flask, Response
from flask_cors import CORS
from mmpm.api.endpoints.index import Index
from mmpm.logger import MMPMLogger
from mmpm.subcommands.loader import Loader

logger = MMPMLogger.get_logger(__name__)

app = Flask(__name__, root_path="/var/www/mmpm", static_url_path="")
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
path = mmpm.api.endpoints.__path__
loader = Loader(module_path=path, module_name="mmpm.api.endpoints", prefix="ep_")

for endpoint in loader.objects.values():
    logger.info(f"Loading blueprint for {endpoint}")
    app.register_blueprint(endpoint.blueprint)

app.register_blueprint(Index(app.url_map).blueprint)
