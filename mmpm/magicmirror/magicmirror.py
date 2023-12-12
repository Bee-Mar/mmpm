#!/usr/bin/env python3
import os
import shutil
import sys
from os import chdir
from pathlib import Path, PosixPath

from mmpm.constants import color
from mmpm.env import MMPMEnv
from mmpm.logger import MMPMLogger
from mmpm.singleton import Singleton
from mmpm.utils import repo_up_to_date, run_cmd

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
        magicmirror_root: PosixPath = self.env.MMPM_MAGICMIRROR_ROOT.get()

        if not magicmirror_root.exists() or not (magicmirror_root / ".git").exists():
            logger.warning("MagicMirror application directory not found or not a git repo.")
            return False

        logger.debug("Checking to see if MagicMirror is up to date")

        chdir(magicmirror_root)
        print(f"Retrieving: https://github.com/MichMich/MagicMirror [{color.n_cyan('MagicMirror')}]")

        try:
            can_upgrade = repo_up_to_date(magicmirror_root)
        except KeyboardInterrupt:
            logger.info("User killed process with CTRL-C")
            sys.exit(127)

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

        root = self.env.MMPM_MAGICMIRROR_ROOT
        root_dir: PosixPath = root.get()

        if not root_dir.exists():
            message = f"{root.name}='{root_dir}' does not exist. Is the {root.name} set properly?"
            logger.error(message)
            return False

        os.chdir(root_dir)

        error_code, _, stderr = run_cmd(["git", "checkout", "."], progress=False)

        if error_code:
            message = "Failed to checkout MagicMirror repo for clean upgrade"
            logger.error(f"{message}. See `mmpm log` for details")
            return stderr

        error_code, _, stderr = run_cmd(["git", "pull"], progress=False)

        if error_code:
            message = "Failed to upgrade MagicMirror"
            logger.error(f"{message}. See `mmpm log` for details")
            return stderr

        error_code, _, stderr = run_cmd(["npm", "install"], progress=True)

        if error_code:
            logger.error(stderr)
            return False

        print("Upgrade complete! Restart MagicMirror for the changes to take effect")
        return True

    def install(self):  # TODO fix docs
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

        root = self.env.MMPM_MAGICMIRROR_ROOT
        root_path: PosixPath = root.get()

        if root_path.exists() and Path(root_path / "modules").exists():
            message = f"MagicMirror appears to already be installed in {root_path}. To install MagicMirror elsewhere, modify the {root.name} using 'mmpm open --env'"
            logger.fatal(message)
            return False

        for cmd in ["git", "npm"]:
            if not shutil.which(cmd):
                logger.fatal(f"'{cmd}' command not found. Please install '{cmd}', then re-run 'mmpm install --magicmirror'")
                return False

        root_path.mkdir(exist_ok=True)
        os.chdir(root_path.parent)

        error_code, _, stderr = run_cmd(
            ["git", "clone", "https://github.com/MichMich/MagicMirror"], progress=True, message=f"Cloning MagicMirror into '{root_path}'"
        )

        if error_code:
            logger.error(f"Failed to clone the MagicMirror repo: {stderr}")
            return False

        os.chdir(root_path)
        error_code, _, stderr = run_cmd(["npm", "run", "install-mm"], progress=True, message="Installing Node dependencies")

        if error_code:
            logger.error(f"Failed to clone the MagicMirror repo: {stderr}")
            return False

        logger.info("Installed MagicMirror!")
        print(f"Run {color.n_green('`mmpm mm-ctl --start`')} to start MagicMirror")
        return True

    def remove(self) -> bool:
        root = self.env.MMPM_MAGICMIRROR_ROOT
        root_path: PosixPath = root.get()

        if not root_path.exists():
            message = f"'{root.name}'={root_path} does not exist. Is {root.name} set properly?"
            logger.fatal(message)
            return False

        if os.getcwd() == f"{root_path}":
            os.chdir("/tmp")

        shutil.rmtree(root_path, ignore_errors=True)
        logger.info("MagicMirror has been removed.")
        return True
