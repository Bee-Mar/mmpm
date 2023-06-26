#!/usr/bin/env python3
from typing import Any
from mmpm.logger import MMPMLogger
from flask import jsonify, Response, abort

logger = MMPMLogger.get_logger(__name__)

class BaseEndpoint:
    def success(self, message: Any) -> Response:
        return jsonify({"code": 200, "message": message})

    def failure(self, code: int, message: Any) -> Response:
        logger.error(message)
        abort(code, message)

