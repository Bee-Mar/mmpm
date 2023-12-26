#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
from time import sleep
from typing import List

import socketio

from mmpm.constants import color
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.singleton import Singleton
from mmpm.utils import kill_pids_of_process, run_cmd

logger = MMPMLogFactory.get_logger(__name__)


class MagicMirrorClientFactory:
    """
    A factory class for creating SocketIO clients to interact with MagicMirror modules. It
    facilitates communication between MMPM and MagicMirror via websockets.
    """

    @staticmethod
    def create_client(event: str, data: dict, namespace: str = "/MMM-mmpm"):
        """
        Creates and configures a SocketIO client for communicating with MagicMirror modules.

        Parameters:
            event (str): The event name to emit to the MagicMirror module.
            data (dict): The data payload to send with the event.
            namespace (str): The namespace for the SocketIO connection.

        Returns:
            socketio.Client: Configured SocketIO client, or None on failure.
        """

        client = None

        if not event:
            logger.error("No event name provided")
            return client

        try:
            client = socketio.Client(reconnection=True, request_timeout=300)
        except socketio.exceptions.SocketIOError as error:
            logger.fatal(f"Failed to create SocketIO client: {error}")

        @client.on("connect", namespace=namespace)
        def connect():
            logger.debug(f"Connected to MagicMirror websocket in {namespace}")
            client.emit(event, namespace=namespace, data=data)
            logger.debug(f"Emitting {data}")

        @client.event
        def connect_error(error):
            logger.error("Failed to connect to MagicMirror websocket. Is the MMPM_MAGICMIRROR_URI environment variable set properly?")
            logger.debug(f"Error when connecting to MagicMirror websocket: {error}")

        @client.on("disconnect", namespace=namespace)
        def disconnect():
            logger.debug("Disconnected from MagicMirror websocket")

        @client.on("ACTIVE_MODULES", namespace=namespace)
        def active_modules(data):
            logger.debug("Received active modules from MMPM MagicMirror module")

            if not data:
                logger.error("No data was received. Is the MMPM_MAGICMIRROR_URI environment variable set properly?")

            for module in [json_data for index, json_data in enumerate(data) if json_data not in data[index + 1 :]]:
                print(f"{color.n_green(module['name'])}\n  hidden: {'true' if module['hidden'] else 'false'}\n  key: {module['key'] + 1}\n")

            logger.debug("Disconnecting from client")
            client.disconnect()

        @client.on("MODULES_TOGGLED", namespace=namespace)
        def modules_toggled(data):
            logger.debug("Received toggled modules from MMPM MagicMirror module")

            if not data:
                logger.error("Unable to find provided module(s)")

            logger.debug("Disconnecting from client")
            client.disconnect()

        return client


