#!/usr/bin/env python3
import os
import sys
import json
import shutil
import socketio
import subprocess
import mmpm.consts
from mmpm.singleton import Singleton
from mmpm.constants import paths
from time import sleep
from mmpm.logger import MMPMLogger
from mmpm.env import MMPMEnv
from pathlib import Path, PosixPath
from mmpm.utils import get_pids, read_available_upgrades, kill_pids_of_process

logger = MMPMLogger.get_logger(__name__)


class MagicMirrorClientFactory:
    def __new__(cls, event: str, data: dict):
        client = None

        try:
            client = socketio.Client(logger=logger, reconnection=True, request_timeout=300)
        except socketio.exceptions.SocketIOError as error:
            logger.fatal("Failed to create SocketIO client")

        @client.on('connect', namespace="/MMM-mmpm")
        def connect():
            logger.info('Connected to MagicMirror websocket')
            client.emit(event, namespace="/MMM-mmpm", data=data)

        @client.event
        def connect_error():
            logger.error('Failed to connect to MagicMirror websocket. Is the MMPM_MAGICMIRROR_URI environment variable set properly?')

        @client.on('disconnect', namespace="/MMM-mmpm")
        def disconnect():
            logger.info('Disconnected from MagicMirror websocket')

        @client.on('ACTIVE_MODULES', namespace="/MMM-mmpm")
        def active_modules(data):
            logger.info('Received active modules from MMPM MagicMirror module')

            if not data:
                print(mmpm.consts.RED_X)
                logger.error('No data was received. Is the MMPM_MAGICMIRROR_URI environment variable set properly?')

            for module in [json_data for index, json_data in enumerate(data) if json_data not in data[index + 1:]]:
                print(f"{mmpm.color.normal_green(module['name'])}\n  hidden: {'true' if module['hidden'] else 'false'}\n  key: {module['index'] + 1}\n")

            client.disconnect()

        @client.on('MODULES_TOGGLED', namespace="/MMM-mmpm")
        def modules_toggled(data):
            logger.info('Received toggled modules from MMPM MagicMirror module')

            if not data:
                print(mmpm.consts.RED_X)
                logger.error('Unable to find provided module(s)')

            client.disconnect()

        return client



