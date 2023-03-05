#!/usr/bin/env python3
import os
import sys
import json
import shutil
import socketio
import mmpm.consts
from mmpm.constants import paths
from time import sleep
from mmpm.logger import MMPMLogger
from mmpm.env import MMPMEnv
from pathlib import Path, PosixPath
from mmpm.utils import get_pids

logger = MMPMLogger.get_logger(__name__)
logger.setLevel(MMPMEnv.mmpm_log_level.get())


class MagicMirrorClient:
    __client__ = socketio.Client(logger=logger, reconnection=True, request_timeout=3000)

    @classmethod
    def init(cls, event: str, data: dict):
        try:
            client = socketio.Client(logger=logger, reconnection=True, request_timeout=300)
        except socketio.exceptions.SocketIOError as error:
            logger.fatal("Failed to create SocketIO client")

        @client.on('connect', namespace="/mmpm")
        def connect(): # pylint: disable=unused-variable
            logger.info('Connected to MagicMirror websocket')
            client.emit(event, namespace="/mmpm", data=data)

        @client.event
        def connect_error(): # pylint: disable=unused-variable
            logger.error('Failed to connect to MagicMirror websocket. Is the MMPM_MAGICMIRROR_URI environment variable set properly?')

        @client.on('disconnect', namespace="/mmpm")
        def disconnect(): # pylint: disable=unused-variable
            logger.info('Disconnected from MagicMirror websocket')

        @client.on('ACTIVE_MODULES', namespace="/mmpm")
        def active_modules(data): # pylint: disable=unused-variable
            logger.info('received active modules from MMPM MagicMirror module')

            if not data:
                print(mmpm.consts.RED_X)
                logger.error('No data was received from the MagicMirror websocket. Is the MMPM_MAGICMIRROR_URI environment variable set properly?')

            for module in [json_data for index, json_data in enumerate(data) if json_data not in data[index + 1:]]:
                print(f"{mmpm.color.normal_green(module['name'])}\n  hidden: {'true' if module['hidden'] else 'false'}\n  key: {module['index'] + 1}\n")

            client.disconnect()

        @client.on('MODULES_TOGGLED', namespace="/mmpm")
        def modules_toggled(data): # pylint: disable=unused-variable
            logger.info('Received toggled modules from MMPM MagicMirror module')

            if not data:
                print(mmpm.consts.RED_X)
                logger.error('Unable to find provided module(s)')

            client.disconnect()

        MagicMirrorClient.__client__ = client

    @classmethod
    def get_client(cls, event: str, data: dict) -> socketio.Client:
        MagicMirrorClient.init(event, data)
        return MagicMirrorClient.__client__


