#!/usr/bin/env python3
import getpass
import os
import shutil
import subprocess
import sys
from re import findall
from socket import gethostbyname, gethostname

from mmpm.constants import paths, symbols
from mmpm.logger import MMPMLogger
from mmpm.singleton import Singleton
from mmpm.utils import prompt, systemctl

logger = MMPMLogger.get_logger(__name__)


class MMPMGui(Singleton):
    def __init__(self):
        pass

    def install(self, assume_yes: bool = False):
        """
        Installs the MMPM GUI by configuring the required NGINX files bundled in
        the MMPM PyPI package. This asks the user for sudo permissions. The
        template config files are copied from the mmpm PyPI package, modified to
        contain the proper paths, then installed in the required system folders

        Parameters:
            assume_yes (bool): if True, all prompts are assumed to have a response of yes from the user. This is used only internally of the MMPM CLI


        Returns:
            None
        """

        if not assume_yes and not prompt("Are you sure you want to install the MMPM GUI? This requires sudo permission."):
            return

        if not shutil.which("nginx"):
            logger.msg.fatal("NGINX is not in your $PATH. Please install `nginx-full` (Debian), `nginx-mainline` (Arch) or equivalent")

        sub_gunicorn: str = "SUBSTITUTE_gunicorn"
        sub_user: str = "SUBSTITUTE_user"
        user: str = getpass.getuser()

        gunicorn_executable: str = shutil.which("gunicorn")

        if not gunicorn_executable:
            message = "Gunicorn executable not found. Please ensure Gunicorn is installed and in your PATH"
            logger.msg.fatal(message)
            logger.fatal(message)

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

        logger.msg.info("Copying NGINX and SystemdD service configs ")

        os.system(
            f"""
                  sudo mkdir -p /var/www/mmpm;
                  sudo cp -r /tmp/etc /;
                  sudo cp -r {paths.MMPM_PYTHON_ROOT_DIR}/static /var/www/mmpm;
                  sudo cp -r {paths.MMPM_PYTHON_ROOT_DIR}/templates /var/www/mmpm;
                  """
        )

        print(symbols.GREEN_CHECK_MARK)

        logger.msg.info("Cleaning configuration files and resetting SystemdD daemons ")
        print(symbols.GREEN_CHECK_MARK)

        os.system("rm -rf /tmp/etc")

        logger.msg.info("Reloading SystemdD daemon ")
        daemon_reload = systemctl("daemon-reload")

        if daemon_reload.returncode != 0:
            print(symbols.RED_X)
            logger.msg.error("Failed to reload SystemdD daemon. See `mmpm log` for details")
            logger.error(daemon_reload.stderr.decode("utf-8"))
        else:
            print(symbols.GREEN_CHECK_MARK)

        logger.msg.info("Enabling MMPM SystemdD daemon ")

        enable_mmpm_service = systemctl("enable", ["mmpm.service"])

        if enable_mmpm_service.returncode != 0:
            if prompt("Failed to enable MMPM SystemD service. Would you like to remove the MMPM-GUI? [y/n]: "):
                self.remove()
            sys.exit(127)

        print(symbols.GREEN_CHECK_MARK)

        start_mmpm_service = systemctl("start", ["mmpm.service"])

        if start_mmpm_service.returncode != 0:
            if prompt("Failed to start MMPM SystemD service. Would you like to remove the MMPM-GUI? [y/n]: "):
                self.remove()
            sys.exit(127)

        link_nginx_conf = subprocess.run(
            ["sudo", "ln", "-sf", "/etc/nginx/sites-available/mmpm.conf", "/etc/nginx/sites-enabled"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if link_nginx_conf.returncode != 0:
            if prompt("Failed to create sym link for NGINX config. Would you like to remove the MMPM-GUI? [y/n]: "):
                self.remove()
            sys.exit(127)

        logger.msg.info("Restarting NGINX SystemD service ")
        restart_nginx = systemctl("restart", ["nginx"])

        if restart_nginx.returncode != 0:
            if prompt("Failed to restart NGINX SystemD service. Would you like to remove the MMPM-GUI? [y/n]: "):
                self.remove()
            sys.exit(127)

        print(symbols.GREEN_CHECK_MARK)
        print("MMPM GUI installed! See `mmpm list --gui-url` for the URI, or run `mmpm open --gui` to launch")

    def remove(self, assume_yes: bool = False):
        """
        Removes all SystemD services and NGINX, SystemD, and static web files
        associated with the MMPM GUI. This requires sudo permission, and the user
        is prompted, letting them know this is the case. During any failures,
        verbose error messages are written to the log files, and the user is made
        known of the errors.

        Parameters:
            assume_yes (bool): used when calling the `remove` function from within the
                                `install` function to clean up any possible conflicts

        Returns:
            None
        """
        if not assume_yes and not prompt("Are you sure you want to remove the MMPM GUI? This requires sudo permission."):
            return

        INACTIVE: str = "inactive\n"
        DISABLED: str = "disabled\n"

        is_active = systemctl("is-active", ["mmpm.service"])

        if is_active.returncode == 0:
            logger.msg.info("Stopping MMPM SystemD service ")
            stopping = systemctl("stop", ["mmpm.service"])

            if stopping.returncode == 0:
                print(symbols.GREEN_CHECK_MARK)
            else:
                print(symbols.RED_X)
                logger.msg.error("Failed to stop MMPM SystemD service. See `mmpm log` for details")
                logger.error(f"{stopping.stdout.decode('utf-8')}\n{stopping.stderr.decode('utf-8')}")

        elif is_active.stdout.decode("utf-8") == INACTIVE:
            print(f"MMPM SystemD service not active, nothing to do {symbols.GREEN_CHECK_MARK}")

        is_enabled = systemctl("is-enabled", ["mmpm.service"])

        if is_enabled.returncode == 0:
            logger.msg.info("Disabling MMPM SystemD service ")
            disabling = systemctl("disable", ["mmpm.service"])

            if disabling.returncode == 0:
                print(symbols.GREEN_CHECK_MARK)
            else:
                print(symbols.RED_X)
                logger.msg.error("Failed to disable MMPM SystemD service. See `mmpm log` for details")
                logger.error(f"{disabling.stdout.decode('utf-8')}\n{disabling.stderr.decode('utf-8')}")

        elif is_enabled.stdout.decode("utf-8") == DISABLED:
            print(f"MMPM SystemD service not enabled, nothing to do {symbols.GREEN_CHECK_MARK}")

        logger.msg.info("Force removing NGINX and SystemD configs ")

        cmd: str = f"""
        sudo rm -f {paths.MMPM_SYSTEMD_SERVICE_FILE};
        sudo rm -f {paths.MMPM_NGINX_CONF_FILE};
        sudo rm -rf /var/www/mmpm;
        sudo rm -f /etc/nginx/sites-available/mmpm.conf;
        sudo rm -f /etc/nginx/sites-enabled/mmpm.conf;
        """

        print(symbols.GREEN_CHECK_MARK)

        os.system(cmd)

        logger.msg.info("Reloading SystemdD daemon ")
        daemon_reload = systemctl("daemon-reload")

        if daemon_reload.returncode != 0:
            print(symbols.RED_X)
            logger.msg.error("Failed to reload SystemdD daemon. See `mmpm log` for details")
            logger.error(daemon_reload.stderr.decode("utf-8"))
        else:
            print(symbols.GREEN_CHECK_MARK)

        logger.msg.info("Restarting NGINX SystemD service ")
        restart_nginx = systemctl("restart", ["nginx"])

        if restart_nginx.returncode != 0:
            print(symbols.RED_X)
            logger.msg.error("Failed to restart NGINX SystemdD daemon. See `mmpm log` for details")
            logger.error(restart_nginx.stderr.decode("utf-8"))
        else:
            print(symbols.GREEN_CHECK_MARK)

        print("MMPM GUI Removed!")

    def get_uri(self):
        """
        Parses the MMPM nginx conf file for the port number assigned to the web
        interface, and returns a string containing containing the host IP and
        assigned port.

        Parameters:
            None

        Returns:
            str: The URL of the MMPM web interface
        """

        if not os.path.exists(paths.MMPM_NGINX_CONF_FILE):
            logger.msg.fatal("The MMPM NGINX configuration file does not appear to exist. Is the GUI installed?")

        # this value needs to be retrieved dynamically in case the user modifies the nginx conf
        with open(paths.MMPM_NGINX_CONF_FILE, "r", encoding="utf-8") as conf:
            mmpm_conf = conf.read()

        try:
            port: str = findall(r"listen\s?\d+", mmpm_conf)[0].split()[1]
        except IndexError:
            logger.msg.fatal("Unable to retrieve the port number of the MMPM web interface")

        return f"http://{gethostbyname(gethostname())}:{port}"
