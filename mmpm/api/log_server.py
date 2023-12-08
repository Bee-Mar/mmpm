#!/usr/bin/env python3
"""
An incredibly simplistic SocketIO server used for repeating logs from the MMPM CLI to the UI.
"""

from gevent import monkey

monkey.patch_all()

import socketio
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from mmpm.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)


def setup_server():
    server = socketio.Server(cors_allowed_origins="*", async_mode="gevent")

    @server.event
    def connect(sid, environ):
        logger.debug("Client connected:", sid)

    @server.event
    def logs(sid, data):
        server.emit("logs", data, skip_sid=sid)

    @server.event
    def disconnect(sid):
        logger.debug("Client disconnected:", sid)

    return server


if __name__ == "__main__":
    server = setup_server()
    logger.debug("Setup SocketIO log server")

    app = socketio.WSGIApp(server)
    logger.debug("Setup log server WSGI Application")

    logger.debug("Starting log server")

    try:
        pywsgi.WSGIServer(("", 6789), app, handler_class=WebSocketHandler).serve_forever()
    except KeyboardInterrupt:
        logger.debug("Log server stopped by CTRL-C")
