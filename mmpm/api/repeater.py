#!/usr/bin/env python3
from gevent import monkey

monkey.patch_all()

import socketio
from mmpm.env import MMPMEnv
from mmpm.log.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)

# Use the synchronous version of SocketIO
sio = socketio.Server(cors_allowed_origins="*", async_mode="gevent")

def create_app():
    app = socketio.WSGIApp(sio)
    env = MMPMEnv()
    client_sio = socketio.Client(request_timeout=300)
    client_ids = set()

    @sio.event
    def connect(sid, environ):
        logger.debug(f"Client connected to SocketIO-Repeater: {sid}")

        if sid not in client_ids:
            client_ids.add(sid)

            if not client_sio.connected:
                client_sio.connect(env.MMPM_MAGICMIRROR_URI.get())

        logger.debug(f"SocketIO-Repeater connected to MagicMirror SocketIO server: {client_sio.connected}")
        client_sio.emit("FROM_MMPM_APP_get_active_modules", namespace="/MMM-mmpm", data={})

        logger.debug("Emitted data request to MagicMirror SocketIO server")

    @sio.event
    def disconnect(sid):
        logger.debug(f"Client disconnected: {sid}")

        if sid in client_ids:
            client_ids.remove(sid)

    @sio.event
    def error(sid):
        logger.debug(f"Client encountered error: {sid}")
        client_sio.disconnect()
        client_ids = set()
        client_sio.connect(env.MMPM_MAGICMIRROR_URI.get())

    # Event handler for receiving data from server2
    @client_sio.on("ACTIVE_MODULES", namespace="/MMM-mmpm")
    def active_modules(data):
        logger.debug(f"Received data from MagicMirror SocketIO Server: {data}")

        for client_id in client_ids:
            logger.debug(f"Repeating data to {client_id}")
            sio.emit("modules", data=data, to=client_id)

    # Event handler for receiving data from server2
    @client_sio.on("MODULES_TOGGLED", namespace="/MMM-mmpm")
    def modules_toggled(data):
        logger.debug(f"Received toggled modules from MagicMirror SocketIO Server: {data}")
        client_sio.emit("FROM_MMPM_APP_get_active_modules", namespace="/MMM-mmpm", data={})

    return app
