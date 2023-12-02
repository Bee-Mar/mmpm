#!/usr/bin/env python3
import json
import os
import shutil
from time import sleep
from typing import List

import socketio
from mmpm.constants import color
from mmpm.env import MMPMEnv
from mmpm.logger import MMPMLogger
from mmpm.singleton import Singleton
from mmpm.utils import get_pids, kill_pids_of_process, run_cmd
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import JsonLexer

logger = MMPMLogger.get_logger(__name__)


class MagicMirrorClientFactory:
    @staticmethod
    def create_client(event: str, data: dict, namespace: str = "/MMM-mmpm"):
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
            logger.error(f"Failed to connect to MagicMirror websocket. Is the MMPM_MAGICMIRROR_URI environment variable set properly?")
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
    def __init__(self):
        self.env = MMPMEnv()
        self.factory = MagicMirrorClientFactory()

    def status(self):
        client = self.factory.create_client("FROM_MMPM_APP_get_active_modules", {})

        try:
            client.connect(self.env.MMPM_MAGICMIRROR_URI.get())
        except (OSError, BrokenPipeError, Exception) as error:
            logger.error(f"Failed to connect to MagicMirror, closing socket. Is MagicMirror running? : {error}")

    def hide_modules(self, modules_to_hide):
        client = self.factory.create_client("FROM_MMPM_APP_toggle_modules", {"directive": "hide", "modules": modules_to_hide})

        try:
            client.connect(self.env.MMPM_MAGICMIRROR_URI.get())
        except (OSError, BrokenPipeError, Exception) as error:
            logger.error(f"Failed to connect to MagicMirror, closing socket. Is MagicMirror running? : {error}")

    def show_modules(self, modules_to_show):
        client = self.factory.create_client("FROM_MMPM_APP_toggle_modules", data={"directive": "show", "modules": modules_to_show})

        try:
            client.connect(self.env.MMPM_MAGICMIRROR_URI.get())
        except (OSError, BrokenPipeError, Exception) as error:
            logger.error(f"Failed to connect to MagicMirror, closing socket. Is MagicMirror running? : {error}")

    def start(self):
        """
        Launches MagicMirror using pm2, if found, otherwise a 'npm start' is run as
        a background process

        Parameters:
            None

        Returns:
            None
        """
        logger.info("Starting MagicMirror")

        process: str = ""
        command: List[str] = []

        MMPM_MAGICMIRROR_PM2_PROCESS_NAME: str = self.env.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.get()
        MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: str = self.env.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.get()

        if MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE:
            logger.debug(f"docker-compose file set as {MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE}")

        if MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
            logger.debug(f"pm2 process set as {MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE}")

        if shutil.which("pm2") and MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
            command = ["pm2", "start", MMPM_MAGICMIRROR_PM2_PROCESS_NAME]
            process = "pm2"

        elif shutil.which("docker-compose") and MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE:
            command = ["docker-compose", "-f", MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE, "up", "-d"]
            process = "docker-compose"

        if command and process:
            logger.debug(f"Starting MagicMirror using {command[0]} ")
            error_code, stderr, _ = run_cmd(command, progress=False, background=True)

            if error_code:
                logger.error(stderr.strip())
                return False

            logger.debug(f"Started MagicMirror using '{process}'")
            return True

        os.chdir(self.env.MMPM_MAGICMIRROR_ROOT.get())

        command = ["npm", "run", "start"]
        logger.debug(f"Starting Magicmirror using `{' '.join(command)}`")

        run_cmd(command, progress=False, background=True)
        return True

    def stop(self):
        """
        Stops MagicMirror using pm2, if found, otherwise the associated
        processes are killed

        Parameters:
            None

        Returns:
            success (bool): True if successful, False if failure
        """

        process: str = ""
        command: List[str] = []

        MMPM_MAGICMIRROR_PM2_PROCESS_NAME: str = self.env.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.get()
        MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: str = self.env.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.get()

        if MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE:
            logger.debug(f"docker-compose file set as {MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE}")

        if MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
            logger.debug(f"pm2 process set as {MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE}")

        if shutil.which("pm2") and MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
            command = ["pm2", "stop", MMPM_MAGICMIRROR_PM2_PROCESS_NAME]
            process = "pm2"

        elif shutil.which("docker-compose") and MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE:
            command = ["docker-compose", "-f", MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE, "stop"]
            process = "docker-compose"

        logger.debug("Stopping MagicMirror ")

        if command and process:
            logger.debug(f"Using '{process}' to stop MagicMirror")
            # pm2 and docker-compose cause the output to flip
            error_code, stderr, _ = run_cmd(command, progress=False, background=True)

            if error_code:
                logger.error(stderr.strip())
                return False

            logger.debug(f"Stopped MagicMirror using '{process}'")
            return True

        processes = ["electron"]

        logger.debug(f"Killing processes associated with MagicMirror: {processes}")

        for process in processes:
            kill_pids_of_process(process)
            logger.debug(f"Killed pids of process {process}")

        return True

    def restart(self):
        """
        Restarts MagicMirror using pm2, if found, otherwise the associated
        processes are killed and 'npm start' is re-run a background process

        Parameters:
            None

        Returns:
            None
        """
        self.stop()
        sleep(2)
        self.start()

    def is_running(self):
        """
        The status of MagicMirror running is determined by the presence of certain
        types of processes running. If those are found, it's assumed to be running,
        otherwise, not

        Parameters:
            None

        Returns:
            running (bool): True if running, False if not
        """
        return bool(get_pids("electron") or get_pids("pm2"))
