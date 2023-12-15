#!/usr/bin/env python3
import getpass
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from re import findall
from socket import gethostbyname, gethostname

from ItsPrompt.prompt import Prompt

from mmpm.constants import paths
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
                    "script": f"python3 -m gunicorn --worker-class gevent -b 0.0.0.0:7891 mmpm.wsgi:app",
                    "watch": True,
                },
                {
                    "name": "MMPM-Log-Server",
                    "script": f"python3 -m gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 'mmpm.log.server:create_app()' -b 0.0.0.0:6789",
                    "watch": True,
                },
                {
                    "name": "MMPM-UI",
                    "script": f"python3 -m http.server 7890 --bind 0.0.0.0 -d {paths.MMPM_PYTHON_ROOT_DIR / 'ui' / 'static'}",
                    "watch": True,
                },
            ]
        }

    def create_pm2_config(self):
        if not self.pm2_config.exists():
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

    def install(self, assume_yes: bool = False) -> bool:
        """
        Installs the MMPM UI. It sets up NGINX configuration files and Systemd service files required for running
        the MMPM UI. This process includes copying and modifying template configuration files, setting up necessary
        directories, and ensuring the required services are enabled and running.

        Parameters:
            assume_yes (bool): If True, skips confirmation prompts and proceeds with installation.

        Returns:
            None
        """

        if not assume_yes and not Prompt.confirm("Are you sure you want to install the MMPM UI?"):
            return False

        if not shutil.which("pm2"):
            logger.fatal("pm2 is not in your PATH. Please run `npm install -g pm2`, and run the UI installation again.")
            return False

        self.create_pm2_config()
        error_code, _, stderr = self.start()

        if error_code:
            logger.error(f"Failed to install MMPM UI: {stderr}")
            self.delete()

        return True

    def status(self):
        self.create_pm2_config()

        for process in self.pm2_processes["apps"]:
            error_code, stdout, stderr = run_cmd(["pm2", "describe", process["name"]])

            if error_code:
                logger.error(stderr)
            else:
                print(stdout)

    def remove(self, assume_yes: bool = False):
        """
        Removes the MMPM UI. This method handles the deletion of NGINX configurations, Systemd service files,
        and any static web files associated with the MMPM UI. It stops and disables the relevant services
        and removes the related files. The user is prompted for confirmation unless assume_yes is True.

        Parameters:
        assume_yes (bool): If True, skips confirmation prompts and proceeds with removal.

        Returns:
        None
        """

        if not assume_yes and not Prompt.confirm("Are you sure you want to remove the MMPM UI?"):
            return False

        if not shutil.which("pm2"):
            logger.fatal("pm2 is not in your PATH. Please run `npm install -g pm2`, and run the UI installation again.")
            return False

        self.create_pm2_config()
        error_code, _, stderr = self.delete()

        if error_code:
            logger.error(f"Failed to remove MMPM UI: {stderr}")
            self.delete()

        shutil.rmtree(self.pm2_config.parent, ignore_errors=True)

    def get_uri(self) -> str:
        """
        Retrieves the URI of the MMPM web interface. It parses the NGINX configuration file to find the
        port number and constructs the URI using the host IP and the identified port.

        Returns:
            str: The URL of the MMPM web interface.
        """
        return f"http://{gethostbyname(gethostname())}:7890"
