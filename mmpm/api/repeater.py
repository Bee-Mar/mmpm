#!/usr/bin/env python3
"""
This socketio server/client repeats the information collected by the MMM-mmpm module back to the UI. MagicMirror
has network settings which prevent the UI from directly interacting with MMM-mmpm if you open up the UI on a computer
other than the one hosting MMPM. It's weird, it's annoying, but it's the workaround for it. Maybe there will be simpler
solution later on, but for now this is what works. Otherwise, users would need to be told how to modify MagicMirror's
source code, and let's face it, practically nobody is going to want to do that. The other option is to make a PR to MagicMirror
but I'm sure it won't get accepted for security purposes.
"""
from gevent import monkey

monkey.patch_all()

from time import sleep

import socketio
from mmpm.env import MMPMEnv
from mmpm.log.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)

def create():
    server = socketio.Server(cors_allowed_origins="*", async_mode="gevent")
    app = socketio.WSGIApp(server)
    env = MMPMEnv()
    client = socketio.Client(request_timeout=300)
    client_ids = set()

    def create_connection(sid):
        try:
            client.connect(env.MMPM_MAGICMIRROR_URI.get(), wait_timeout=10, wait=True)

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

        client.disconnect()

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
