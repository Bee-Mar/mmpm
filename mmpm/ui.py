#!/usr/bin/env python3
import sys

if sys.version_info < (3, 9):
    import importlib_resources as pkg_resources
else:
    import importlib.resources as pkg_resources

import json
import os
from pathlib import Path
from shutil import rmtree, which
from sys import executable

from mmpm.__version__ import version
from mmpm.constants import urls
from mmpm.log.factory import MMPMLogFactory
from mmpm.singleton import Singleton
from mmpm.utils import run_cmd

logger = MMPMLogFactory.get_logger(__name__)


class MMPMui(Singleton):
    """
    Class responsible for managing the MMPM user interface. It provides methods to control and monitor
    the MMPM UI application, including starting, stopping, installing, and removing the UI.
    """

    def __init__(self):
        python = executable
        gunicorn = which("gunicorn") or f"{python} -m gunicorn"
        namespace = "mmpm"

        self.pm2_config_path = Path("/tmp/mmpm/ecosystem.json")

        self.pm2_ecosystem_config = {
            "apps": [
                {
                    "namespace": namespace,
                    "name": f"{namespace}.api",
                    "script": f"{gunicorn} -k gevent -b 0.0.0.0:{urls.MMPM_API_SERVER_PORT} mmpm.wsgi:app",
                    "version": version,
                    "watch": True,
                },
                {
                    "namespace": namespace,
                    "name": f"{namespace}.log-server",
                    "script": f"{gunicorn} -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 'mmpm.log.server:create()' -b 0.0.0.0:{urls.MMPM_LOG_SERVER_PORT}",
                    "version": version,
                    "watch": True,
                },
                {
                    "namespace": namespace,
                    "name": f"{namespace}.repeater",
                    "script": f"{gunicorn} -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 'mmpm.api.repeater:create()' -b 0.0.0.0:{urls.MMPM_REPEATER_SERVER_PORT}",
                    "version": version,
                    "watch": True,
                },
                {
                    "namespace": namespace,
                    "name": f"{namespace}.ui",
                    "script": f"{python} -m http.server -d {pkg_resources.files('mmpm').resolve() / 'ui'} -b 0.0.0.0 {urls.MMPM_UI_PORT}",
                    "version": version,
                    "watch": True,
                },
            ]
        }

    def create_pm2_config(self):
        """
        Creates the PM2 configuration file for MMPM if it does not already exist. This configuration
        file is used to manage the MMPM UI processes.

        Parameters:
            None

        Returns:
            None
        """

        if self.pm2_config_path.exists():
            logger.debug(f"{self.pm2_config_path} exists. Nothing to do.")
            return

        logger.debug(f"Creating {self.pm2_config_path} file")
        self.pm2_config_path.parent.mkdir(exist_ok=True)
        self.pm2_config_path.touch(exist_ok=True)

        with open(self.pm2_config_path, mode="w", encoding="utf-8") as config:
            logger.debug(f"Writing PM2 Configuration to {self.pm2_config_path}")
            json.dump(self.pm2_ecosystem_config, config)

    def stop(self):
        """
        Stops the MMPM UI application using PM2.

        Parameters:
            None

        Returns:
            A tuple containing the process exit code, stdout, and stderr.
        """

        return run_cmd(["pm2", "stop", f"{self.pm2_config_path}"], message="Stopping MMPM UI")

    def delete(self):
        """
        Deletes the MMPM UI application from PM2's process list.

        Parameters:
            None

        Returns:
            A tuple containing the process exit code, stdout, and stderr.
        """

        return run_cmd(["pm2", "delete", f"{self.pm2_config_path}"], message="Removing MMPM UI")

    def start(self):
        """
        Starts the MMPM UI application using PM2.

        Parameters:
            None

        Returns:
            A tuple containing the process exit code, stdout, and stderr.
        """

        return run_cmd(["pm2", "start", f"{self.pm2_config_path}"], message="Installing MMPM UI")

    def install(self) -> bool:
        """
        Installs the MMPM UI by setting up necessary configurations and services. It creates the PM2
        configuration file and starts the MMPM UI application. If PM2 is not installed, logs a fatal error.

        Parameters:
            None

        Returns:
            True if the installation is successful, False otherwise.
        """

        if not which("pm2"):
            logger.fatal("pm2 is not in your PATH. Please run `npm install -g pm2`, and run the UI installation again.")
            return False

        self.create_pm2_config()
        error_code, _, stderr = self.start()

        if error_code:
            logger.error(f"Failed to install MMPM UI: {stderr}")
            return False

        return True

    def status(self) -> None:
        """
        Displays the current status of the MMPM UI processes using PM2.

        Parameters:
            None

        Returns:
            None
        """
        self.create_pm2_config()
        os.system("pm2 list mmpm")

    def remove(self) -> bool:
        """
        Removes the MMPM UI by stopping and deleting its processes from PM2 and cleaning up configuration
        files. Logs a fatal error if PM2 is not installed.

        Returns:
            True if the removal is successful, False otherwise.
        """
        if not which("pm2"):
            logger.fatal("pm2 is not in your PATH. Please run `npm install -g pm2`, and run the UI installation again.")
            return False

        self.create_pm2_config()
        error_code, _, stderr = self.delete()

        if error_code:
            logger.error(stderr)
            return False

        rmtree(self.pm2_config_path.parent, ignore_errors=True)
        return True
