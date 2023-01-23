#!/usr/bin/env python3
import socketio
from mmpm.logger import MMPMLogger
from mmpm.env import get_env
import mmpm.consts

logger = MMPMLogger.get_logger(__name__)
logger.setLevel(get_env(mmpm.consts.MMPM_LOG_LEVEL))


class MagicMirrorClient:
    __client__ = socketio.Client(logger=logger, reconnection=True, request_timeout=3000)

    @staticmethod
    def __init_client__(event: str, input_data: dict):
        try:
            MagicMirrorClient.__client__ = socketio.Client(logger=logger, reconnection=True, request_timeout=3000)
        except socketio.exceptions.SocketIOError as error:
            logger.fatal("Failed to create SocketIO client")

        @MagicMirrorClient.__client__.on('connect', namespace=mmpm.consts.MMPM_SOCKETIO_NAMESPACE)
        def connect(): # pylint: disable=unused-variable
            logger.info('connected to MagicMirror websocket')
            MagicMirrorClient.__client__.emit(event, namespace=mmpm.consts.MMPM_SOCKETIO_NAMESPACE, data=input_data)
            logger.info('emitted request for show modules to MMPM module')


        @MagicMirrorClient.__client__.event
        def connect_error(): # pylint: disable=unused-variable
            logger.error('Failed to connect to MagicMirror websocket. Is the MMPM_MAGICMIRROR_URI environment variable set properly?')
            mmpm.utils.error_msg('Failed to connect to MagicMirror websocket. Is the MMPM_MAGICMIRROR_URI environment variable set properly?')


        @MagicMirrorClient.__client__.on('disconnect', namespace=mmpm.consts.MMPM_SOCKETIO_NAMESPACE)
        def disconnect(): # pylint: disable=unused-variable
            logger.info('disconnected from MagicMirror websocket')


        @MagicMirrorClient.__client__.on('ACTIVE_MODULES', namespace=mmpm.consts.MMPM_SOCKETIO_NAMESPACE)
        def active_modules(data): # pylint: disable=unused-variable
            logger.info('received active modules from MMPM MagicMirror module')

            if not data:
                print(mmpm.consts.RED_X)
                mmpm.utils.error_msg('No data was received from the MagicMirror websocket. Is the MMPM_MAGICMIRROR_URI environment variable set properly?')
            else:
                print(mmpm.consts.GREEN_CHECK_MARK)

            for module in [json_data for index, json_data in enumerate(data) if json_data not in data[index + 1:]]:
                print(f"{mmpm.color.normal_green(module['name'])}\n  hidden: {'true' if module['hidden'] else 'false'}\n  key: {module['index'] + 1}\n")

            mmpm.utils.socketio_client_disconnect(client)

        @MagicMirrorClient.__client__.on('MODULES_TOGGLED', namespace=mmpm.consts.MMPM_SOCKETIO_NAMESPACE)
        def modules_toggled(data): # pylint: disable=unused-variable
            logger.info('received toggled modules from MMPM MagicMirror module')
            stop_thread_event.set()

            if not data:
                print(mmpm.consts.RED_X)
                mmpm.utils.error_msg('Unable to find provided module(s)')
            else:
                print(mmpm.consts.GREEN_CHECK_MARK)


        @MagicMirrorClient.__client__.on('MODULES_TOGGLED', namespace=mmpm.consts.MMPM_SOCKETIO_NAMESPACE)
        def modules_toggled(data): # pylint: disable=unused-variable
            logger.info('received toggled modules from MMPM MagicMirror module')
            stop_thread_event.set()

            if not data:
                print(mmpm.consts.RED_X)
                mmpm.utils.error_msg('Unable to find provided module(s)')
            else:
                print(mmpm.consts.GREEN_CHECK_MARK)


    @staticmethod
    def get_client(event: str, input_data: dict) -> socketio.Client:
        if __client__ is None:
            MagicMirrorClient.__init_client__(event, input_data)

        return MagicMirrorClient.__client__


