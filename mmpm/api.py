#!/usr/bin/env python3
import os
import json
import shutil
import datetime

from pathlib import Path, PosixPath
from flask_cors import CORS
from flask import Flask, request, send_file, render_template, send_from_directory, Response
from typing import List, Callable
from time import sleep

import mmpm.utils
import mmpm.consts
import mmpm.core
import mmpm.models
import mmpm.mmpm
from mmpm.logger import MMPMLogger
from mmpm.magicmirror.package import MagicMirrorPackage
from mmpm.env import MMPMEnv

logger = MMPMLogger.get_logger(__name__)
logger.setLevel(MMPMEnv.mmpm_log_level.get())

app = Flask(__name__, root_path="/var/www/mmpm", static_url_path="")
app.config['CORS_HEADERS'] = 'Content-Type'

resources: dict = {
    r'/*': {'origins': '*'},
    r'/api/*': {'origins': '*'},
    r'/socket.io/*': {'origins': '*'},
}

CORS(app)

_packages_ = mmpm.core.load_packages()


def __deserialize_selected_packages__(rqst, key: str = 'selected-packages') -> List[MagicMirrorPackage]:
    '''
    Helper method to extract a list of MagicMirrorPackage objects from Flask
    request object

    Parameters:
       request (werkzeug.wrappers.Request): the Flask request object

    Returns:
        selected_packages (List[MagicMirrorPackage]): extracted list of MagicMirrorPackage objects
    '''

    pkgs: dict = rqst.get_json(force=True)[key]

    modules_dir = Path(MMPMEnv.mmpm_root.get() / "modules")
    default_directory = lambda title: str(Path(modules_dir / title))

    for pkg in pkgs:
        if not pkg['directory']:
            pkg['directory'] = default_directory(pkg['title'])

    return [MagicMirrorPackage(**pkg) for pkg in pkgs]


@app.after_request # type: ignore
def after_request(response: Response) -> Response:
    '''
    Appends extra headers after each api request is sent to the server

    Parameters:
        response (flask.Response): the response object being returned to the frontend

    Returns
        response (flask.Response): the modified response object with new headers attached
    '''

    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route('/<path:path>', methods=[mmpm.consts.GET])
def static_proxy(path):
    return send_from_directory('./', path)


@app.route('/', methods=[mmpm.consts.GET, mmpm.consts.POST, mmpm.consts.DELETE])
def root():
    '''
    Returns the index.html page from the template folder as requested by the
    frontend back to the root url

    Parameters:
        None

    Returns:
        index (str): the index.html content as a string
    '''
    return render_template('index.html')


@app.errorhandler(500)
def server_error(error) -> Response:
    '''
    Sends back a verbose error message to the frontend alerting an error occurred

    Parameters:
        None

    Returns:
        response (flask.Response): the response object containing the error message
    '''
    return Response(f'An internal error occurred [{__name__}.py]: {error}', status=500)


#  -- START: PACKAGES --
@app.route('/api/packages/marketplace', methods=[mmpm.consts.GET])
def packages_marketplace() -> Response:
    '''
    Sends back all of the available packages in the MMPM/MagicMirror database

    Parameters:
        None

    Returns:
        response (flask.Response): the response object containing all the available packages
    '''
    logger.info('Sending all marketplace packages')
    return Response(json.dumps(_packages_, default=lambda pkg: pkg.serialize_full()))


@app.route('/api/packages/installed', methods=[mmpm.consts.GET])
def packages_installed() -> Response:
    '''
    Sends back all of the installed packages

    Parameters:
        None

    Returns:
        response (flask.Response): the response object containing all the installed packages
    '''
    logger.info('Sending all installed packages')
    return Response(json.dumps(mmpm.core.get_installed_packages(_packages_), default=lambda pkg: pkg.serialize_full()))


@app.route('/api/packages/external', methods=[mmpm.consts.GET])
def packages_external() -> Response:
    '''
    Sends back all the external packages created by the user to the frontend

    Parameters:
        None

    Returns:
        response (flask.Response): the response object containing all the external packages
    '''
    logger.info('Sending all external packages')
    return Response(json.dumps(mmpm.core.load_external_packages(), default=lambda pkg: pkg.serialize_full()))


