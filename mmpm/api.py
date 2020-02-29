#!/usr/bin/env python3
from flask_cors import CORS
from flask import Flask, request, send_file, render_template, send_from_directory
from mmpm import core, utils
import json

app = Flask(__name__, root_path='/var/www/mmpm', static_folder="/var/www/mmpm/static")
CORS(app)


def __api__(path=''):
    return f'/api/{path}'


def __json__(val):
    return json.dumps(val)


def __modules__(force_refresh=False):
    modules, _, _, _ = core.load_modules(force_refresh=force_refresh)
    return modules


@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
    return send_from_directory('./', path)


@app.route('/')
def root():
    return render_template('index.html')


@app.errorhandler(500)
def server_error(error):
    return f'An internal error occurred [{__name__}.py]: {error}', 500


@app.route(__api__('all-modules'), methods=['GET', 'OPTIONS'])
def get_magicmirror_modules():
    return __modules__()


@app.route(__api__('install-modules'), methods=['POST', 'OPTIONS'])
def install_magicmirror_modules():
    core.install_modules(__modules__(), request.args.get('modules_to_install'))
    return True


@app.route(__api__('uninstall-module'), methods=['POST', 'OPTIONS'])
def remove_magicmirror_modules():
    modules, _, _, _ = core.load_modules()
    core.remove_modules(modules, request.args.get('modules_to_remove'))
    return True


@app.route(__api__('installed-modules'), methods=['GET', 'OPTIONS'])
def get_installed_magicmirror_modules():
    return core.get_installed_modules(__modules__())


@app.route(__api__('external-module-sources'), methods=['GET', 'OPTIONS'])
def get_external_modules_sources():
    modules = __modules__()
    ext_sources = modules[utils.EXTERNAL_MODULE_SOURCES] if utils.EXTERNAL_MODULE_SOURCES in modules.keys() else []
    return {utils.EXTERNAL_MODULE_SOURCES: ext_sources}


@app.route(__api__('register-external-module-source'), methods=['POST', 'OPTIONS'])
def add_external_module_source():
    core.add_external_module_source(
        request.args.get('title'),
        request.args.get('author'),
        request.args.get('desc'),
        request.args.get('repo')
    )


@app.route(__api__('refresh-modules'), methods=['GET', 'OPTIONS'])
def force_refresh_magicmirror_modules():
    return __modules__(force_refresh=True)


@app.route(__api__('get-magicmirror-config'), methods=['GET', 'OPTIONS'])
def get_magicmirror_config():
    path = utils.get_magicmirror_config_file_path()
    result = send_file(path, attachment_filename='config.js') if path else ''
    return result


@app.route(__api__('/update-magicmirror-config'), methods=['GET', 'OPTIONS'])
def update_magicmirror_config():
    return __modules__()
