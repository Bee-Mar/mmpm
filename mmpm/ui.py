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
from mmpm.logger import MMPMLogger
from mmpm.singleton import Singleton
from mmpm.utils import run_cmd, systemctl

logger = MMPMLogger.get_logger(__name__)


class MMPMui(Singleton):
    def __init__(self):
        self.ecosystem_config = Path("/tmp/mmpm/ecosystem.json")

        self.pm2_processes = {
            "apps": [
                {
                    "name": "MMPM-API-Server",
                    "script": "cd ~/Development/github/mmpm && pdm run server",
                    "watch": True,
                },
                {
                    "name": "MMPM-UI",
                    "script": "cd ~/Development/github/mmpm/ui/build/static && python3 -m http.server 7890 --bind 0.0.0.0",
                    "watch": True,
                },
                {
                    "name": "MMPM-Log-Server",
                    "script": "cd ~/Development/github/mmpm && pdm run logs",
                    "watch": True,
                },
            ]
        }

    def __create_config(self):
        if not self.ecosystem_config.exists():
            logger.debug(f"Creating {self.ecosystem_config} file")
            self.ecosystem_config.parent.mkdir(exist_ok=True)
            self.ecosystem_config.touch(exist_ok=True)

        with open(self.ecosystem_config, mode="w", encoding="utf-8") as config:
            logger.debug(f"Writing PM2 Configuration to {self.ecosystem_config}")
            json.dump(self.pm2_processes, config)

    def stop(self):
        return run_cmd(["pm2", "stop", f"{self.ecosystem_config}"], message="Stopping MMPM UI")

    def delete(self):
        return run_cmd(["pm2", "delete", f"{self.ecosystem_config}"], message="Removing MMPM UI")

    def start(self):
        return run_cmd(["pm2", "start", f"{self.ecosystem_config}"], message="Installing MMPM UI")

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

        self.__create_config()
        error_code, _, stderr = self.start()

        if error_code:
            logger.error(f"Failed to install MMPM UI: {stderr}")
            self.delete()

        return True

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

        self.__create_config()
        error_code, _, stderr = self.delete()

        if error_code:
            logger.error(f"Failed to remove MMPM UI: {stderr}")
            self.delete()

        shutil.rmtree(self.ecosystem_config.parent, ignore_errors=True)

    def get_uri(self) -> str:
        """
        Retrieves the URI of the MMPM web interface. It parses the NGINX configuration file to find the
        port number and constructs the URI using the host IP and the identified port.

        Returns:
            str: The URL of the MMPM web interface.
        """
        return f"http://{gethostbyname(gethostname())}:{port}"