@app.route('/api/packages/install', methods=[mmpm.consts.POST])
def packages_install() -> Response:
    '''
    Installs the selected packages on the user's device

    Parameters:
        None

    Returns:
        response (flask.Response): the result following the installation, success or failure
    '''
    selected_packages: List[MagicMirrorPackage] = __deserialize_selected_packages__(request)
    failures: List[dict] = []

    for package in selected_packages:
        error = mmpm.core.install_package(package, assume_yes=True)

        if error:
            logger.error(f'Failed to install {package.title} with error of: {error}')
            failures.append({'package': package.serialize(), 'error': error})
        else:
            logger.info(f'Installed {package.title}')

    return Response(json.dumps(failures))


@app.route('/api/packages/remove', methods=[mmpm.consts.POST])
def packages_remove() -> Response:
    '''
    Removes the selected packages from the user's device

    Parameters:
        None

    Returns:
        response (flask.Response): the result following the removal, success or failure
    '''
    # not bothering with serialization since the directory is already included in the request
    selected_packages: List[dict] = request.get_json(force=True)['selected-packages']
    failures: List[dict] = []

    for package in selected_packages:
        directory = package['directory']
        logger.info(f"Attempting to removing {package['title']} at {directory}")

        try:
            shutil.rmtree(directory)
        except (PermissionError, Exception) as error:
            failures.append({'package': package, 'error': f"Cannot remove {directory}: {str(error)}"})
        finally:
            sleep(0.05)

    return Response(json.dumps(failures))


@app.route('/api/packages/upgrade', methods=[mmpm.consts.POST])
def packages_upgrade() -> Response:
    '''
    Upgrades the selected packages on the user's device

    Parameters:
        None

    Returns:
        response (flask.Response): the result following the package upgrade(s), success or failure
    '''
    selected_packages: List[MagicMirrorPackage] = __deserialize_selected_packages__(request)
    logger.info(f'Request to upgrade {selected_packages}')

    failures: List[dict] = []

    for package in selected_packages:
        error = package.upgrade()
        if error:
            logger.error(f'Failed to upgrade {package.title} with error of: {error}')
            failures.append({'package': package.serialize(), 'error': error})

    logger.info('Finished executing upgrades')
    return Response(json.dumps(failures))


@app.route('/api/packages/update', methods=[mmpm.consts.GET])
def packages_update() -> Response:
    '''
    Checks for package/application updates within the users MMPM/MagicMirror installation

    Parameters:
        None

    Returns:
        response (flask.Response): the result of the update check, success or failure as a boolean
    '''
    try:
        mmpm.core.check_for_package_updates(_packages_)
        mmpm.core.check_for_mmpm_updates()
        mmpm.core.check_for_magicmirror_updates()
    except Exception as error:
        logger.error(str(error))
        return Response(json.dumps(False))

    return Response(json.dumps(True))

@app.route('/api/packages/upgradable', methods=[mmpm.consts.GET])
def packages_upgradable() -> Response:
    '''
    Sends back a JSON object detailing which packages/applications have available upgrades

    Parameters:
        None

    Returns:
        response (flask.Response): the object containing which packages/applications have available upgrades
    '''
    logger.info('Request to get upgradable packages')
    available_upgrades: dict = mmpm.core.get_available_upgrades()

    MMPM_MAGICMIRROR_ROOT: str = MMPMEnv.mmpm_root.get()

    available_upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES] = [
        pkg.serialize_full() for pkg in available_upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.PACKAGES]
    ]

    available_upgrades[MMPM_MAGICMIRROR_ROOT][mmpm.consts.MMPM] = available_upgrades[mmpm.consts.MMPM]
    return Response(json.dumps(available_upgrades[MMPM_MAGICMIRROR_ROOT]))
#  -- END: PACKAGES --