class MagicMirrorController:
    def __init__(self):
        pass

    def status(self):
        client = MagicMirrorClient.get_client('FROM_MMPM_APP_get_active_modules', None)

        try:
            client.connect(MMPM_MAGICMIRROR_URI, namespaces=[mmpm.consts.MMPM_SOCKETIO_NAMESPACE])
        except (OSError, BrokenPipeError, Exception) as error:
            mmpm.utils.error_msg('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))
            client.disconnect()

    def hide_modules(self, modules_to_hide):
        client = MagicMirrorClient.get_client('FROM_MMPM_APP_toggle_modules', {'directive': 'hide', 'modules': modules_to_hide})

        try:
            client.connect(MMPM_MAGICMIRROR_URI, namespaces=[mmpm.consts.MMPM_SOCKETIO_NAMESPACE])
        except (OSError, BrokenPipeError, Exception) as error:
            mmpm.utils.error_msg('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))
            client.disconnect()

    def show_modules(self, modules_to_show):
        client = MagicMirrorClient.get_client('FROM_MMPM_APP_toggle_modules', data={'directive': 'show', 'modules': modules_to_show})

        try:
            client.connect(MMPM_MAGICMIRROR_URI, namespaces=[mmpm.consts.MMPM_SOCKETIO_NAMESPACE])
        except (OSError, BrokenPipeError, Exception) as error:
            mmpm.utils.error_msg('Failed to connect to MagicMirror, closing socket. Is MagicMirror running?')
            logger.error(str(error))
            client.disconnect()

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

        MMPM_MAGICMIRROR_PM2_PROCESS_NAME: str = get_env(mmpm.consts.MMPM_MAGICMIRROR_PM2_PROCESS_NAME_ENV)
        MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: str = get_env(mmpm.consts.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE_ENV)

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
            error_code, stderr, _ = mmpm.utils.run_cmd(command, progress=False)

            if error_code:
                print(mmpm.consts.RED_X)
                logger.msg.env_variables_error(stderr.strip())
                return False

            logger.info(f"started MagicMirror using '{process}'")
            print(mmpm.consts.GREEN_CHECK_MARK)
            return True

        MMPM_MAGICMIRROR_ROOT: str = os.path.normpath(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV))

        os.chdir(MMPM_MAGICMIRROR_ROOT)
        logger.info("Running 'npm start' in the background")

        mmpm.utils.plain_print(f'{mmpm.consts.GREEN_PLUS} npm start ')
        os.system('npm start &')
        print(mmpm.consts.GREEN_CHECK_MARK)
        logger.info("Using 'npm start' to start MagicMirror. Stdout/stderr capturing not possible in this case")
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

        MMPM_MAGICMIRROR_PM2_PROCESS_NAME: str = get_env(mmpm.consts.MMPM_MAGICMIRROR_PM2_PROCESS_NAME_ENV)
        MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: str = get_env(mmpm.consts.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE_ENV)

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

        mmpm.utils.kill_magicmirror_processes()
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

        process: str = ''
        command: List[str] = []

        MMPM_MAGICMIRROR_PM2_PROCESS_NAME: str = get_env(mmpm.consts.MMPM_MAGICMIRROR_PM2_PROCESS_NAME_ENV)
        MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: str = get_env(mmpm.consts.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE_ENV)

        if MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE:
            logger.info(f'docker-compose file set as {MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE}')

        if MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
            logger.info(f'pm2 process set as {MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE}')

        if shutil.which('pm2') and MMPM_MAGICMIRROR_PM2_PROCESS_NAME:
            command = ['pm2', 'restart', MMPM_MAGICMIRROR_PM2_PROCESS_NAME]
            process = 'pm2'

        elif shutil.which('docker-compose') and MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE:
            command = ['docker-compose', '-f', MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE, 'restart']
            process = 'docker-compose'

        if command and process:
            mmpm.utils.plain_print(f"{mmpm.consts.GREEN_PLUS} restarting MagicMirror using {command[0]} ")
            logger.info(f"Using '{process}' to restart MagicMirror")

            # pm2 and docker-compose cause the output to flip
            error_code, stderr, _ = mmpm.utils.run_cmd(command, progress=False)

            if error_code:
                print(mmpm.consts.RED_X)
                logger.msg.env_variables_error(stderr.strip())
                return False

            logger.info(f"restarted MagicMirror using '{process}'")
            print(mmpm.consts.GREEN_CHECK_MARK)
            return True

        if not stop_magicmirror():
            logger.error('Failed to stop MagicMirror using npm commands')
            return False

        if not start_magicmirror():
            logger.error('Failed to start MagicMirror using npm commands')
            return False

        logger.info('Restarted MagicMirror using npm commands')
        return True
