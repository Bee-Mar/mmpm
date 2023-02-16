#!/usr/bin/env python3
import os
import sys
import shutil
import socketio
import mmpm.consts
from time import sleep
from mmpm.logger import MMPMLogger
from mmpm.env import MMPMEnv
from pathlib import Path

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
            mmpm.utils.error_msg('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))

    @classmethod
    def show_modules(cls, modules_to_show):
        client = MagicMirrorClient.get_client('FROM_MMPM_APP_toggle_modules', data={'directive': 'show', 'modules': modules_to_show})

        try:
            client.connect(MMPMEnv.mmpm_magicmirror_uri.get(), namespaces=["/mmpm"])
        except (OSError, BrokenPipeError, Exception) as error:
            mmpm.utils.error_msg('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
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
            mmpm.utils.plain_print(f"{mmpm.consts.GREEN_PLUS} starting MagicMirror using {command[0]} ")
            logger.info(f"Using '{process}' to start MagicMirror")
            error_code, stderr, _ = mmpm.utils.run_cmd(command, progress=False, background=True)

            if error_code:
                print(mmpm.consts.RED_X)
                logger.msg.env_variables_error(stderr.strip())
                return False

            logger.info(f"started MagicMirror using '{process}'")
            print(mmpm.consts.GREEN_CHECK_MARK)
            return True

        os.chdir(Path(MMPMEnv.mmpm_magicmirror_root.get()))
        logger.info("Running 'npm start' in the background")

        mmpm.utils.plain_print(f'{mmpm.consts.GREEN_PLUS} npm start ')
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
            mmpm.utils.plain_print(f"{mmpm.consts.GREEN_PLUS} stopping MagicMirror using {command[0]} ")
            logger.info(f"Using '{process}' to stop MagicMirror")
            # pm2 and docker-compose cause the output to flip
            error_code, stderr, _ = mmpm.utils.run_cmd(command, progress=False)

            if error_code:
                print(mmpm.consts.RED_X)
                logger.msg.env_variables_error(stderr.strip())
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

        if root_path.exists():
            message = f"MagicMirror appears to already be installed in {root}. To install MagicMirror elsewhere, modify the {root.name} using 'mmpm open --env'"
            logger.fatal(message)
            logger.msg.fatal(message)
            return

        print(f'{mmpm.consts.GREEN_PLUS} Installing MagicMirror')

        if mmpm.utils.prompt_user(f"Use '{root_path}' ({root.name}) as the parent directory of the new MagicMirror installation?"):
            root_path.mkdir(parents=True, exist_ok=True)
            os.chdir(root_path)
        else:
            print(f"Cancelled installation. To change the installation path of MagicMirror, modify the {root.name} using 'mmpm open --env'")
            sys.exit(0)

        for cmd in ["git", "npm"]:
            if not shutil.which(cmd):
                mmpm.utils.fatal_msg(f"'{cmd}' command not found. Please install '{cmd}', then re-run mmpm install --magicmirror")

        print(mmpm.color.normal_cyan(f'Installing MagicMirror in {root_path}/MagicMirror ...'))
        os.system(f"cd {root_path} && git clone https://github.com/MichMich/MagicMirror && cd MagicMirror && npm run install-mm")

        print(mmpm.color.normal_green("\nRun 'mmpm mm-ctl --start' to start MagicMirror"))
        return True

    @classmethod
    def remove(cls) -> bool:
        root = MMPMEnv.mmpm_magicmirror_root
        root_path: PosixPath = Path(root.get())

        if not root_path.exists():
            message = f"The {root.name} ({root_path}) does not exist. Please adjust the MMPM environment variables using 'mmpm open --env'."
            logger.fatal(message)
            logger.msg.fatal(message)
            return False

        print(f'{mmpm.consts.GREEN_PLUS} Installing MagicMirror')

        if mmpm.utils.prompt_user(f"Are you sure you want to remove MagicMirror?"):
            shutil.rmtree(root_path, ignore_errors=True)
            return True

        return False

    @classmethod
    def install_mmpm_module(cls):
        pass

    @classmethod
    def remove_mmpm_module(cls):
        pass
