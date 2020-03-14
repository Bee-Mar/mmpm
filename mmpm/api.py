#!/usr/bin/env python3
import json
from flask_cors import CORS
from flask import Flask, request, send_file, render_template, send_from_directory, Response
from mmpm import core, utils
from shelljob import proc
from flask_socketio import send, emit

import eventlet
eventlet.monkey_patch()

app = Flask(__name__, root_path='/var/www/mmpm', static_folder="/var/www/mmpm/static")
CORS(app)

GET = 'GET'
POST = 'POST'
PATCH = 'PATCH'
DELETE = 'DELETE'
OPTIONS = 'OPTIONS'


def __api__(path=''):
    return f'/api/{path}'


def __to_json__(val: object):
    return json.dumps(val)


def __modules__(force_refresh=False):
    modules, _, _, _ = core.load_modules(force_refresh=force_refresh)
    return modules


def __stream_cmd_output__(process: proc.Group, namespace: str) -> bool:
    try:
        while process.is_pending():
            for proc, line in process.readlines():
                send(str(line.decode('utf-8')), namespace)
    except Exception:
        return __to_json__(False)
    return __to_json__(True)


def __run__(process: proc.Group, cmd: list):
    process.run(['mmpm'] + cmd)


@app.route('/<path:path>', methods=[GET, OPTIONS])
def static_proxy(path):
    return send_from_directory('./', path)


@app.route('/', methods=[GET, POST, PATCH, DELETE, OPTIONS])
def root():
    return render_template('index.html')


@app.errorhandler(500)
def server_error(error):
    return f'An internal error occurred [{__name__}.py]: {error}', 500


@app.route(__api__('all-modules'), methods=[GET, OPTIONS])
def get_magicmirror_modules():
    return __modules__()


@app.route(__api__('install-modules'), methods=[POST, OPTIONS])
def install_magicmirror_modules():
    selected_modules = request.get_json(force=True)['selected-modules']
    process = proc.Group()
    __run__(process, ['-i'] + [selected_module['title'] for selected_module in selected_modules])
    return __stream_cmd_output__(process, '/install-modules-stream')


@app.route(__api__('uninstall-modules'), methods=[POST, OPTIONS])
def remove_magicmirror_modules():
    selected_modules = request.get_json(force=True)['selected-modules']
    process = proc.Group()
    __run__(process, ['-r'] + [selected_module['title'] for selected_module in selected_modules])
    return __stream_cmd_output__(process, '/uninstall-modules-stream')


@app.route(__api__('update-selected-modules'), methods=[POST, OPTIONS])
def update_magicmirror_modules():
    modules, _, _, _ = core.load_modules()
    core.remove_modules(modules, request.args.get('modules_to_remove'))
    return True


@app.route(__api__('all-installed-modules'), methods=[GET, OPTIONS])
def get_installed_magicmirror_modules():
    return core.get_installed_modules(__modules__())


@app.route(__api__('all-external-module-sources'), methods=[GET, OPTIONS])
def get_external__modules__sources():
    ext_sources = {utils.EXTERNAL_MODULE_SOURCES: []}
    try:
        with open(utils.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
            ext_sources[utils.EXTERNAL_MODULE_SOURCES] = json.load(
                mmpm_ext_srcs)[utils.EXTERNAL_MODULE_SOURCES]
    except IOError:
        pass
    return ext_sources


@app.route(__api__('update-modules'), methods=[GET, OPTIONS])
def update_installed_modules():
    ext_sources = {utils.EXTERNAL_MODULE_SOURCES: []}
    try:
        with open(utils.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
            ext_sources[utils.EXTERNAL_MODULE_SOURCES] = json.load(
                mmpm_ext_srcs)[utils.EXTERNAL_MODULE_SOURCES]
    except IOError:
        pass
    return ext_sources


@app.route(__api__('add-external-module-source'), methods=[POST, OPTIONS])
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


@app.route(__api__('remove-external-module-source'), methods=[DELETE, OPTIONS])
def remove_external_module_source():
    external_sources = request.get_json(force=True)['external-sources']
    titles = [external_source['title'] for external_source in external_sources]

    try:
        success = core.remove_external_module_source(titles)
        return json.dumps(True if not return_code else False)
    except Exception:
        return json.dumps(False)


@app.route(__api__('refresh-modules'), methods=[GET, OPTIONS])
def force_refresh_magicmirror_modules():
    return __modules__(force_refresh=True)


@app.route(__api__('get-magicmirror-config'), methods=[GET, OPTIONS])
def get_magicmirror_config():
    path = utils.MAGICMIRROR_CONFIG_FILE
    result = send_file(path, attachment_filename='config.js') if path else ''
    return result


@app.route(__api__('update-magicmirror-config'), methods=[POST, OPTIONS])
def update_magicmirror_config():
    data = request.get_json(force=True)

    try:
        with open(utils.MAGICMIRROR_CONFIG_FILE, 'w') as config:
            config.write(data.get('code'))
    except IOError:
        return json.dumps(False)

    return json.dumps(True)
