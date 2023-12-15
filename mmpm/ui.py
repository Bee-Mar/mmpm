#!/usr/bin/env python3
import getpass
import os
import shutil
import subprocess
import sys
from re import findall
from socket import gethostbyname, gethostname

from ItsPrompt.prompt import Prompt

from mmpm.constants import paths
from mmpm.logger import MMPMLogger
from mmpm.singleton import Singleton
from mmpm.utils import systemctl

logger = MMPMLogger.get_logger(__name__)


class MMPMui(Singleton):
    def install(self, assume_yes: bool = False):
        """
        Installs the MMPM UI. It sets up NGINX configuration files and Systemd service files required for running
        the MMPM UI. This process includes copying and modifying template configuration files, setting up necessary
        directories, and ensuring the required services are enabled and running.

        Parameters:
            assume_yes (bool): If True, skips confirmation prompts and proceeds with installation.

        Returns:
            None
        """

        if not assume_yes and not Prompt.confirm("Are you sure you want to install the MMPM UI? (Requires sudo permission)"):
            return

        if not shutil.which("nginx"):
            logger.fatal("NGINX is not in your $PATH. Please install `nginx-full` (Debian), `nginx-mainline` (Arch) or equivalent")

        sub_gunicorn: str = "SUBSTITUTE_gunicorn"
        sub_user: str = "SUBSTITUTE_user"
        user: str = getpass.getuser()

        gunicorn_executable: str = shutil.which("gunicorn")

        if not gunicorn_executable:
            logger.fatal("Gunicorn executable not found. Please ensure Gunicorn is installed and in your PATH")

        temp_etc: str = "/tmp/etc"

        shutil.rmtree(temp_etc, ignore_errors=True)
        shutil.copytree(paths.MMPM_BUNDLED_ETC_DIR, temp_etc)

        temp_mmpm_service: str = f"{temp_etc}/systemd/system/mmpm.service"

        self.remove(assume_yes=True)

        with open(temp_mmpm_service, "r", encoding="utf-8") as original:
            config = original.read()

        with open(temp_mmpm_service, "w", encoding="utf-8") as mmpm_service:
            subbed = config.replace(sub_gunicorn, gunicorn_executable)
            subbed = subbed.replace(sub_user, user)
            mmpm_service.write(subbed)

        logger.info("Copying NGINX and SystemdD service configs ")

        os.system(
            f"""
                  sudo mkdir -p /var/www/mmpm;
                  sudo cp -r /tmp/etc /;
                  sudo cp -r {paths.MMPM_PYTHON_ROOT_DIR}/static /var/www/mmpm;
                  sudo cp -r {paths.MMPM_PYTHON_ROOT_DIR}/templates /var/www/mmpm;
                  """
        )

        logger.info("Cleaning configuration files and resetting SystemdD daemons ")

        os.system("rm -rf /tmp/etc")

        logger.info("Reloading SystemdD daemon ")
        daemon_reload = systemctl("daemon-reload")

        if daemon_reload.returncode != 0:
            logger.error(f"Failed to reload SystemdD daemon: {daemon_reload.stderr.decode('utf-8')}")

        logger.info("Enabling MMPM SystemdD daemon ")

        enable_mmpm_service = systemctl("enable", ["mmpm.service"])

        if enable_mmpm_service.returncode != 0:
            if Prompt.confirm("Failed to enable MMPM SystemD service. Would you like to remove the MMPM-UI?"):
                self.remove()
            sys.exit(127)

        start_mmpm_service = systemctl("start", ["mmpm.service"])

        if start_mmpm_service.returncode != 0:
            if Prompt.confirm("Failed to start MMPM SystemD service. Would you like to remove the MMPM-UI?"):
                self.remove()
            sys.exit(127)

        link_nginx_conf = subprocess.run(
            ["sudo", "ln", "-sf", "/etc/nginx/sites-available/mmpm.conf", "/etc/nginx/sites-enabled"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if link_nginx_conf.returncode != 0:
            if Prompt.confirm("Failed to create sym link for NGINX config. Would you like to remove the MMPM-UI?"):
                self.remove()
            sys.exit(127)

        logger.info("Restarting NGINX SystemD service ")
        restart_nginx = systemctl("restart", ["nginx"])

        if restart_nginx.returncode != 0:
            if Prompt.confirm("Failed to restart NGINX SystemD service. Would you like to remove the MMPM-UI?"):
                self.remove()
            sys.exit(127)

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
        if not assume_yes and not Prompt.confirm("Are you sure you want to remove the MMPM UI? (Requires sudo permission)"):
            return

        INACTIVE: str = "inactive\n"
        DISABLED: str = "disabled\n"

        is_active = systemctl("is-active", ["mmpm.service"])

        if is_active.returncode == 0:
            logger.info("Stopping MMPM SystemD service ")
            stopping = systemctl("stop", ["mmpm.service"])

            if stopping.returncode:
                logger.error("Failed to stop MMPM SystemD service. See `mmpm log` for details")
                logger.error(f"{stopping.stdout.decode('utf-8')}\n{stopping.stderr.decode('utf-8')}")

        elif is_active.stdout.decode("utf-8") == INACTIVE:
            logger.info("MMPM SystemD service not active, nothing to do")

        is_enabled = systemctl("is-enabled", ["mmpm.service"])

        if is_enabled.returncode == 0:
            disabling = systemctl("disable", ["mmpm.service"])

            if disabling.returncode == 0:
                logger.info("Disabled MMPM SystemD service")
            else:
                error = f"{disabling.stdout.decode('utf-8')}\n{disabling.stderr.decode('utf-8')}"
                logger.error(f"Failed to disable MMPM SystemD service: {error}")

        elif is_enabled.stdout.decode("utf-8") == DISABLED:
            logger.info("MMPM SystemD service not enabled, nothing to do")

        logger.info("Force removing NGINX and SystemD configs")

        cmd: str = f"""
        sudo rm -f {paths.MMPM_SYSTEMD_SERVICE_FILE};
        sudo rm -f {paths.MMPM_NGINX_CONF_FILE};
        sudo rm -rf /var/www/mmpm;
        sudo rm -f /etc/nginx/sites-available/mmpm.conf;
        sudo rm -f /etc/nginx/sites-enabled/mmpm.conf;
        """

        os.system(cmd)

        logger.info("Reloading SystemdD daemon ")
        daemon_reload = systemctl("daemon-reload")

        if daemon_reload.returncode != 0:
            error = daemon_reload.stderr.decode("utf-8")
            logger.error(f"Failed to reload SystemdD daemon. {error}")

        logger.info("Restarting NGINX SystemD service")
        restart_nginx = systemctl("restart", ["nginx"])

        if restart_nginx.returncode:
            error = restart_nginx.stderr.decode("utf-8")
            logger.error(f"Failed to restart NGINX SystemdD daemon. See `mmpm log` for details: {error}")

        print("MMPM UI Removed!")

    def get_uri(self) -> str:
        """
        Retrieves the URI of the MMPM web interface. It parses the NGINX configuration file to find the
        port number and constructs the URI using the host IP and the identified port.

        Returns:
            str: The URL of the MMPM web interface.
        """

        if not os.path.exists(paths.MMPM_NGINX_CONF_FILE):
            logger.fatal("The MMPM NGINX configuration file does not appear to exist. Is the UI installed?")

        # this value needs to be retrieved dynamically in case the user modifies the nginx conf
        with open(paths.MMPM_NGINX_CONF_FILE, "r", encoding="utf-8") as conf:
            mmpm_conf = conf.read()

        try:
            port: str = findall(r"listen\s?\d+", mmpm_conf)[0].split()[1]
        except IndexError:
            logger.fatal("Unable to retrieve the port number of the MMPM web interface")

        return f"http://{gethostbyname(gethostname())}:{port}"
