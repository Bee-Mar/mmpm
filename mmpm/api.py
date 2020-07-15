#!/usr/bin/env python3
import eventlet
eventlet.monkey_patch()

import os
import pathlib
import json
import shutil
import datetime

from flask_cors import CORS
from flask import Flask, request, send_file, render_template, send_from_directory, Response
from flask_socketio import SocketIO
from typing import Tuple, List

import mmpm.utils
import mmpm.consts
import mmpm.core
import mmpm.models

MagicMirrorPackage = mmpm.models.MagicMirrorPackage
get_env = mmpm.utils.get_env

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
flask_sio = SocketIO(app, cors_allowed_origins='*', logger=mmpm.utils.log)

api = lambda path: f'/api/{path}'

_packages_ = mmpm.core.load_packages()


def __get_selected_packages__(rqst, key: str = 'selected-packages') -> List[MagicMirrorPackage]:
    '''
    Helper method to extract a list of MagicMirrorPackage objects from Flask
    request object

    Parameters:
       request (werkzeug.wrappers.Request): the Flask request object

    Returns:
        selected_packages (List[MagicMirrorPackage]): extracted list of MagicMirrorPackage objects
    '''
    pkgs: dict = rqst.get_json(force=True)[key]

    MAGICMIRROR_MODULES_DIR: str = os.path.join(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV), 'modules')

    # more-or-less a bandaid to the larger problem of aligning the data structure in angular
    for pkg in pkgs:
        del pkg['category']

        if not pkg['directory']:
            mmpm.utils.log.info(pkg)
            pkg['directory'] = os.path.normpath(os.path.join(MAGICMIRROR_MODULES_DIR, pkg['title']))

    return [MagicMirrorPackage(**pkg) for pkg in pkgs]


@flask_sio.on_error()
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


@flask_sio.on('connect')
def on_connect() -> None:
    mmpm.utils.log.info('connected to socketio')


@flask_sio.on('disconnect')
def on_disconnect() -> None:
    message: str = 'Server disconnected'
    mmpm.utils.log.info(message)


@app.after_request
def after_request(response: Response) -> Response:
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
    return json.dumps(_packages_, default=lambda pkg: pkg.serialize_full())


@app.route(api('packages/installed'), methods=[mmpm.consts.GET])
def packages_installed() -> str:
    mmpm.utils.log.info('Sending all installed packages')
    return json.dumps(mmpm.core.get_installed_packages(_packages_), default=lambda pkg: pkg.serialize_full())


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

        os.system(f"rm -rf '{package.directory}'")
        mmpm.utils.log.info(f'Removed {package.directory}')

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


@app.route(api('packages/update'), methods=[mmpm.consts.GET])
def packages_update() -> str:
    try:
        mmpm.core.check_for_package_updates(_packages_)
        mmpm.core.check_for_mmpm_updates()
        mmpm.core.check_for_magicmirror_updates()
    except Exception as error:
        mmpm.utils.log.error(str(error))
        return json.dumps(False)

    return json.dumps(True)

@app.route(api('packages/upgradeable'), methods=[mmpm.consts.GET])
def packages_upgradeable() -> str:
    mmpm.utils.log.info(f'Request to get upgradeable packages')
    available_upgrades: dict = mmpm.core.get_available_upgrades()

    for key in available_upgrades:
        if key != mmpm.consts.MMPM:
            available_upgrades[key][mmpm.consts.PACKAGES] = [
                pkg.serialize_full() for pkg in available_upgrades[key][mmpm.consts.PACKAGES]
            ]

    MMPM_MAGICMIRROR_ROOT: str = os.path.normpath(os.path.join(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV)))
    return json.dumps(available_upgrades[MMPM_MAGICMIRROR_ROOT])


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
    selected_packages: List[MagicMirrorPackage] = __get_selected_packages__(request, 'external-packages')
    mmpm.utils.log.info(f'Request to remove external sources')

    ext_packages: dict = {mmpm.consts.EXTERNAL_PACKAGES: []}
    marked_for_removal: list = []
    external_packages: List[MagicMirrorPackage] = mmpm.core.load_external_packages()[mmpm.consts.EXTERNAL_PACKAGES]

    for selected_package in selected_packages:
        for external_package in external_packages:
            if external_package == selected_package:
                marked_for_removal.append(external_package)
                mmpm.utils.log.info(f'Found matching external module ({external_package.title}) and marked for removal')

    for package in marked_for_removal:
        external_packages.remove(package)
        mmpm.utils.log.info(f'Removed {package.title}')

    try:
        with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, 'w') as mmpm_ext_srcs:
            json.dump(ext_packages, mmpm_ext_srcs)
        mmpm.utils.log.info(f'Wrote updated external modules to {mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE}')
    except IOError as error:
        mmpm.utils.log.error(error)
        return json.dumps({'error': str(error)})

    mmpm.utils.log.info(f'Wrote external modules to {mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE}')
    return json.dumps({'error': "no_error"})
#  -- END: EXTERNAL PACKAGES --


