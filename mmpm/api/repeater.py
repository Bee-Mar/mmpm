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
from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)


def create():
    server = socketio.Server(cors_allowed_origins="*", async_mode="gevent", logger=logger)
    app = socketio.WSGIApp(server)
    env = MMPMEnv()
    mm_client = socketio.Client(request_timeout=300, logger=logger)
    client_ids = set()

    def setup_mm_client():
        attempt = 0
        max_retries = 250

        logger.debug("Attempting to connect to MagicMirror SocketIO server. Using a maximum of 250 retries")

        while attempt < max_retries and not mm_client.connected:
            try:
                mm_client.connect(env.MMPM_MAGICMIRROR_URI.get(), wait_timeout=10, wait=True)
                logger.debug("Successfully connected to the MagicMirror SocketIO server")
                break  # Connection successful, break out of the loop
            except Exception:
                attempt += 1
                sleep(1)

        if attempt == max_retries:
            logger.error("Maximum retry attempts reached, failed to connect.")

    @server.on("reconnect")
    @server.on("connect")
    def connect(sid, environ):  # pylint: disable=unused-argument
        logger.debug(f"Client connected to SocketIO-Repeater: {sid}")

        if sid not in client_ids:
            logger.debug(f"Added {sid} to known Client IDs")
            client_ids.add(sid)

        if not mm_client.connected:
            setup_mm_client()

    @server.event
    def disconnect(sid):
        logger.debug(f"Client disconnected: {sid}")

        if sid in client_ids:
            logger.debug(f"Removed {sid} from known Client IDs")
            client_ids.remove(sid)

        if not client_ids:
            logger.debug("No clients connected. Disconnecting from MagicMirror SocketIO Server.")
            mm_client.disconnect()

    @server.event
    def request_modules(sid):  # pylint: disable=unused-argument
        logger.debug(f"SocketIO-Repeater connected to MagicMirror SocketIO server: {mm_client.connected}")
        mm_client.emit("FROM_MMPM_APP_get_active_modules", namespace="/MMM-mmpm", data={})
        logger.debug("Emitted data request to MagicMirror SocketIO server")

    @server.event
    def error(sid):
        logger.debug(f"Client encountered error: {sid}")

    # Event handler for receiving data from server2
    @mm_client.on("ACTIVE_MODULES", namespace="/MMM-mmpm")
    def active_modules(data):
        logger.debug(f"Received data from MagicMirror SocketIO Server: {data}")

        for client_id in client_ids:
            logger.debug(f"Repeating data to {client_id}")
            server.emit("modules", data=data, to=client_id)

    # Event handler for receiving data from server2
    @mm_client.on("MODULES_TOGGLED", namespace="/MMM-mmpm")
    def modules_toggled(data):
        logger.debug(f"Received toggled modules from MagicMirror SocketIO Server: {data}")

        for client_id in client_ids:
            logger.debug(f"Repeating data to {client_id}")
            server.emit("modules", data=data, to=client_id)

    return app
