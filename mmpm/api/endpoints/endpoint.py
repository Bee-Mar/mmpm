#!/usr/bin/env python3
from typing import Any

from flask import Response, jsonify

from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)


class Endpoint:
    """
    A class representing a web endpoint in a Flask application. It provides methods
    to generate standard success and failure responses.
    """

    def __init__(self):
        """
        Initializes the Endpoint instance with an empty name.
        """
        self.name: str = ""

    def success(self, msg: Any) -> Response:
        """
        Generates a success response for the endpoint.

        Parameters:
            msg (Any): The message or data to be included in the response.

        Returns:
            Response: A Flask Response object with a 200 status code and the provided message.
        """
        return jsonify({"code": 200, "message": msg})

    def failure(self, msg: Any, code: int = 500) -> Response:
        """
        Generates a failure response for the endpoint.

        Parameters:
            msg (Any): The error message or data to be included in the response.
            code (int, optional): The HTTP status code for the response. Defaults to 500.

        Returns:
            Response: A Flask Response object with the specified status code and the provided message.
        """
        return jsonify({"code": code, "message": msg})
