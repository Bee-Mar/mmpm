#!/usr/bin/env python3
import getpass
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from re import findall

from mmpm.constants import paths, urls
from mmpm.log.logger import MMPMLogger
from mmpm.singleton import Singleton
from mmpm.utils import run_cmd, systemctl

logger = MMPMLogger.get_logger(__name__)


class MMPMui(Singleton):
    def __init__(self):
        self.pm2_config = Path("/tmp/mmpm/ecosystem.json")
        self.pm2_processes = {
            "apps": [
                {
                    "name": "MMPM-API-Server",
                    "script": f"python3 -m gunicorn -k gevent -b 0.0.0.0:{urls.MMPM_API_SERVER_PORT} mmpm.wsgi:app",
                    "watch": True,
                },
                {
                    "name": "MMPM-Log-Server",
                    "script": f"python3 -m gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 'mmpm.log.server:create_app()' -b 0.0.0.0:{urls.MMPM_LOG_SERVER_PORT}",
                    "watch": True,
                },
                {
                    "name": "MMPM-UI",
                    "script": f"python3 -m http.server -d {paths.MMPM_PYTHON_ROOT_DIR / 'ui' / 'static'} -b 0.0.0.0 {urls.MMPM_UI_PORT}",
                    "watch": True,
                },
            ]
        }

    def create_pm2_config(self):
        if self.pm2_config.exists():
            logger.debug(f"{self.pm2_config} exists. Nothing to do.")
            return

        logger.debug(f"Creating {self.pm2_config} file")
        self.pm2_config.parent.mkdir(exist_ok=True)
        self.pm2_config.touch(exist_ok=True)

        with open(self.pm2_config, mode="w", encoding="utf-8") as config:
            logger.debug(f"Writing PM2 Configuration to {self.pm2_config}")
            json.dump(self.pm2_processes, config)

    def stop(self):
        return run_cmd(["pm2", "stop", f"{self.pm2_config}"], message="Stopping MMPM UI")

    def delete(self):
        return run_cmd(["pm2", "delete", f"{self.pm2_config}"], message="Removing MMPM UI")

    def start(self):
        return run_cmd(["pm2", "start", f"{self.pm2_config}"], message="Installing MMPM UI")

    def install(self) -> bool:
        """
        Installs the MMPM UI. It sets up NGINX configuration files and Systemd service files required for running
        the MMPM UI. This process includes copying and modifying template configuration files, setting up necessary
        directories, and ensuring the required services are enabled and running.

        Parameters:
            None

        Returns:
            None
        """

        if not shutil.which("pm2"):
            logger.fatal("pm2 is not in your PATH. Please run `npm install -g pm2`, and run the UI installation again.")
            return False

        self.create_pm2_config()
        error_code, _, stderr = self.start()

        if error_code:
            logger.error(f"Failed to install MMPM UI: {stderr}")
            return False

        return True

    def status(self):
        self.create_pm2_config()

        for process in self.pm2_processes["apps"]:
            error_code, stdout, stderr = run_cmd(["pm2", "describe", process["name"]])

            if error_code:
                logger.error(stderr)
            else:
                print(stdout)

    def remove(self):
        """
        Removes the MMPM UI. This method handles the deletion of NGINX configurations, Systemd service files,
        and any static web files associated with the MMPM UI. It stops and disables the relevant services
        and removes the related files. The user is prompted for confirmation unless assume_yes is True.

        Parameters:
            None

        Returns:
            None
        """
        if not shutil.which("pm2"):
            logger.fatal("pm2 is not in your PATH. Please run `npm install -g pm2`, and run the UI installation again.")
            return False

        self.create_pm2_config()
        error_code, _, stderr = self.delete()

        if error_code:
            logger.error(stderr)
            return False

        shutil.rmtree(self.pm2_config.parent, ignore_errors=True)
        return True
