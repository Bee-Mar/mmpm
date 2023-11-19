#!/usr/bin/env python3
import os
import shutil
import sys
from os import chdir
from pathlib import Path, PosixPath

from mmpm.constants import color, symbols
from mmpm.env import MMPMEnv
from mmpm.logger import MMPMLogger
from mmpm.singleton import Singleton
from mmpm.utils import prompt, run_cmd

logger = MMPMLogger.get_logger(__name__)


class MagicMirror(Singleton):
    def __init__(self):
        self.env = MMPMEnv()

    def update(self):
        """
        Checks for updates available to the MagicMirror repository. Alerts user if an upgrade is available.

        Parameters:
            None

        Returns:
            bool: True upon success, False upon failure
        """
        magicmirror_root: PosixPath = self.env.mmpm_magicmirror_root.get()

        if not magicmirror_root.exists() or not (magicmirror_root / ".git").exists():
            logger.msg.warning("MagicMirror application directory not found or not a git repo.")
            return False

        chdir(magicmirror_root)
        logger.msg.retrieving("https://github.com/MichMich/MagicMirror", "MagicMirror")

        try:
            error_code, _, stdout = run_cmd(["git", "fetch", "--dry-run"], progress=False)
            can_upgrade: bool = bool(stdout)
        except KeyboardInterrupt:
            logger.info("User killed process with CTRL-C")
            sys.exit(127)

        if error_code:
            logger.msg.error("Unable to communicate with git server")

        return can_upgrade

    def upgrade(self):
        """
        Handles upgrade processs of MagicMirror by pulling changes from MagicMirror
        repo, and installing dependencies.

        Parameters:
            None

        Returns:
            success (bool): True if successful else False
        """
        print(f"Upgrading {color.n_green('MagicMirror')}")

        root = self.env.mmpm_magicmirror_root
        root_dir: PosixPath = root.get()

        if not root_dir.exists():
            message = f"{root_dir} does not exist. Is the {root.name} set properly?"
            logger.msg.error(message)
            logger.error(message)
            return False

        os.chdir(root_dir)

        error_code, _, stderr = run_cmd(["git", "checkout", "."], progress=False)

        if error_code:
            message = "Failed to checkout MagicMirror repo for clean upgrade"
            logger.msg.error(f"{message}. See `mmpm log` for details. {symbols.RED_X}")
            logger.error(f"{message}: {stderr}")
            return stderr

        error_code, _, stderr = run_cmd(["git", "pull"], progress=False)

        if error_code:
            message = "Failed to upgrade MagicMirror"
            logger.msg.error(f"{message}. See `mmpm log` for details. {symbols.RED_X}")
            logger.error(f"{message}: {stderr}")
            return stderr

        error_code, _, stderr = run_cmd(["npm", "install"], progress=True)

        if error_code:
            logger.msg.error(stderr)
            return False

        print("Upgrade complete! Restart MagicMirror for the changes to take effect")
        return True

    def install(self):
        """
        Installs MagicMirror. First checks if a MagicMirror installation can be
        found, and if one is found, prompts user to update the MagicMirror.
        Otherwise, searches for current version of NodeJS on the system. If one is
        found, the MagicMirror is then installed. If an old version of NodeJS is
        found, a newer version is installed before installing MagicMirror.

        Parameters:
            None

        Returns:
            bool: True upon success, False upon failure
        """

        root = self.env.mmpm_magicmirror_root
        root_path: PosixPath = root.get()

        if root_path.exists() and Path(root_path / "modules").exists():
            message = f"MagicMirror appears to already be installed in {root_path}. To install MagicMirror elsewhere, modify the {root.name} using 'mmpm open --env'"
            logger.fatal(message)
            logger.msg.fatal(message)
            return False

        print(f"Installing MagicMirror")

        if not prompt(f"Use '{root_path}' ({root.name}) as the parent directory of the new MagicMirror installation?"):
            print(f"Cancelled installation. To change the installation path of MagicMirror, modify the {root.name} using 'mmpm open --env'")
            return False

        for cmd in ["git", "npm"]:
            if not shutil.which(cmd):
                logger.msg.fatal(f"'{cmd}' command not found. Please install '{cmd}', then re-run 'mmpm install --magicmirror'")
                return False

        print(color.n_cyan(f"Installing MagicMirror in {root_path}/MagicMirror ..."))
        os.system(f"cd {root_path.parent} && git clone https://github.com/MichMich/MagicMirror && cd MagicMirror && npm run install-mm")

        print(color.n_green("\nRun 'mmpm mm-ctl --start' to start MagicMirror"))
        return True

    def remove(self) -> bool:
        root = self.env.mmpm_magicmirror_root
        root_path: PosixPath = root.get()

        if not root_path.exists():
            message = f"The {root_path} does not exist. Is {root.name} set properly?"
            logger.fatal(message)
            logger.msg.fatal(message)
            return False

        if prompt("Are you sure you want to remove MagicMirror?"):
            shutil.rmtree(root_path, ignore_errors=True)
            print("Removed MagicMirror")
            logger.info("Removed MagicMirror")
            return True

        return False