#  -- START: EXTERNAL PACKAGES --
@app.route('/api/external-packages/add', methods=[mmpm.consts.POST])
def external_packages_add() -> Response:
    '''
    Adds an External Package to the user's database

    Parameters:
        None

    Returns:
        response (flask.Response): the success or failure of adding the external package to the database
    '''
    package: dict = request.get_json(force=True)['external-package']

    failures: List[dict] = []

    error: str = mmpm.core.add_external_package(
        title=package.get('title'),
        author=package.get('author'),
        description=package.get('description'),
        repo=package.get('repository')
    )

    failures.append({'package': package, 'error': error})
    return Response(json.dumps({'error': "no_error" if not error else error}))


@app.route('/api/external-packages/remove', methods=[mmpm.consts.DELETE])
def external_packages_remove() -> Response:
    '''
    Removes an External Package from the user's database

    Parameters:
        None

    Returns:
        response (flask.Response): the success or failure of removing the external package from the database
    '''
    selected_packages: List[MagicMirrorPackage] = __deserialize_selected_packages__(request, 'external-packages')
    logger.info('Request to remove external sources')

    ext_packages: dict = {mmpm.consts.EXTERNAL_PACKAGES: []}
    marked_for_removal: list = []
    external_packages: List[MagicMirrorPackage] = mmpm.core.load_external_packages()[mmpm.consts.EXTERNAL_PACKAGES]

    for selected_package in selected_packages:
        for external_package in external_packages:
            if external_package == selected_package:
                marked_for_removal.append(external_package)
                logger.info(f'Found matching external module ({external_package.title}) and marked for removal')

    for package in marked_for_removal:
        external_packages.remove(package)
        logger.info(f'Removed {package.title}')

    try:
        with open(mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE, mode='w', encoding="utf-8") as mmpm_ext_srcs:
            json.dump(ext_packages, mmpm_ext_srcs)

        logger.info(f'Wrote updated external modules to {mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE}')

    except IOError as error:
        logger.error(error)
        return Response(json.dumps({'error': str(error)}))

    logger.info(f'Wrote external modules to {mmpm.consts.MMPM_EXTERNAL_PACKAGES_FILE}')
    return Response(json.dumps({'error': "no_error"}))
#  -- END: EXTERNAL PACKAGES --


#  -- START: MAGICMIRROR --
@app.route('/api/magicmirror/config', methods=[mmpm.consts.GET, mmpm.consts.POST])
def magicmirror_config() -> Response:
    '''
    Retrieves the user's MagicMirror config.js, and sends file contents to frontend

    Parameters:
        None

    Returns:
        response (flask.Response): the file contents
    '''
    magicmirror_config_dir: PosixPath = Path(MMPMEnv.mmpm_root.get() / "config")
    magicmirror_config_file: PosixPath = Path(MAGICMIRROR_CONFIG_DIR) / 'config.js'

    if request.method == mmpm.consts.GET:
        if not os.path.exists(magicmirror_config_file):
            does_not_exist: str = f'// {magicmirror_config_file} not found. An empty file was created for you in its place'
            try:
                magicmirror_config_dir.mkdir(parents=True, exist_ok=True)
                magicmirror_config_file.touch(mode=0o664, exist_ok=True)
                return Response(does_not_exist)
            except OSError:
                return Response(does_not_exist)

        logger.info('Retrieving MagicMirror config')

        return send_file(magicmirror_config_file, 'config.js')

    data: dict = request.get_json(force=True)
    logger.info('Saving MagicMirror config file')

    try:
        with open(magicmirror_config_file, mode='w', encoding="utf-8") as config:
            config.write(data.get('code'))
    except IOError:
        return Response(json.dumps(False))

    return Response(json.dumps(True))