class MagicMirrorController:
    @classmethod
    def status(cls):
        client = MagicMirrorClient.get_client('FROM_MMPM_APP_get_active_modules', {})

        try:
            client.connect(MMPMEnv.mmpm_magicmirror_uri.get(), namespaces=["/mmpm"])
        except (OSError, BrokenPipeError, Exception) as error:
            logger.msg.error('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))

    @classmethod
    def hide_modules(cls, modules_to_hide):
        client = MagicMirrorClient.get_client('FROM_MMPM_APP_toggle_modules', {'directive': 'hide', 'modules': modules_to_hide})

        try:
            client.connect(MMPMEnv.mmpm_magicmirror_uri.get(), namespaces=["/mmpm"])
        except (OSError, BrokenPipeError, Exception) as error:
            logger.msg.error('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))

    @classmethod
    def show_modules(cls, modules_to_show):
        client = MagicMirrorClient.get_client('FROM_MMPM_APP_toggle_modules', data={'directive': 'show', 'modules': modules_to_show})

        try:
            client.connect(MMPMEnv.mmpm_magicmirror_uri.get(), namespaces=["/mmpm"])
        except (OSError, BrokenPipeError, Exception) as error:
            logger.msg.error('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))

    @classmethod
    def start(cls):
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
            logger.msg.info(f"{mmpm.consts.GREEN_PLUS} starting MagicMirror using {command[0]} ")
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
        logger.info("Running 'npm start' in the background")

        logger.msg.info(f'{mmpm.consts.GREEN_PLUS} npm start ')
        os.system('npm start &')
        print(mmpm.consts.GREEN_CHECK_MARK)
        logger.info("Using 'npm start' to start MagicMirror. Stdout/stderr capturing not possible in this case")
        return True


    @classmethod
    def stop(cls):
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

        if command and process:
            logger.msg.info(f"{mmpm.consts.GREEN_PLUS} stopping MagicMirror using {command[0]} ")
            logger.info(f"Using '{process}' to stop MagicMirror")
            # pm2 and docker-compose cause the output to flip
            error_code, stderr, _ = mmpm.utils.run_cmd(command, progress=False)

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


    @classmethod
    def restart(cls):
        '''
        Restarts MagicMirror using pm2, if found, otherwise the associated
        processes are killed and 'npm start' is re-run a background process

        Parameters:
        None

        Returns:
            None
        '''
        MagicMirrorController.stop()
        sleep(2)
        MagicMirrorController.start()

    @classmethod
    def install(cls):
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

        print(f'{mmpm.consts.GREEN_PLUS} Installing MagicMirror')

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

    @classmethod
    def remove(cls) -> bool:
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

    @classmethod
    def install_mmpm_module(cls, assume_yes: bool = False) -> bool:
        if not assume_yes and not mmpm.utils.prompt('Are you sure you want to install the MMPM module?'):
            return False

        root: PosixPath = Path(MMPMEnv.mmpm_magicmirror_root.get())
        mmpm_module_dir: PosixPath = root / "modules" / "mmpm"

        logger.msg.info(f'{mmpm.consts.GREEN_PLUS} Creating MMPM module in MagicMirror modules directory ')

        try:
            mmpm_module_dir.mkdir(parents=True, exist_ok=True, mode=0o777)
            shutil.copyfile(f'{mmpm.consts.MMPM_JS_DIR}/mmpm.js', f'{mmpm_module_dir}/mmpm.js')
            shutil.copyfile(f'{mmpm.consts.MMPM_JS_DIR}/node_helper.js', f'{mmpm_module_dir}/node_helper.js')
        except OSError as error:
            logger.msg.error('Failed to create MMPM module. Is the directory owned by root?')
            logger.error(str(error))
            return False

        print(mmpm.consts.GREEN_CHECK_MARK)
        print('Run `mmpm open --config` and append { module: "mmpm" } to the modules array, then restart MagicMirror if running')

        return True

    @classmethod
    def remove_mmpm_module(cls, assume_yes: bool = False) -> bool:
        root = MMPMEnv.mmpm_magicmirror_root
        root_dir: PosixPath = Path(root.get())
        mmpm_module_dir: PosixPath = root_dir / "modules" / "mmpm"

        if not mmpm_module_dir.exists():
            message = f"The {root.name} ({root_path}) does not exist. Please adjust the MMPM environment variables using 'mmpm open --env'."
            logger.error(message)
            return False

        if not assume_yes and not mmpm.utils.prompt('Are you sure you want to remove the MMPM module?'):
            shutil.rmtree(mmpm_module_dir, ignore_errors=True)
            return False

    @classmethod
    def upgrade(cls) -> bool: # TODO: TEST
        '''
        Handles upgrade processs of MagicMirror by pulling changes from MagicMirror
        repo, and installing dependencies.

        Parameters:
            None

        Returns:
            success (bool): True if successful else False
        '''
        print(f"{mmpm.consts.GREEN_PLUS} Upgrading {mmpm.color.normal_green('MagicMirror')}")

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

    @classmethod
    def update(cls) -> bool:
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

        is_git: bool = True
        can_upgrade = False

        if not (magicmirror_root / '.git').exists():
            logger.msg.warning('The MagicMirror root is not a git repo. If running MagicMirror as a Docker container, updates cannot be performed via mmpm.')
            is_git = False

        if is_git:
            os.chdir(magicmirror_root)
            cyan_application: str = f"{mmpm.color.normal_cyan('application')}"
            logger.msg.info(f"Checking {mmpm.color.normal_green('MagicMirror')} [{cyan_application}] for updates")

            try:
                # stdout and stderr are flipped for git command output, but oddly stderr doesn't contain error messages
                error_code, _, stdout = mmpm.utils.run_cmd(['git', 'fetch', '--dry-run'])
            except KeyboardInterrupt:
                logger.info("User killed process with CTRL-C")
                sys.exit(127)

            print(mmpm.consts.GREEN_CHECK_MARK)

            if error_code:
                logger.msg.error('Unable to communicate with git server')

            if stdout:
                can_upgrade = True

        upgradable = {}

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="r", encoding="utf-8") as upgrade_file:
            upgradable = json.load(upgrade_file)

        with open(paths.MMPM_AVAILABLE_UPGRADES_FILE, mode="w", encoding="utf-8") as upgrade_file:
            upgradable["MagicMirror"] = can_upgrade
            json.dump(upgradable, upgrade_file)

        return can_upgrade


    @classmethod
    def is_running(cls):
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
