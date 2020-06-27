#!/usr/bin/env python3
import eventlet
eventlet.monkey_patch()

import os
import json
import shutil
from flask_cors import CORS
from flask import Flask, request, send_file, render_template, send_from_directory, Response
from shelljob.proc import Group
from flask_socketio import SocketIO
from typing import Tuple, List, Dict
import mmpm.utils as utils
import mmpm.consts as consts
import mmpm.core as core


MMPM_EXECUTABLE: list = [os.path.join(consts.HOME_DIR, '.local', 'bin', 'mmpm')]

app = Flask(
    __name__,
    root_path='/var/www/mmpm',
    static_folder="/var/www/mmpm/static",
)

app.config['CORS_HEADERS'] = 'Content-Type'

resources: dict = {
    r'/*': {'origins': '*'},
    r'/api/*': {'origins': '*'},
    r'/socket.io/*': {'origins': '*'},
}

CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')

api = lambda path: f'/api/{path}'

_modules_ = core.load_packages()


def __stream_cmd_output__(process: Group, cmd: list):
    '''
    Streams command output to socket.io client on frontend.

    Parameters:
        process (Group): the process object responsible for running the command
        cmd (List[str]): list of command arguments

    Returns:
        None
    '''
    command: list = MMPM_EXECUTABLE + cmd
    utils.log.info(f"Executing {command}")
    process.run(command)

    try:
        while process.is_pending():
            utils.log.info('Process pending')
            for _, line in process.readlines():
                socketio.emit('live-terminal-stream', {'data': str(line.decode('utf-8'))})
        utils.log.info(f'Process complete: {command}')
    except Exception:
        pass


@socketio.on_error()
def error_handler(error) -> Tuple[str, int]:
    '''
    Socket.io error handler

    Parameters:
        error (str): error message

    Returns:
        tuple (str, int): error message and code
    '''
    message: str = f'An internal error occurred within flask_socketio: {error}'
    utils.log.critical(message)
    return message, 500


@socketio.on('connect')
def on_connect() -> None:
    message: str = 'Server connected'
    utils.log.info(message)
    socketio.emit('connected', {'data': message})


@socketio.on('disconnect')
def on_disconnect() -> None:
    message: str = 'Server disconnected'
    utils.log.info(message)
    socketio.emit(message, {'data': message})


@app.after_request
def after_request(response: Response) -> Response:
    utils.log.info('Headers being added after the request')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response


@app.route('/<path:path>', methods=[consts.GET])
def static_proxy(path):
    return send_from_directory('./', path)


@app.route('/', methods=[consts.GET, consts.POST, consts.DELETE])
def root() -> str:
    return render_template('index.html')


@app.errorhandler(500)
def server_error(error) -> Tuple[str, int]:
    return f'An internal error occurred [{__name__}.py]: {error}', 500


@app.route(api('all-available-modules'), methods=[consts.GET])
def get_magicmirror_modules() -> dict:
    return _modules_


@app.route(api('install-modules'), methods=[consts.POST])
def install_magicmirror_modules() -> str:
    selected_packages: list = request.get_json(force=True)['selected-modules']
    selected_packages = utils.list_of_dict_to_magicmirror_packages(selected_packages)

    utils.log.info(f'User selected {selected_packages} to be installed')

    result: Dict[str, list] = {'failures': []}

    for package in selected_packages:
        success, error = core.install_package(package, assume_yes=True)

        if not success:
            utils.log.error(f'Failed to install {package.title} with error of: {error}')
            module[consts.ERROR] = error
            result['failures'].append(package)
        else:
            utils.log.info(f'Installed {package.title}')

    return json.dumps(result)


@app.route(api('uninstall-modules'), methods=[consts.POST])
def remove_magicmirror_modules() -> str:
    selected_modules: list = request.get_json(force=True)['selected-modules']
    utils.log.info(f'User selected {selected_modules} to be removed')

    result: Dict[str, list] = {'failures': []}

    for module in selected_modules:
        try:
            shutil.rmtree(module[consts.DIRECTORY])
            utils.log.info(f'Removed {module[consts.DIRECTORY]}')
        except FileNotFoundError as error:
            utils.log.error(f'Failed to remove {module[consts.DIRECTORY]}')
            module[consts.ERROR] = error
            result['failures'].append(module)

    return json.dumps(result)


