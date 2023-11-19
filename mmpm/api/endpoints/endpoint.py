#!/usr/bin/env python3
import json

from flask import Response, jsonify
from mmpm.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)


class Endpoint:
    def __init__(self):
        self.name: str = ""

    def success(msg: str) -> Response:
        return jsonify({"code": 200, "message": msg})

    def failure(msg: str, code: int = 500) -> Response:
        return jsonify({"code": code, "message": msg})
