#!/usr/bin/env python3
import eventlet
eventlet.monkey_patch()

import os
import json
import shutil
import datetime

from flask_cors import CORS
from flask import Flask, request, send_file, render_template, send_from_directory, Response
from flask_socketio import SocketIO
from typing import Tuple, List, Dict

import mmpm.utils
import mmpm.consts
import mmpm.core
import mmpm.models

MagicMirrorPackage = mmpm.models.MagicMirrorPackage

MMPM_EXECUTABLE: list = [os.path.join(mmpm.consts.HOME_DIR, '.local', 'bin', 'mmpm')]

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

_modules_ = mmpm.core.load_packages()


def __get_selected_packages__(rqst) -> List[MagicMirrorPackage]:
    '''
    Helper method to extract a list of MagicMirrorPackage objects from Flask
    request object

    Parameters:
       request (werkzeug.wrappers.Request): the Flask request object

    Returns:
        selected_packages (List[MagicMirrorPackage]): extracted list of MagicMirrorPackage objects
    '''
    pkgs: dict = rqst.get_json(force=True)['selected-packages']

    # more-or-less a bandaid to the larger problem of aligning the data structure in angular
    for pkg in pkgs:
        del pkg['category']

        if not pkg['directory']:
            pkg['directory'] = os.path.join(mmpm.consts.MAGICMIRROR_MODULES_DIR, pkg['title'])

    return mmpm.utils.list_of_dict_to_list_of_magicmirror_packages(rqst.get_json(force=True)['selected-packages'])


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
    mmpm.utils.log.critical(message)
    return message, 500


@socketio.on('connect')
def on_connect() -> None:
    message: str = 'Server connected'
    mmpm.utils.log.info(message)
    socketio.emit('connected', {'data': message})


@socketio.on('disconnect')
def on_disconnect() -> None:
    message: str = 'Server disconnected'
    mmpm.utils.log.info(message)
    socketio.emit(message, {'data': message})


@app.after_request
def after_request(response: Response) -> Response:
    mmpm.utils.log.info('Headers being added after the request')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response


@app.route('/<path:path>', methods=[mmpm.consts.GET])
def static_proxy(path):
    return send_from_directory('./', path)


@app.route('/', methods=[mmpm.consts.GET, mmpm.consts.POST, mmpm.consts.DELETE])
def root() -> str:
    return render_template('index.html')


@app.errorhandler(500)
def server_error(error) -> Tuple[str, int]:
    return f'An internal error occurred [{__name__}.py]: {error}', 500


#  -- START: PACKAGES --
@app.route(api('packages/marketplace'), methods=[mmpm.consts.GET])
def packages_marketplace() -> str:
    mmpm.utils.log.info('Sending all marketplace packages')
    return json.dumps(_modules_, default=lambda pkg: pkg.serialize_full())


@app.route(api('packages/installed'), methods=[mmpm.consts.GET])
def packages_installed() -> str:
    mmpm.utils.log.info('Sending all installed packages')
    return json.dumps(mmpm.core.get_installed_packages(_modules_), default=lambda pkg: pkg.serialize_full())


@app.route(api('packages/external'), methods=[mmpm.consts.GET])
def packages_external() -> str:
    mmpm.utils.log.info('Sending all external packages')
    return json.dumps(mmpm.core.load_external_packages(), default=lambda pkg: pkg.serialize_full())


@app.route(api('packages/install'), methods=[mmpm.consts.POST])
def packages_install() -> str:
    selected_packages: List[MagicMirrorPackage] = __get_selected_packages__(request)
    mmpm.utils.log.info(f'User selected {selected_packages} to be installed')
    failures: List[dict] = []

    for package in selected_packages:
        success, error = mmpm.core.install_package(package, assume_yes=True)

        if not success:
            mmpm.utils.log.error(f'Failed to install {package.title} with error of: {error}')
            failures.append({'package': package.serialize(), 'error': error})
        else:
            mmpm.utils.log.info(f'Installed {package.title}')

    return json.dumps(failures)


@app.route(api('packages/remove'), methods=[mmpm.consts.POST])
def packages_remove() -> str:
    selected_packages: List[MagicMirrorPackage] = __get_selected_packages__(request)
    mmpm.utils.log.info(f'User selected {selected_packages} to be removed')
    failures: List[dict] = []

    for package in selected_packages:
        if not os.path.exists(package.directory):
            failures.append({'package': package.serialize(), 'error': f'{package.directory} not found'})
            continue
        try:
            shutil.rmtree(package.directory)
            mmpm.utils.log.info(f'Removed {package.directory}')
        except FileNotFoundError as error:
            mmpm.utils.log.error(f'Failed to remove {package.directory}')
            failures.append({'package': package.serialize(), 'error': str(error)})

    return json.dumps(failures)