@app.route(api('upgrade-modules'), methods=[consts.POST])
def upgrade_magicmirror_modules() -> str:
    selected_modules: list = request.get_json(force=True)['selected-modules']
    utils.log.info(f'Request to upgrade {selected_modules}')

    result: List[dict] = []

    for module in selected_modules:
        error = core.upgrade_package(module)
        if error:
            utils.log.error(f'Failed to upgrade {module[consts.TITLE]} with error of: {error}')
            module[consts.ERROR] = error
            result.append(module)

    utils.log.info('Finished executing upgrades')
    return json.dumps(result)


@app.route(api('all-installed-modules'), methods=[consts.GET])
def get_installed_magicmirror_modules() -> dict:
    return core.get_installed_packages(_modules_)


@app.route(api('all-external-modules'), methods=[consts.GET])
def get_external__modules__sources() -> dict:
    ext_sources: dict = {consts.EXTERNAL_MODULE_SOURCES: []}
    try:
        with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
            ext_sources[consts.EXTERNAL_MODULE_SOURCES] = json.load(mmpm_ext_srcs)[consts.EXTERNAL_MODULE_SOURCES]
    except IOError as error:
        utils.log.error(error)
        pass
    return ext_sources


@app.route(api('add-external-module-source'), methods=[consts.POST])
def add_external_package() -> str:
    external_source: dict = request.get_json(force=True)['external-source']

    result: List[dict] = []

    error: str = core.add_external_package(
        title=external_source.get('title'),
        author=external_source.get('author'),
        description=external_source.get('description'),
        repo=external_source.get('repository')
    )

    return json.dumps({'error': "no_error" if not error else error})


@app.route(api('remove-external-module-source'), methods=[consts.DELETE])
def remove_external_module_source() -> str:
    selected_modules: list = request.get_json(force=True)['external-sources']
    utils.log.info(f'Request to remove external sources')

    ext_modules: dict = {}
    marked_for_removal: list = []

    try:
        with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
            ext_modules[consts.EXTERNAL_MODULE_SOURCES] = json.load(mmpm_ext_srcs)[consts.EXTERNAL_MODULE_SOURCES]
        utils.log.info(f'Read external modules from {consts.MMPM_EXTERNAL_SOURCES_FILE}')
    except IOError as error:
        utils.log.error(error)
        return json.dumps({'error': error})

    for selected_module in selected_modules:
        # will clean this ugliness up, but for the moment leaving just because it works
        del selected_module[consts.DIRECTORY]
        del selected_module[consts.CATEGORY]

        for module in ext_modules[consts.EXTERNAL_MODULE_SOURCES]:
            print(module)
            if module == selected_module:
                marked_for_removal.append(module)
                utils.log.info(f'Found matching external module ({module[consts.TITLE]}) and marked for removal')

    for module in marked_for_removal:
        ext_modules[consts.EXTERNAL_MODULE_SOURCES].remove(module)
        utils.log.info(f'Removed {module[consts.TITLE]}')

    try:
        with open(consts.MMPM_EXTERNAL_SOURCES_FILE, 'w') as mmpm_ext_srcs:
            json.dump(ext_modules, mmpm_ext_srcs)
        utils.log.info(f'Wrote updated external modules to {consts.MMPM_EXTERNAL_SOURCES_FILE}')
    except IOError as error:
        utils.log.error(error)
        return json.dumps({'error': error})

    utils.log.info(f'Wrote external modules to {consts.MMPM_EXTERNAL_SOURCES_FILE}')
    return json.dumps({'error': "no_error"})


@app.route(api('refresh-database'), methods=[consts.GET])
def force_refresh_magicmirror_modules() -> dict:
    utils.log.info(f'Received request to refresh modules')
    _modules_ = core.load_packages(force_refresh=True)
    return _modules_


@app.route(api('get-magicmirror-config'), methods=[consts.GET])
def get_magicmirror_config():
    path: str = consts.MAGICMIRROR_CONFIG_FILE
    result: str = send_file(path, attachment_filename='config.js') if path else ''
    utils.log.info('Retrieving MagicMirror config')
    return result