@app.route('/api/magicmirror/custom-css', methods=[mmpm.consts.GET, mmpm.consts.POST])
def magicmirror_custom_css() -> Response:
    '''
    Retrieves the user's MagicMirror custom.css, and sends file contents to frontend

    Parameters:
        None

    Returns:
        response (flask.Response): the file contents
    '''
    MAGICMIRROR_CSS_DIR: PosixPath = Path(MMPMEnv.mmpm_root.get() / "css")
    MAGICMIRROR_CUSTOM_CSS_FILE: PosixPath = Path(MAGICMIRROR_CSS_DIR) / 'custom.css'

    if request.method == mmpm.consts.GET:
        if not os.path.exists(MAGICMIRROR_CUSTOM_CSS_FILE):
            try:
                MAGICMIRROR_CSS_DIR.mkdir(parents=True, exist_ok=True)
                MAGICMIRROR_CUSTOM_CSS_FILE.touch(mode=0o664, exist_ok=True)
            except OSError:
                message: str = f'/* File not found. Unable to create {MAGICMIRROR_CUSTOM_CSS_FILE}. Is the MagicMirror directory owned by root? */'
                logger.error(message)
                return Response(message)

        logger.info(f'Retrieving MagicMirror {MAGICMIRROR_CUSTOM_CSS_FILE}')
        return send_file(MAGICMIRROR_CUSTOM_CSS_FILE, 'custom.css')

    # POST
    data: dict = request.get_json(force=True)
    logger.info(f'Saving MagicMirror {MAGICMIRROR_CUSTOM_CSS_FILE}')

    try:
        with open(MAGICMIRROR_CUSTOM_CSS_FILE, mode='w', encoding="utf-8") as custom_css:
            custom_css.write(data.get('code'))
    except IOError:
        return Response(json.dumps(False))

    return Response(json.dumps(True))


@app.route('/api/magicmirror/start', methods=[mmpm.consts.GET])
def magicmirror_start() -> Response:
    '''
    Restart the MagicMirror by killing all associated processes, the
    re-running the startup script for MagicMirror

    Parameters:
        None

    Returns:
        response (flask.Response): response containing boolean of True if the
        command was called, False it appears that MagicMirror is currently
        running
    '''
    # there really isn't an easy way to capture return codes for the background
    # process

    # if these processes are all running, we assume MagicMirror is running currently
    if mmpm.utils.is_magicmirror_running():
        logger.info('MagicMirror appears to be running already. Returning False.')
        return Response(json.dumps({'error': 'MagicMirror appears to be running already'}))

    logger.info('MagicMirror does not appear to be running currently. Returning True.')
    mmpm.core.start_magicmirror()
    return Response(json.dumps({'error': ''}))


@app.route('/api/magicmirror/restart', methods=[mmpm.consts.GET])
def magicmirror_restart() -> Response:
    '''
    Restart the MagicMirror by killing all associated processes, then
    re-running the startup script for MagicMirror

    Parameters:
        None

    Returns:
        response(flask.Response): response object containing boolean, which is
        always True only as a signal the process was called
    '''
    # same issue as the start-magicmirror api call
    mmpm.core.restart_magicmirror()
    return Response(json.dumps(True))


@app.route('/api/magicmirror/stop', methods=[mmpm.consts.GET])
def magicmirror_stop() -> Response:
    '''
    Stop the MagicMirror by killing all associated processes

    Parameters:
        None

    Returns:
        response (flask.Response): response containing boolean that is always
        True only as a signal the process was called
    '''
    # same sort of issue as the start-magicmirror call
    mmpm.core.stop_magicmirror()
    return Response(json.dumps(True))


@app.route('/api/magicmirror/upgrade', methods=[mmpm.consts.GET])
def magicmirror_upgrade() -> Response:
    '''
    Upgrades the MagicMirror application from the Control Center of the GUI

    Parameters:
        None

    Returns:
        response (flask.Response): response containing an error message, if any
        error was encountered. If no error was generated, an empty string is
        returned
    '''
    logger.info('Request to upgrade MagicMirror')
    logger.info('Finished installing')

    error: str = mmpm.core.upgrade_magicmirror()

    if mmpm.utils.is_magicmirror_running():
        mmpm.core.restart_magicmirror()

    return Response(json.dumps({'error': error}))


@app.route('/api/magicmirror/install-mmpm-module', methods=[mmpm.consts.GET])
def magicmirror_install_mmpm_module() -> Response:
    '''
    Install the MMPM MagicMirror module in the user's module path

    Parameters:
        None

    Returns:
        response (flask.Response): response containing an error message, if any
        error was encountered. If no error was generated, an empty string is
        returned
    '''
    return Response(json.dumps({'error': mmpm.core.install_mmpm_as_magicmirror_module(assume_yes=True)}))