@app.route(api('packages/upgrade'), methods=[mmpm.consts.POST])
def packages_upgrade() -> str:
    selected_packages: List[MagicMirrorPackage] = __get_selected_packages__(request)
    mmpm.utils.log.info(f'Request to upgrade {selected_packages}')

    failures: List[dict] = []

    for package in selected_packages:
        error = mmpm.core.upgrade_package(package)
        if error:
            mmpm.utils.log.error(f'Failed to upgrade {package.title} with error of: {error}')
            failures.append({'package': package.serialize(), 'error': error})

    mmpm.utils.log.info('Finished executing upgrades')
    return json.dumps(failures)


@app.route(api('packages/details'), methods=[mmpm.consts.POST])
def packages_details() -> str:
    selected_packages: List[MagicMirrorPackage] = __get_selected_packages__(request)
    mmpm.utils.log.info(f'Request to get verbose details about {selected_packages}')

    result: List[dict] = []

    for package in selected_packages:
        try:
            result.append({
                'package': package.serialize_full(),
                'details': mmpm.utils.get_remote_package_details(package)
            })
        except Exception:
            result.append({
                'package': package.serialize_full(),
                'details': {}
            })

    mmpm.utils.log.info('Finished retrieving verbose details for packages')
    return json.dumps(result)
#  -- END: PACKAGES --

#  -- START: EXTERNAL PACKAGES --
@app.route(api('external-packages/add'), methods=[mmpm.consts.POST])
def external_packages_add() -> str:
    package: dict = request.get_json(force=True)['external-package']

    failures: List[dict] = []

    error: str = mmpm.core.add_external_package(
        title=package.get('title'),
        author=package.get('author'),
        description=package.get('description'),
        repo=package.get('repository')
    )

    failures.append({'package': package, 'error': error})
    return json.dumps({'error': "no_error" if not error else error})


@app.route(api('external-packages/remove'), methods=[mmpm.consts.DELETE])
def external_packages_remove() -> str:
    selected_packages: List[MagicMirrorPackage] = __get_selected_packages__(request)
    mmpm.utils.log.info(f'Request to remove external sources')

    ext_modules: dict = {}
    marked_for_removal: list = []
    external_packages: List[MagicMirrorPackage] = mmpm.core.load_external_packages()[mmpm.consts.EXTERNAL_MODULE_SOURCES]

    for selected_package in selected_packages:
        for external_package in external_packages:
            if external_package == selected_package:
                marked_for_removal.append(external_package)
                mmpm.utils.log.info(f'Found matching external module ({external_package.title}) and marked for removal')

    for package in marked_for_removal:
        external_packages.remove(package)
        mmpm.utils.log.info(f'Removed {package.title}')

    try:
        with open(mmpm.consts.MMPM_EXTERNAL_SOURCES_FILE, 'w') as mmpm_ext_srcs:
            json.dump(ext_modules, mmpm_ext_srcs)
        mmpm.utils.log.info(f'Wrote updated external modules to {mmpm.consts.MMPM_EXTERNAL_SOURCES_FILE}')
    except IOError as error:
        mmpm.utils.log.error(error)
        return json.dumps({'error': str(error)})

    mmpm.utils.log.info(f'Wrote external modules to {mmpm.consts.MMPM_EXTERNAL_SOURCES_FILE}')
    return json.dumps({'error': "no_error"})
#  -- END: EXTERNAL PACKAGES --

#  -- START: DATABASE --
@app.route(api('database/refresh'), methods=[mmpm.consts.GET])
def database_refresh() -> dict:
    mmpm.utils.log.info(f'Received request to refresh modules')
    _modules_ = mmpm.core.load_packages(force_refresh=True)
    return _modules_
#  -- END: DATABASE --

#  -- START: MAGICMIRROR --
@app.route(api('magicmirror/root-dir'), methods=[mmpm.consts.GET])
def magicmirror_root_dir() -> str:
    mmpm.utils.log.info(f'Request to get MagicMirror root directory')
    return json.dumps({"magicmirror_root": mmpm.consts.MAGICMIRROR_ROOT})


@app.route(api('magicmirror/config'), methods=[mmpm.consts.GET, mmpm.consts.POST])
def magicmirror_config():
    if request.method == mmpm.consts.GET:

        result: str = send_file(
            mmpm.consts.MAGICMIRROR_CONFIG_FILE,
            attachment_filename='config.js'
        ) if mmpm.consts.MAGICMIRROR_CONFIG_FILE else '// config.js not found. An empty file was created for you in its place'

        mmpm.utils.log.info('Retrieving MagicMirror config')
        return result

    elif request.method == mmpm.consts.POST:
        data: dict = request.get_json(force=True)
        mmpm.utils.log.info('Saving MagicMirror config file')
        print(data)

        try:
            with open(mmpm.consts.MAGICMIRROR_CONFIG_FILE, 'w') as config:
                config.write(data.get('code'))
        except IOError:
            return json.dumps(False)

        return json.dumps(True)


