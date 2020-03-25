#!/usr/bin/env python3
import eventlet
eventlet.monkey_patch()

import json
from flask_cors import CORS
from flask import Flask, request, send_file, render_template, send_from_directory, Response
from mmpm import core, utils
from mmpm.utils import log
from shelljob.proc import Group
from flask_socketio import SocketIO
from typing import Tuple
import os


MMPM_EXECUTABLE: list = [os.path.join(os.path.expanduser('~'), '.local', 'bin', 'mmpm')]

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

GET: str = 'GET'
POST: str = 'POST'
DELETE: str = 'DELETE'


def __api__(path: str = '') -> str:
    '''
    Returns formatted string containing /api base path

    Parameters:
        path (str): url path

    Returns:
        str
    '''
    return f'/api/{path}'


def __modules__() -> dict:
    '''
    Returns dictionary of MagicMirror modules

    Parameters:
        None

    Returns:
        dict
    '''
    modules, _, _, _ = core.load_modules()
    return modules


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
    log.logger.info(f"Executing {command}")
    process.run(command)

    try:
        while process.is_pending():
            log.logger.info('Process pending')
            for _, line in process.readlines():
                socketio.emit('live-terminal-stream', {'data': str(line.decode('utf-8'))})
        log.logger.info(f'Process complete: {command}')
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
    log.logger.critical(message)
    return message, 500


@socketio.on('connect')
def on_connect() -> None:
    message: str = 'Server connected'
    log.logger.info(message)
    socketio.emit('connected', {'data': message})


@socketio.on('disconnect')
def on_disconnect() -> None:
    message: str = 'Server disconnected'
    log.logger.info(message)
    socketio.emit(message, {'data': message})

@app.after_request
def after_request(response: Response) -> Response:
    log.logger.info('Headers being added after the request')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response


@app.route('/<path:path>', methods=[GET])
def static_proxy(path):
    return send_from_directory('./', path)


@app.route('/', methods=[GET, POST, DELETE])
def root() -> str:
    return render_template('index.html')


@app.errorhandler(500)
def server_error(error) -> Tuple[str, int]:
    return f'An internal error occurred [{__name__}.py]: {error}', 500


@app.route(__api__('all-modules'), methods=[GET])
def get_magicmirror_modules() -> dict:
    return __modules__()


@app.route(__api__('install-modules'), methods=[POST])
def install_magicmirror_modules() -> str:
    selected_modules: list = request.get_json(force=True)['selected-modules']
    log.logger.info(f'Request to install {selected_modules}')
    process: Group = Group()
    Response(
        __stream_cmd_output__(process, ['-i'] + [selected_module['title'] for selected_module in selected_modules]),
        mimetype='text/plain'
    )

    log.logger.info('Finished installing')
    return json.dumps(True)


@app.route(__api__('uninstall-modules'), methods=[POST])
def remove_magicmirror_modules() -> Response:
    selected_modules: list = request.get_json(force=True)['selected-modules']
    process: Group = Group()

    return Response(
        __stream_cmd_output__(process, ['-r'] + [selected_module['title'] for selected_module in selected_modules]),
        mimetype='text/plain'
    )


@app.route(__api__('upgrade-modules'), methods=[POST])
def upgrade_magicmirror_modules() -> str:
    selected_modules: list = request.get_json(force=True)['selected-modules']
    log.logger.info(f'Request to upgrade {selected_modules}')
    process: Group = Group()

    Response(
        __stream_cmd_output__(process, ['-U'] + [selected_module['title'] for selected_module in selected_modules]),
        mimetype='text/plain'
    )

    log.logger.info('Finished update')
    return json.dumps(True)


@app.route(__api__('all-installed-modules'), methods=[GET])
def get_installed_magicmirror_modules() -> dict:
    return core.get_installed_modules(__modules__())


@app.route(__api__('all-external-module-sources'), methods=[GET])
def get_external__modules__sources() -> dict:
    ext_sources: dict = {utils.EXTERNAL_MODULE_SOURCES: []}
    try:
        with open(utils.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
            ext_sources[utils.EXTERNAL_MODULE_SOURCES] = json.load(mmpm_ext_srcs)[utils.EXTERNAL_MODULE_SOURCES]
    except IOError:
        pass
    return ext_sources


@app.route(__api__('add-external-module-source'), methods=[POST])
def add_external_module_source() -> str:
    external_source: dict = request.get_json(force=True)['external-source']
    try:
        success: bool = core.add_external_module_source(
            title=external_source.get('title'),
            author=external_source.get('author'),
            desc=external_source.get('description'),
            repo=external_source.get('repository')
        )
        return json.dumps(bool(success))
    except Exception:
        return json.dumps(False)


@app.route(__api__('remove-external-module-source'), methods=[DELETE])
def remove_external_module_source() -> str:
    selected_sources: list = request.get_json(force=True)['external-sources']
    log.logger.info(f'Request to remove external sources')

    process: Group = Group()
    Response(
        __stream_cmd_output__(process, ['-r'] + [external_source['title'] for external_source in selected_sources] + ['--ext-module-src']),
        mimetype='text/plain'
    )

    return json.dumps(True)


@app.route(__api__('refresh-modules'), methods=[GET])
def force_refresh_magicmirror_modules() -> str:
    log.logger.info(f'Recieved request to refresh modules')
    process: Group = Group()
    Response(__stream_cmd_output__(process, ['-f']), mimetype='text/plain')
    log.logger.info('Finished refresh')
    return json.dumps(True)


@app.route(__api__('get-magicmirror-config'), methods=[GET])
def get_magicmirror_config():
    path: str = utils.MAGICMIRROR_CONFIG_FILE
    result: str = send_file(path, attachment_filename='config.js') if path else ''
    log.logger.info('Retrieving MagicMirror config')
    return result


@app.route(__api__('update-magicmirror-config'), methods=[POST])
def update_magicmirror_config() -> str:
    data: dict = request.get_json(force=True)
    log.logger.info('Saving MagicMirror config file')

    try:
        with open(utils.MAGICMIRROR_CONFIG_FILE, 'w') as config:
            config.write(data.get('code'))
    except IOError:
        return json.dumps(False)
    return json.dumps(True)
