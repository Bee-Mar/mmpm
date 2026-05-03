"""
An incredibly simplistic SocketIO server used for repeating logs from the MMPM CLI to the UI.
"""

from collections import deque

from gevent import monkey

monkey.patch_all()

import socketio

from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)


def create():
    server = socketio.Server(cors_allowed_origins="*", async_mode="gevent")
    log_buffer: deque = deque(maxlen=500)

    @server.event
    def connect(sid, environ):  # pylint: disable=unused-argument
        logger.debug(f"Client connected to SocketIO-Log-Server: {sid}")
        for entry in log_buffer:
            server.emit("logs", entry, to=sid)

    @server.event
    def logs(sid, data):
        log_buffer.append(data)
        server.emit("logs", data, skip_sid=sid)

    @server.event
    def disconnect(sid):
        logger.debug("Client disconnected:", sid)

    app = socketio.WSGIApp(server)
    return app
