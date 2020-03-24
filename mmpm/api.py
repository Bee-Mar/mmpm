#!/usr/bin/env python3
import eventlet
eventlet.monkey_patch()

import json
from flask_cors import CORS, cross_origin
from flask import Flask, request, send_file, render_template, send_from_directory, Response
from mmpm import core, utils
from mmpm.utils import log
from shelljob import proc
from flask_socketio import SocketIO, send, emit
import os

MMPM_EXECUTABLE: list = [os.path.join(os.path.expanduser('~'), '.local', 'bin', 'mmpm')]

app: object = Flask(
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


CORS(app, send_wildcard=True)
socketio: object = SocketIO(app, cors_allowed_origins='*')

GET: str = 'GET'
POST: str = 'POST'
DELETE: str = 'DELETE'


def __api__(path='') -> str:
    ''' Returns formatted string containing /api base path'''
    return f'/api/{path}'


def __modules__() -> dict:
    ''' Returns dictionary of MagicMirror modules '''
    modules, _, _, _ = core.load_modules()
    return modules


def __callback__() -> None:
    log.logger.info('Acked')

def __stream_cmd_output__(process: proc.Group, cmd: list) -> None:
    command: list = MMPM_EXECUTABLE + cmd
    log.logger.info(f"Executing {command}")
    process.run(command)

    try:
        while process.is_pending():
            log.logger.info('Process pending')
            for proc, line in process.readlines():
                socketio.emit('live-terminal-stream', {'data': str(line.decode('utf-8'))})
        log.logger.info(f'Process complete: {command}')
    except Exception:
        pass


@socketio.on_error()
def error_handler(error) -> tuple:
    message: str = f'An internal error occurred within flask_socketio: {error}'
    log.logger.critical(message)
    return message, 500


@socketio.on('connect')
def test_connection() -> None:
    message: str = 'Server connected'
    log.logger.info(message)
    socketio.emit('connected', {'data': message})


@socketio.on('disconnect')
def test_connection() -> None:
    message: str = 'Server disconnected'
    log.logger.info(message)
    socketio.emit(message, {'data': message})

@app.after_request
def after_request(response: Response) -> Response:
    log.logger.info('')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
    return response


@app.route('/<path:path>', methods=[GET])
def static_proxy(path):
    return send_from_directory('./', path)


@app.route('/', methods=[GET, POST, DELETE])
def root():
    return render_template('index.html')


@app.errorhandler(500)
def server_error(error):
    return f'An internal error occurred [{__name__}.py]: {error}', 500


@app.route(__api__('all-modules'), methods=[GET])
def get_magicmirror_modules():
    return __modules__()


@app.route(__api__('install-modules'), methods=[POST])
def install_magicmirror_modules():
    selected_modules = request.get_json(force=True)['selected-modules']
    log.logger.info(f'Request to install {selected_modules}')
    process = proc.Group()
    response = Response(
        __stream_cmd_output__(process, ['-i'] + [selected_module['title'] for selected_module in selected_modules]),
        mimetype='text/plain'
    )

    log.logger.info('Finished installing')
    return json.dumps(True)


@app.route(__api__('uninstall-modules'), methods=[POST])
def remove_magicmirror_modules():
    selected_modules = request.get_json(force=True)['selected-modules']
    process = proc.Group()
    return Response(
        __stream_cmd_output__(process, ['-r'] + [selected_module['title'] for selected_module in selected_modules]),
        mimetype='text/plain'
    )


@app.route(__api__('update-selected-modules'), methods=[POST])
def update_magicmirror_modules():
    modules, _, _, _ = core.load_modules()
    core.remove_modules(modules, request.args.get('modules_to_remove'))
    return True


@app.route(__api__('all-installed-modules'), methods=[GET])
def get_installed_magicmirror_modules():
    return core.get_installed_modules(__modules__())


@app.route(__api__('all-external-module-sources'), methods=[GET])
def get_external__modules__sources():
    ext_sources = {utils.EXTERNAL_MODULE_SOURCES: []}
    try:
        with open(utils.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
            ext_sources[utils.EXTERNAL_MODULE_SOURCES] = json.load(
                mmpm_ext_srcs)[utils.EXTERNAL_MODULE_SOURCES]
    except IOError:
        pass
    return ext_sources


@app.route(__api__('update-modules'), methods=[GET])
def update_installed_modules():
    ext_sources = {utils.EXTERNAL_MODULE_SOURCES: []}
    try:
        with open(utils.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
            ext_sources[utils.EXTERNAL_MODULE_SOURCES] = json.load(
                mmpm_ext_srcs)[utils.EXTERNAL_MODULE_SOURCES]
    except IOError:
        pass
    return ext_sources


@app.route(__api__('add-external-module-source'), methods=[POST])
def add_external_module_source():
    external_source = request.get_json(force=True)['external-source']
    try:
        success = core.add_external_module_source(
            title=external_source.get('title'),
            author=external_source.get('author'),
            desc=external_source.get('description'),
            repo=external_source.get('repository')
        )
        return json.dumps(True if success else False)
    except Exception:
        return json.dumps(False)


@app.route(__api__('remove-external-module-source'), methods=[DELETE])
def remove_external_module_source():
    selected_sources = request.get_json(force=True)['external-sources']
    log.logger.info(f'Request to remove external sources')

    process = proc.Group()
    response = Response(
        __stream_cmd_output__(process, ['-r'] + [external_source['title'] for external_source in selected_sources] + ['--ext-module-src']),
        mimetype='text/plain'
    )

    return json.dumps(True)


@app.route(__api__('refresh-modules'), methods=[GET])
def force_refresh_magicmirror_modules():
    log.logger.info(f'Recieved request to refresh modules')
    process = proc.Group()
    response = Response(__stream_cmd_output__(process, ['-f']), mimetype='text/plain')
    log.logger.info('Finished refresh')
    return json.dumps(True)


@app.route(__api__('get-magicmirror-config'), methods=[GET])
def get_magicmirror_config():
    path = utils.MAGICMIRROR_CONFIG_FILE
    result = send_file(path, attachment_filename='config.js') if path else ''
    log.logger.info('Retrieving MagicMirror config')
    return result


@app.route(__api__('update-magicmirror-config'), methods=[POST])
def update_magicmirror_config():
    data = request.get_json(force=True)
    log.logger.info('Saving MagicMirror config file')

    try:
        with open(utils.MAGICMIRROR_CONFIG_FILE, 'w') as config:
            config.write(data.get('code'))
    except IOError:
        return json.dumps(False)

    return json.dumps(True)
