#!/usr/bin/env python3
from gevent import monkey

monkey.patch_all()

import socketio
from mmpm.env import MMPMEnv
from mmpm.log.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)

def create_app():
    server = socketio.Server(cors_allowed_origins="*", async_mode="gevent")
    app = socketio.WSGIApp(server)
    env = MMPMEnv()
    client = socketio.Client(request_timeout=300)
    client_ids = set()

    def create_connection(sid):
        try:
            client.connect(env.MMPM_MAGICMIRROR_URI.get())

            if sid not in client_ids:
                client_ids.add(sid)
        except Exception as error:
            logger.error(error)

    @server.event
    def connect(sid, environ):
        logger.debug(f"Client connected to SocketIO-Repeater: {sid}")

        if not client.connected:
            create_connection(sid)

        if client.connected:
            logger.debug(f"SocketIO-Repeater connected to MagicMirror SocketIO server: {client.connected}")
            client.emit("FROM_MMPM_APP_get_active_modules", namespace="/MMM-mmpm", data={})

            logger.debug("Emitted data request to MagicMirror SocketIO server")

    @server.event
    def disconnect(sid):
        logger.debug(f"Client disconnected: {sid}")

        if sid in client_ids:
            client_ids.remove(sid)

    @server.event
    def error(sid):
        logger.debug(f"Client encountered error: {sid}")

        client.disconnect()
        client_ids = set()

        create_connection()

    # Event handler for receiving data from server2
    @client.on("ACTIVE_MODULES", namespace="/MMM-mmpm")
    def active_modules(data):
        logger.debug(f"Received data from MagicMirror SocketIO Server: {data}")

        for client_id in client_ids:
            logger.debug(f"Repeating data to {client_id}")
            server.emit("modules", data=data, to=client_id)

    # Event handler for receiving data from server2
    @client.on("MODULES_TOGGLED", namespace="/MMM-mmpm")
    def modules_toggled(data):
        logger.debug(f"Received toggled modules from MagicMirror SocketIO Server: {data}")
        client.emit("FROM_MMPM_APP_get_active_modules", namespace="/MMM-mmpm", data={})

    return app