class MagicMirrorController(Singleton):
    """
    Controller class for managing and interacting with the MagicMirror application. It provides
    methods to start, stop, restart, and check the status of MagicMirror, as well as to show
    or hide specific modules.
    """

    def __init__(self):
        self.env = MMPMEnv()
        self.factory = MagicMirrorClientFactory()

    def status(self):
        """
        Checks the status of MagicMirror by attempting to connect to it using a SocketIO client.

        Returns:
            True if the connection is successful, False otherwise.
        """

        try:
            client = self.factory.create_client("FROM_MMPM_APP_get_active_modules", {})
            client.connect(self.env.MMPM_MAGICMIRROR_URI.get())
            return True
        except (OSError, BrokenPipeError, Exception) as error:
            logger.error(f"Failed to connect to MagicMirror, closing socket. Is MagicMirror running? : {error}")

        return False

    def hide(self, modules: List[str]):
        """
        Hides specified modules in MagicMirror using a SocketIO client.

        Parameters:
            modules (List[str]): List of module names or identifiers to hide.

        Returns:
            True if the operation is successful, False otherwise.
        """

        try:
            client = self.factory.create_client(
                "FROM_MMPM_APP_toggle_modules",
                {"directive": "hide", "modules": modules},
            )

            client.connect(self.env.MMPM_MAGICMIRROR_URI.get())
            logger.info(f"Hid modules with keys: {', '.join(modules)}")
            return True
        except (OSError, BrokenPipeError, Exception) as error:
            logger.error(f"Failed to connect to MagicMirror, closing socket. Is MagicMirror running? : {error}")

        return False

    def show(self, modules: List[str]):
        """
        Hides specified modules in MagicMirror using a SocketIO client.

        Parameters:
            modules (List[str]): List of module names or identifiers to hide.

        Returns:
            True if the operation is successful, False otherwise.
        """

        try:
            client = self.factory.create_client(
                "FROM_MMPM_APP_toggle_modules",
                data={"directive": "show", "modules": modules},
            )

            client.connect(self.env.MMPM_MAGICMIRROR_URI.get())
            logger.info(f"Made modules visible with keys: {', '.join(modules)}")
            return True
        except (OSError, BrokenPipeError, Exception) as error:
            logger.error(f"Failed to connect to MagicMirror, closing socket. Is MagicMirror running? : {error}")

        return False

    def start(self) -> bool:
        """
        Launches MagicMirror using pm2, if found, otherwise a 'npm start' is run as
        a background process

        Parameters:
            None

        Returns:
            True if the operation is successful, False otherwise.
        """
        command = ["npm", "run", "start"]

        pm2_process: str = self.env.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.get()
        compose_file: str = self.env.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.get()

        if compose_file:
            logger.debug(f"Docker compose file set as {compose_file}")
            command = ["docker", "compose", "-f", compose_file, "up", "-d"]
        elif pm2_process:
            logger.debug(f"pm2 process set as {pm2_process}")
            command = ["pm2", "start", pm2_process]

        if not shutil.which(command[0]):
            logger.error(f"{command[0]} not found in PATH. Unable to start MagicMirror")
            return False

        root = self.env.MMPM_MAGICMIRROR_ROOT.get()
        root.mkdir(exist_ok=True, parents=True)

        if not Path(root / "node_modules").exists():
            logger.error("MagicMirror dependencies have not been installed. Please run `mmpm mm-ctl --install` first.")
            return False

        os.chdir(root)

        logger.debug(f"Attempting to start MagicMirror using {' '.join(command)} ")
        error_code, _, stderr = run_cmd(
            command,
            message="Starting MagicMirror",
            background=bool(command[0] == "npm"),
        )

        if error_code:
            logger.error(stderr)
            return False

        logger.info("Started MagicMirror")
        return True

    def stop(self) -> bool:
        """
        Stops MagicMirror using pm2, if found, otherwise the associated
        processes are killed

        Parameters:
            None

        Returns:
            success (bool): True if successful, False if failure
        """

        command: List[str] = []

        pm2_process: str = self.env.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.get()
        compose_file: str = self.env.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.get()

        if compose_file:
            logger.debug(f"docker-compose file set as {compose_file}")
            command = ["docker", "compose", "-f", compose_file, "stop"]
        elif pm2_process:
            logger.debug(f"pm2 process set as {pm2_process}")
            command = ["pm2", "stop", pm2_process]

        if command and shutil.which(command[0]):
            logger.debug(f"Attempting to stop MagicMirror using '{command[0]}'")
            # pm2 and docker-compose cause stdout/stderr to flip
            error_code, _, stderr = run_cmd(command, message="Stopping MagicMirror")

            if error_code:
                logger.error(stderr)
                return False

            logger.debug(f"Stopped MagicMirror using '{command[0]}'")
            logger.info("Stopped MagicMirror")
            return True

        logger.debug("Stopping electron processes associated with MagicMirror")
        kill_pids_of_process("electron")
        logger.info("Stopped MagicMirror")
        return True

    def restart(self) -> bool:
        """
        Restarts MagicMirror using pm2, if found, otherwise the associated
        processes are killed and 'npm start' is re-run a background process

        Parameters:
            None

        Returns:
            success (bool): True if successful, False if failure
        """
        if not self.stop():
            return False

        sleep(2)

        if not self.start():
            return False

        return True
