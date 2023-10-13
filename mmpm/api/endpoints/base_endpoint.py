#!/usr/bin/env python3
from mmpm.logger import MMPMLogger

from flask import Response, jsonify

import json

logger = MMPMLogger.get_logger(__name__)

class BaseEndpoint:

    def __init__(self):
        pass

    def success(msg: str) -> Response:
        return jsonify({"code": 200, "message": msg})

    def failure(msg: str, code: int = 500) -> Response:
        return jsonify({"code": code, "message": msg})
