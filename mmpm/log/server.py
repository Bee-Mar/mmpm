#!/usr/bin/env python3
"""
An incredibly simplistic SocketIO server used for repeating logs from the MMPM CLI to the UI.
"""

from gevent import monkey

monkey.patch_all()

import socketio
from gevent.pywsgi import WSGIServer
from mmpm.log.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)

# Function to create the SocketIO server
def create_app():
    sio = socketio.Server(cors_allowed_origins="*", async_mode="gevent")

    @sio.event
    def connect(sid, environ):
        logger.debug(f"Client connected to SocketIO-Log-Server: {sid}")

    @sio.event
    def logs(sid, data):
        sio.emit("logs", data, skip_sid=sid)

    @sio.event
    def disconnect(sid):
        logger.debug("Client disconnected:", sid)

    app = socketio.WSGIApp(sio)
    return app