#  -- END: MAGICMIRROR --


#  -- START: RASPBERRYPI --
@app.route('/api/raspberrypi/restart', methods=[mmpm.consts.GET])
def raspberrypi_restart() -> Response:
    '''
    Reboot the RaspberryPi

    Parameters:
        None

    Returns:
        response (flask.Response): If the command fails, False is returned. If
        success, the return will never reach the interface
    '''
    logger.info('Restarting RaspberryPi')
    mmpm.core.stop_magicmirror()
    error_code, _, _ = mmpm.utils.run_cmd(['sudo', 'reboot'])
    # if success, it'll never get the response, but we'll know if it fails
    return Response(json.dumps(bool(not error_code)))


@app.route('/api/raspberrypi/stop', methods=[mmpm.consts.GET])
def raspberrypi_stop() -> Response:
    '''
    Shut down the RaspberryPi

    Parameters:
        None

    Returns:
        response (flask.Response): If the command fails, False is returned. If success,
        the return will never reach the interface
    '''
    logger.info('Shutting down RaspberryPi')
    # if success, we'll never get the response, but we'll know if it fails
    mmpm.core.stop_magicmirror()
    error_code, _, _ = mmpm.utils.run_cmd(['sudo', 'shutdown', '-P', 'now'])
    return Response(json.dumps(bool(not error_code)))


#  -- START: MMPM --
@app.route('/api/mmpm/download-logs', methods=[mmpm.consts.GET])
def download_log_files() -> Response:
    '''
    Compresses the log files generated by MMPM, and sends them back to the frontend for the user to download.

    Parameters:
        None

    Returns:
        response (flask.Response): the log files as a single zip file
    '''
    os.chdir('/tmp')
    today = datetime.datetime.now()
    zip_file_name = f'mmpm-logs-{today.year}-{today.month}-{today.day}'
    shutil.make_archive(zip_file_name, 'zip', mmpm.consts.MMPM_LOG_DIR)

    return send_file(f'/tmp/{zip_file_name}.zip', f'{zip_file_name}.zip', as_attachment=True)


# this is stupid and should be condensed
@app.route('/api/mmpm/environment-vars', methods=[mmpm.consts.GET])
def mmpm_environment_vars() -> Response:
    '''
    Sends the MMPM environment variables as json object to the frontend

    Parameters:
        None

    Returns:
        response (flask.Response): a JSON object containing the MMPM environment variables
    '''
    env_vars: dict = {}

    with open(mmpm.consts.MMPM_ENV_FILE, mode='r', encoding="utf-8") as env:
        try:
            env_vars = json.load(env)
        except json.JSONDecodeError:
            pass

    return Response(json.dumps(env_vars))


@app.route('/api/mmpm/environment-vars-file', methods=[mmpm.consts.GET, mmpm.consts.POST])
def mmpm_environment_vars_file() -> Response:
    '''
    If the frontend sends a GET request, the MMPM environment variables
    contents is sent back. If the request method is a POST, then the updated
    file contents are written to the mmpm-env.json file.

    Parameters:
        None

    Returns:
        response (flask.Response): the MMPM environment variables file contents
        if it is a GET, otherwise the file contents are written to the user's
        mmpm-env.json file
    '''
    if request.method == mmpm.consts.GET:
        return send_file(mmpm.consts.MMPM_ENV_FILE, 'mmpm-env.json')

    data: dict = request.get_json(force=True)
    logger.info('Saving MMPM environment variables file')

    try:
        with open(mmpm.consts.MMPM_ENV_FILE, mode='w', encoding="utf-8") as config:
            config.write(data.get('code'))
    except IOError:
        return Response(json.dumps(False))

    return Response(json.dumps(True))


@app.route('/api/mmpm/version', methods=[mmpm.consts.GET])
def mmpm_version() -> Response:
    '''
    Gets the MMPM version number

    Parameters:
        None

    Returns:
        response (flask.Response): the MMPM version number
    '''
    return Response(json.dumps({'version': mmpm.mmpm.__version__}))