#  -- START: MAGICMIRROR --
@app.route(api('magicmirror/config'), methods=[mmpm.consts.GET, mmpm.consts.POST])
def magicmirror_config() -> str:
    if request.method == mmpm.consts.GET:
        MAGICMIRROR_CONFIG_DIR: str = os.path.join(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV), 'config')
        MAGICMIRROR_CONFIG_FILE: str = os.path.join(MAGICMIRROR_CONFIG_DIR, 'config.js')

        if not os.path.exists(MAGICMIRROR_CONFIG_FILE):
            try:
                pathlib.Path(MAGICMIRROR_CONFIG_DIR).mkdir(parents=True, exist_ok=True)
                pathlib.Path(MAGICMIRROR_CONFIG_FILE).touch(mode=0o664, exist_ok=True)
                return f'// {MAGICMIRROR_CONFIG_FILE} not found. An empty file was created for you in its place'
            except OSError:
                pass
        else:
            result: str = send_file(MAGICMIRROR_CONFIG_FILE, attachment_filename='config.js')

        mmpm.utils.log.info('Retrieving MagicMirror config')
        return result

    elif request.method == mmpm.consts.POST:
        data: dict = request.get_json(force=True)
        mmpm.utils.log.info('Saving MagicMirror config file')

        try:
            with open(MAGICMIRROR_CONFIG_FILE, 'w') as config:
                config.write(data.get('code'))
        except IOError:
            return json.dumps(False)

        return json.dumps(True)


@app.route(api('magicmirror/custom-css'), methods=[mmpm.consts.GET, mmpm.consts.POST])
def magicmirror_custom_css() -> str:
    if request.method == mmpm.consts.GET:
        MAGICMIRROR_CUSTOM_DIR: str = os.path.join(get_env(mmpm.consts.MMPM_MAGICMIRROR_ROOT_ENV), 'custom')
        MAGICMIRROR_CUSTOM_CSS_FILE: str = os.path.join(MAGICMIRROR_CUSTOM_DIR, 'custom.css')

        if not os.path.exists(MAGICMIRROR_CUSTOM_CSS_FILE):
            try:
                pathlib.Path(MAGICMIRROR_CUSTOM_DIR).mkdir(parents=True, exist_ok=True)
                pathlib.Path(MAGICMIRROR_CUSTOM_CSS_FILE).touch(mode=0o664, exist_ok=True)
            except OSError:
                message: str = f'/* File not found. Unable to create {MAGICMIRROR_CUSTOM_CSS_FILE}. Is the MagicMirror directory owned by root? */'
                mmpm.utils.log.error(message)
                return message

        result: str = send_file(MAGICMIRROR_CUSTOM_CSS_FILE, attachment_filename='custom.css')
        mmpm.utils.log.info(f'Retrieving MagicMirror {MAGICMIRROR_CUSTOM_CSS_FILE}')
        return result

    elif request.method == mmpm.consts.POST:
        data: dict = request.get_json(force=True)
        mmpm.utils.log.info(f'Saving MagicMirror {MAGICMIRROR_CUSTOM_CSS_FILE}')

        try:
            with open(MAGICMIRROR_CUSTOM_CSS_FILE, 'w') as custom_css:
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
    # there really isn't an easy way to capture return codes for the background
    # process

    # if these processes are all running, we assume MagicMirror is running currently
    if mmpm.utils.is_magicmirror_running():
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

    if mmpm.utils.is_magicmirror_running():
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
@app.route(api('mmpm/download-logs'), methods=[mmpm.consts.GET])
def download_log_files():
    os.chdir('/tmp')
    today = datetime.datetime.now()
    zip_file_name = f'mmpm-logs-{today.year}-{today.month}-{today.day}'
    shutil.make_archive(zip_file_name, 'zip', mmpm.consts.MMPM_LOG_DIR)
    return send_file(f'/tmp/{zip_file_name}.zip', attachment_filename='{}.zip'.format(zip_file_name), as_attachment=True)


@app.route(api('mmpm/environment-vars'), methods=[mmpm.consts.GET])
def mmpm_environment_vars() -> str:
    env_vars: dict = {}

    with open(mmpm.consts.MMPM_ENV_FILE, 'r') as env:
        try:
            env_vars = json.load(env)
        except json.JSONDecodeError:
            pass

    return json.dumps(env_vars)


@app.route(api('mmpm/environment-vars-file'), methods=[mmpm.consts.GET, mmpm.consts.POST])
def mmpm_environment_vars_file() -> str:
    if request.method == mmpm.consts.GET:
        result: str = send_file(mmpm.consts.MMPM_ENV_FILE, attachment_filename='mmpm-env.json')
        return result

    elif request.method == mmpm.consts.POST:
        data: dict = request.get_json(force=True)
        mmpm.utils.log.info('Saving MMPM environment variables file')

        try:
            with open(mmpm.consts.MMPM_ENV_FILE, 'w') as config:
                config.write(data.get('code'))
        except IOError:
            return json.dumps(False)

        return json.dumps(True)