@app.route(api('update-magicmirror-config'), methods=[consts.POST])
def update_magicmirror_config() -> str:
    data: dict = request.get_json(force=True)
    utils.log.info('Saving MagicMirror config file')

    try:
        with open(consts.MAGICMIRROR_CONFIG_FILE, 'w') as config:
            config.write(data.get('code'))
    except IOError:
        return json.dumps(False)
    return json.dumps(True)


@app.route(api('start-magicmirror'), methods=[consts.GET])
def start_magicmirror() -> str:
    '''
    Restart the MagicMirror by killing all Chromium processes, the
    re-running the startup script for MagicMirror

    Parameters:
        None

    Returns:
        bool: True if the command was called, False it appears that MagicMirror is currently running
    '''
    # there really isn't an easy way to capture return codes for the background process, so, for the first version, let's just be lazy for now
    # need to find way to capturing return codes

    # if these processes are all running, we assume MagicMirror is running currently
    if utils.get_pids('chromium') and utils.get_pids('node') and utils.get_pids('npm'):
        utils.log.info('MagicMirror appears to be running already. Returning False.')
        return json.dumps(False)

    utils.log.info('MagicMirror does not appear to be running currently. Returning True.')
    core.start_magicmirror()
    return json.dumps(True)


@app.route(api('restart-magicmirror'), methods=[consts.GET])
def restart_magicmirror() -> str:
    '''
    Restart the MagicMirror by killing all Chromium processes, the
    re-running the startup script for MagicMirror

    Parameters:
        None

    Returns:
        bool: Always True only as a signal the process was called
    '''
    # same issue as the start-magicmirror api call
    core.restart_magicmirror()
    return json.dumps(True)


@app.route(api('stop-magicmirror'), methods=[consts.GET])
def stop_magicmirror() -> str:
    '''
    Stop the MagicMirror by killing all Chromium processes

    Parameters:
        None

    Returns:
        bool: Always True only as a signal the process was called
    '''
    # same sort of issue as the start-magicmirror call
    core.stop_magicmirror()
    return json.dumps(True)


@app.route(api('restart-raspberrypi'), methods=[consts.GET])
def restart_raspberrypi() -> str:
    '''
    Reboot the RaspberryPi

    Parameters:
        None

    Returns:
        success (bool): If the command fails, False is returned. If success, the return will never reach the interface
    '''

    utils.log.info('Restarting RaspberryPi')
    core.stop_magicmirror()
    error_code, _, _ = utils.run_cmd(['sudo', 'reboot'])
    # if success, it'll never get the response, but we'll know if it fails
    return json.dumps(bool(not error_code))


@app.route(api('stop-raspberrypi'), methods=[consts.GET])
def turn_off_raspberrypi() -> str:
    '''
    Shut down the RaspberryPi

    Parameters:
        None

    Returns:
        success (bool): If the command fails, False is returned. If success, the return will never reach the interface
    '''

    utils.log.info('Shutting down RaspberryPi')
    # if success, we'll never get the response, but we'll know if it fails
    core.stop_magicmirror()
    error_code, _, _ = utils.run_cmd(['sudo', 'shutdown', '-P', 'now'])
    return json.dumps(bool(not error_code))


@app.route(api('upgrade-magicmirror'), methods=[consts.GET])
def upgrade_magicmirror() -> str:
    utils.log.info(f'Request to upgrade MagicMirror')
    process: Group = Group()
    Response(__stream_cmd_output__(process, ['-M', '--GUI']), mimetype='text/plain')
    utils.log.info('Finished installing')

    if utils.get_pids('node') and utils.get_pids('npm') and utils.get_pids('electron'):
        core.restart_magicmirror()

    return json.dumps(True)


@app.route(api('get-magicmirror-root-directory'), methods=[consts.GET])
def get_magicmirror_root_directory() -> str:
    utils.log.info(f'Request to get MagicMirror root directory')
    return json.dumps({"magicmirror_root": consts.MAGICMIRROR_ROOT})

#@app.route(api('download-log-files'), methods=[consts.GET])
#def download_log_files():
#    path: str = consts.MAGICMIRROR_CONFIG_FILE
#    result: str = send_file(path, attachment_filename='config.js') if path else ''
#    log.info('Retrieving MMPM log files')
#    return result