class MagicMirrorController(Singleton):
    def status(self):
        client = MagicMirrorClientFactory('FROM_MMPM_APP_get_active_modules', {})

        try:
            client.connect(MMPMEnv.mmpm_magicmirror_uri.get(), namespaces=["/MMM-mmpm"])
        except (OSError, BrokenPipeError, Exception) as error:
            logger.msg.error('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))

    def hide_modules(self, modules_to_hide):
        client = MagicMirrorClientFactory('FROM_MMPM_APP_toggle_modules', {'directive': 'hide', 'modules': modules_to_hide})

        try:
            client.connect(MMPMEnv.mmpm_magicmirror_uri.get(), namespaces=["/MMM-mmpm"])
        except (OSError, BrokenPipeError, Exception) as error:
            logger.msg.error('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))

    def show_modules(self, modules_to_show):
        client = MagicMirrorClientFactory('FROM_MMPM_APP_toggle_modules', data={'directive': 'show', 'modules': modules_to_show})

        try:
            client.connect(MMPMEnv.mmpm_magicmirror_uri.get(), namespaces=["/MMM-mmpm"])
        except (OSError, BrokenPipeError, Exception) as error:
            logger.msg.error('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))

    def start(self):
        '''
        Launches MagicMirror using pm2, if found, otherwise a 'npm start' is run as
        a background process

        Parameters:
        None

        Returns:
            None
        '''
        logger.info('Starting MagicMirror')

        process: str = ''
        command: List[str] = []

        MMPM_MAGICMIRROR_PM2_PROCESS_NAME: str = MMPMEnv.mmpm_magicmirror_pm2_process_name.get()
        MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: str = MMPMEnv.mmpm_magicmirror_docker_compose_file.get()

        if MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE:
            logger.info(f'docker-compose file set as {MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE}')

        if MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
            logger.info(f'pm2 process set as {MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE}')

        if shutil.which('pm2') and MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
            command = ['pm2', 'start', MMPM_MAGICMIRROR_PM2_PROCESS_NAME]
            process = 'pm2'

        elif shutil.which('docker-compose') and MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE:
            command = ['docker-compose', '-f', MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE, 'up', '-d']
            process = 'docker-compose'

        if command and process:
            logger.msg.info(f"starting MagicMirror using {command[0]} ")
            logger.info(f"Using '{process}' to start MagicMirror")
            error_code, stderr, _ = mmpm.utils.run_cmd(command, progress=False, background=True)

            if error_code:
                print(mmpm.consts.RED_X)
                logger.msg.error(stderr.strip())
                return False

            logger.info(f"started MagicMirror using '{process}'")
            print(mmpm.consts.GREEN_CHECK_MARK)
            return True

        os.chdir(Path(MMPMEnv.mmpm_magicmirror_root.get()))

        command = ["npm", "run", "start"]

        logger.info(f"Running `{' '.join(command)} in the background`")
        logger.msg.info(f"Starting MagicMirror ")

        mmpm.utils.run_cmd(command, progress=False, background=True)
        print(mmpm.consts.GREEN_CHECK_MARK)
        return True


    def stop(self):
        '''
        Stops MagicMirror using pm2, if found, otherwise the associated
        processes are killed

        Parameters:
        None

        Returns:
            success (bool): True if successful, False if failure
        '''

        process: str = ''
        command: List[str] = []

        MMPM_MAGICMIRROR_PM2_PROCESS_NAME: str = MMPMEnv.mmpm_magicmirror_pm2_process_name.get()
        MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: str = MMPMEnv.mmpm_magicmirror_docker_compose_file.get()

        if MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE:
            logger.info(f'docker-compose file set as {MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE}')

        if MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
            logger.info(f'pm2 process set as {MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE}')

        if shutil.which('pm2') and MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
            command = ['pm2', 'stop', MMPM_MAGICMIRROR_PM2_PROCESS_NAME]
            process = 'pm2'

        elif shutil.which('docker-compose') and MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE:
            command = ['docker-compose', '-f', MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE, 'stop']
            process = 'docker-compose'

        logger.msg.info(f'Stopping MagicMirror ')

        if command and process:
            logger.info(f"Using '{process}' to stop MagicMirror")
            # pm2 and docker-compose cause the output to flip
            error_code, stderr, _ = mmpm.utils.run_cmd(command, progress=False, background=True)

            if error_code:
                print(mmpm.consts.RED_X)
                logger.msg.error(stderr.strip())
                return False

            logger.info(f"stopped MagicMirror using '{process}'")
            print(mmpm.consts.GREEN_CHECK_MARK)
            return True

        processes = ['electron']

        logger.info(f'Killing processes associated with MagicMirror: {processes}')

        for process in processes:
            kill_pids_of_process(process)
            logger.info(f'Killed pids of process {process}')

        return True


    def restart(self):
        '''
        Restarts MagicMirror using pm2, if found, otherwise the associated
        processes are killed and 'npm start' is re-run a background process

        Parameters:
        None

        Returns:
            None
        '''
        self.stop()
        sleep(2)
        self.start()

    def install(self):
        '''
        Installs MagicMirror. First checks if a MagicMirror installation can be
        found, and if one is found, prompts user to update the MagicMirror.
        Otherwise, searches for current version of NodeJS on the system. If one is
        found, the MagicMirror is then installed. If an old version of NodeJS is
        found, a newer version is installed before installing MagicMirror.

        Parameters:
            None

        Returns:
            bool: True upon succcess, False upon failure
        '''
        root = MMPMEnv.mmpm_magicmirror_root

        root_path: PosixPath = Path(root.get())

        if root_path.exists() and Path(root_path / "modules").exists():
            message = f"MagicMirror appears to already be installed in {root_path}. To install MagicMirror elsewhere, modify the {root.name} using 'mmpm open --env'"
            logger.fatal(message)
            logger.msg.fatal(message)
            return False

        print(f'Installing MagicMirror')

        if not mmpm.utils.prompt(f"Use '{root_path}' ({root.name}) as the parent directory of the new MagicMirror installation?"):
            print(f"Cancelled installation. To change the installation path of MagicMirror, modify the {root.name} using 'mmpm open --env'")
            return False

        for cmd in ["git", "npm"]:
            if not shutil.which(cmd):
                logger.msg.fatal(f"'{cmd}' command not found. Please install '{cmd}', then re-run mmpm install --magicmirror")
                return False

        print(mmpm.color.normal_cyan(f'Installing MagicMirror in {root_path}/MagicMirror ...'))
        os.system(f"cd {root_path.parent} && git clone https://github.com/MichMich/MagicMirror && cd MagicMirror && npm run install-mm")

        print(mmpm.color.normal_green("\nRun 'mmpm mm-ctl --start' to start MagicMirror"))
        return True

    def remove(self) -> bool:
        root = MMPMEnv.mmpm_magicmirror_root
        root_path: PosixPath = Path(root.get())

        if not root_path.exists():
            message = f"The {root_path} does not exist. Is {root.name} set properly?"
            logger.fatal(message)
            logger.msg.fatal(message)
            return False

        if mmpm.utils.prompt(f"Are you sure you want to remove MagicMirror?"):
            shutil.rmtree(root_path, ignore_errors=True)
            print("Removed MagicMirror")
            logger.info("Removed MagicMirror")
            return True

        return False

    def upgrade(self) -> bool: # TODO: TEST
        '''
        Handles upgrade processs of MagicMirror by pulling changes from MagicMirror
        repo, and installing dependencies.

        Parameters:
            None

        Returns:
            success (bool): True if successful else False
        '''
        print(f"Upgrading {mmpm.color.normal_green('MagicMirror')}")

        root = MMPMEnv.mmpm_magicmirror_root
        root_dir: PosixPath = Path(root.get())

        if not root_dir.exists():
            logger.msg.error(f"{root_dir} does not exist. Is the {root.name} set properly?")
            logger.error(f"{root_dir} does not exist. Cannot perform upgrade")
            return False

        os.chdir(root_dir)
        error_code, _, stderr = mmpm.utils.run_cmd(['git', 'pull'], progress=False)

        if error_code:
            message = 'Failed to upgrade MagicMirror'
            logger.msg.error(f'{message} {mmpm.consts.RED_X}')
            logger.error(f"{message}: {stderr}")
            return stderr

        error_code, _, stderr = mmpm.utils.run_cmd(['npm', 'install'], progress=True)

        if error_code:
            logger.msg.error(stderr)
            return False

        print('Upgrade complete! Restart MagicMirror for the changes to take effect')
        return True


    def update(self) -> bool:
        '''
        Checks for updates available to the MagicMirror repository. Alerts user if an upgrade is available.

        Parameters:
            None

        Returns:
            bool: True upon success, False upon failure
        '''
        magicmirror_root: PosixPath = Path(MMPMEnv.mmpm_magicmirror_root.get())

        if not magicmirror_root.exists():
            logger.msg.error('MagicMirror application directory not found. Please ensure the MMPM environment variables are set properly in your shell configuration')
            return False

        if not (magicmirror_root / '.git').exists():
            logger.msg.warning('The MagicMirror root is not a git repo. If running MagicMirror as a Docker container, updates cannot be performed via mmpm.')
            return False

        os.chdir(magicmirror_root)
        logger.msg.retrieving("https://github.com/MichMich/MagicMirror", "MagicMirror")

        try:
            # stdout and stderr are flipped for git command output, but oddly stderr doesn't contain error messages
            error_code, _, stdout = mmpm.utils.run_cmd(['git', 'fetch', '--dry-run'], progress=False)
            can_upgrade: bool = True if stdout else False
        except KeyboardInterrupt:
            logger.info("User killed process with CTRL-C")
            sys.exit(127)

        if error_code:
            logger.msg.error('Unable to communicate with git server')

        configuration = read_available_upgrades()

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="w", encoding="utf-8") as upgrade_file:
            configuration["MagicMirror"] = can_upgrade
            json.dump(configuration, upgrade_file)

        return can_upgrade


    def is_running(self):
        '''
        The status of MagicMirror running is determined by the presence of certain
        types of processes running. If those are found, it's assumed to be running,
        otherwise, not

        Parameters:
            None

        Returns:
            running (bool): True if running, False if not
        '''
        return bool(get_pids('electron') or get_pids('pm2'))