@app.route(api('magicmirror/custom-css'), methods=[mmpm.consts.GET, mmpm.consts.POST])
def magicmirror_custom_css():
    if request.method == mmpm.consts.GET:

        result: str = send_file(
            mmpm.consts.MAGICMIRROR_CUSTOM_CSS_FILE,
            attachment_filename='custom.css'
        ) if mmpm.consts.MAGICMIRROR_CUSTOM_CSS_FILE else '/* custom.css file not found. An empty file was created for you in its place */'

        mmpm.utils.log.info('Retrieving MagicMirror custom/custom.css')
        return result

    elif request.method == mmpm.consts.POST:
        data: dict = request.get_json(force=True)
        mmpm.utils.log.info('Saving MagicMirror custom/custom.css file')
        print(data)

        try:
            with open(mmpm.consts.MAGICMIRROR_CUSTOM_CSS_FILE, 'w') as custom_css:
                custom_css.write(data.get('code'))
        except IOError:
            return json.dumps(False)

        return json.dumps(True)


@app.route(api('magicmirror/start'), methods=[mmpm.consts.GET])
def magicmirror_start() -> str:
    '''
    Restart the MagicMirror by killing all associated processes, the
    re-running the startup script for MagicMirror

    Parameters:
        None

    Returns:
        bool: True if the command was called, False it appears that MagicMirror is currently running
    '''
    # there really isn't an easy way to capture return codes for the background process, so, for the first version, let's just be lazy for now
    # need to find way to capturing return codes

    # if these processes are all running, we assume MagicMirror is running currently
    # TODO: Change this to include functionality for pm2
    if mmpm.utils.get_pids('node') and mmpm.utils.get_pids('npm') and mmpm.utils.get_pids('electron'):
        mmpm.utils.log.info('MagicMirror appears to be running already. Returning False.')
        return json.dumps(False)

    mmpm.utils.log.info('MagicMirror does not appear to be running currently. Returning True.')
    mmpm.core.start_magicmirror()
    return json.dumps(True)


@app.route(api('magicmirror/restart'), methods=[mmpm.consts.GET])
def magicmirror_restart() -> str:
    '''
    Restart the MagicMirror by killing all associated processes, then
    re-running the startup script for MagicMirror

    Parameters:
        None

    Returns:
        bool: Always True only as a signal the process was called
    '''
    # same issue as the start-magicmirror api call
    mmpm.core.restart_magicmirror()
    return json.dumps(True)


@app.route(api('magicmirror/stop'), methods=[mmpm.consts.GET])
def magicmirror_stop() -> str:
    '''
    Stop the MagicMirror by killing all associated processes

    Parameters:
        None

    Returns:
        bool: Always True only as a signal the process was called
    '''
    # same sort of issue as the start-magicmirror call
    mmpm.core.stop_magicmirror()
    return json.dumps(True)


@app.route(api('magicmirror/upgrade'), methods=[mmpm.consts.GET])
def magicmirror_upgrade() -> str:
    mmpm.utils.log.info(f'Request to upgrade MagicMirror')
    mmpm.utils.log.info('Finished installing')

    mmpm.core.upgrade_magicmirror()

    # TODO: Change this to include functionality for pm2
    if mmpm.utils.get_pids('node') and mmpm.utils.get_pids('npm') and mmpm.utils.get_pids('electron'):
        mmpm.core.restart_magicmirror()

    return json.dumps(True)

#  -- END: MAGICMIRROR --

#  -- START: RASPBERRYPI --
@app.route(api('raspberrypi/restart'), methods=[mmpm.consts.GET])
def raspberrypi_restart() -> str:
    '''
    Reboot the RaspberryPi

    Parameters:
        None

    Returns:
        success (bool): If the command fails, False is returned. If success, the return will never reach the interface
    '''

    mmpm.utils.log.info('Restarting RaspberryPi')
    mmpm.core.stop_magicmirror()
    error_code, _, _ = mmpm.utils.run_cmd(['sudo', 'reboot'])
    # if success, it'll never get the response, but we'll know if it fails
    return json.dumps(bool(not error_code))


@app.route(api('raspberrypi/stop'), methods=[mmpm.consts.GET])
def raspberrypi_stop() -> str:
    '''
    Shut down the RaspberryPi

    Parameters:
        None

    Returns:
        success (bool): If the command fails, False is returned. If success, the return will never reach the interface
    '''

    mmpm.utils.log.info('Shutting down RaspberryPi')
    # if success, we'll never get the response, but we'll know if it fails
    mmpm.core.stop_magicmirror()
    error_code, _, _ = mmpm.utils.run_cmd(['sudo', 'shutdown', '-P', 'now'])
    return json.dumps(bool(not error_code))
#  -- END: RASPBERRYPI --

#  -- START: MMPM --
@app.route(api('mmpm/logs'), methods=[mmpm.consts.GET])
def download_log_files():
    os.chdir('/tmp')
    today = datetime.datetime.now()
    zip_file_name = f'mmpm-logs-{today.year}-{today.month}-{today.day}'
    shutil.make_archive(zip_file_name, 'zip', mmpm.consts.MMPM_LOG_DIR)
    return send_file(f'/tmp/{zip_file_name}.zip', attachment_filename='{}.zip'.format(zip_file_name), as_attachment=True)
#  -- END: MMPM --
