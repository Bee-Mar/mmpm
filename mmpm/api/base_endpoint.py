#!/usr/bin/env python3
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.env import MMPMEnv

from typing import Any
from flask import jsonify, Response, abort

logger = MMPMLogger.get_logger(__name__)

class BaseEndpoint:
    def __init__(self):
        self.db = MagicMirrorDatabase()
        self.env = MMPMEnv()

    def success(self, message: Any) -> Response:
        return jsonify({"code": 200, "message": message})

    def failure(self, code: int, message: Any) -> Response:
        logger.error(message)
        abort(code, message)

