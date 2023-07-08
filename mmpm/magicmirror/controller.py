#!/usr/bin/env python3
from mmpm.singleton import Singleton
from mmpm.constants import symbols, color
from mmpm.logger import MMPMLogger
from mmpm.env import MMPMEnv
from mmpm.utils import get_pids, kill_pids_of_process, run_cmd

import os
import shutil
import socketio
from time import sleep
from typing import List

logger = MMPMLogger.get_logger(__name__)


class MagicMirrorClientFactory:
    def __new__(cls, event: str, data: dict):
        client = None

        try:
            client = socketio.Client(logger=logger, reconnection=True, request_timeout=300)
        except socketio.exceptions.SocketIOError as error:
            logger.fatal(f"Failed to create SocketIO client: {error}")

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
                print(symbols.RED_X)
                logger.error('No data was received. Is the MMPM_MAGICMIRROR_URI environment variable set properly?')

            for module in [json_data for index, json_data in enumerate(data) if json_data not in data[index + 1:]]:
                print(f"{color.n_green(module['name'])}\n  hidden: {'true' if module['hidden'] else 'false'}\n  key: {module['index'] + 1}\n")

            client.disconnect()

        @client.on('MODULES_TOGGLED', namespace="/MMM-mmpm")
        def modules_toggled(data):
            logger.info('Received toggled modules from MMPM MagicMirror module')

            if not data:
                print(symbols.RED_X)
                logger.error('Unable to find provided module(s)')

            client.disconnect()

        return client



class MagicMirrorController(Singleton):
    def init(self):
        self.env = MMPMEnv()

    def status(self):
        client = MagicMirrorClientFactory('FROM_MMPM_APP_get_active_modules', {})

        try:
            client.connect(self.env.mmpm_magicmirror_uri.get(), namespaces=["/MMM-mmpm"])
        except (OSError, BrokenPipeError, Exception) as error:
            logger.msg.error('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))

    def hide_modules(self, modules_to_hide):
        client = MagicMirrorClientFactory('FROM_MMPM_APP_toggle_modules', {'directive': 'hide', 'modules': modules_to_hide})

        try:
            client.connect(self.env.mmpm_magicmirror_uri.get(), namespaces=["/MMM-mmpm"])
        except (OSError, BrokenPipeError, Exception) as error:
            logger.msg.error('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))

    def show_modules(self, modules_to_show):
        client = MagicMirrorClientFactory('FROM_MMPM_APP_toggle_modules', data={'directive': 'show', 'modules': modules_to_show})

        try:
            client.connect(self.env.mmpm_magicmirror_uri.get(), namespaces=["/MMM-mmpm"])
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

        MMPM_MAGICMIRROR_PM2_PROCESS_NAME: str = self.env.mmpm_magicmirror_pm2_process_name.get()
        MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: str = self.env.mmpm_magicmirror_docker_compose_file.get()

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
            error_code, stderr, _ = run_cmd(command, progress=False, background=True)

            if error_code:
                print(symbols.RED_X)
                logger.msg.error(stderr.strip())
                return False

            logger.info(f"started MagicMirror using '{process}'")
            print(symbols.GREEN_CHECK_MARK)
            return True

        os.chdir(self.env.mmpm_magicmirror_root.get())

        command = ["npm", "run", "start"]

        logger.info(f"Running `{' '.join(command)} in the background`")
        logger.msg.info("Starting MagicMirror ")

        run_cmd(command, progress=False, background=True)
        print(symbols.GREEN_CHECK_MARK)
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

        MMPM_MAGICMIRROR_PM2_PROCESS_NAME: str = self.env.mmpm_magicmirror_pm2_process_name.get()
        MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: str = self.env.mmpm_magicmirror_docker_compose_file.get()

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

        logger.msg.info('Stopping MagicMirror ')

        if command and process:
            logger.info(f"Using '{process}' to stop MagicMirror")
            # pm2 and docker-compose cause the output to flip
            error_code, stderr, _ = run_cmd(command, progress=False, background=True)

            if error_code:
                print(symbols.RED_X)
                logger.msg.error(stderr.strip())
                return False

            logger.info(f"stopped MagicMirror using '{process}'")
            print(symbols.GREEN_CHECK_MARK)
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
