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


@app.route('/<path:path>', methods=['GET', 'OPTIONS'])
def static_proxy(path):
    return send_from_directory('./', path)


@app.route('/', methods=['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'])
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


@app.route(__api__('get-external-module-sources'), methods=['GET', 'OPTIONS'])
def get_external_modules_sources():
    ext_sources = {utils.EXTERNAL_MODULE_SOURCES: []}
    try:
        with open(utils.MMPM_EXTERNAL_SOURCES_FILE, 'r') as mmpm_ext_srcs:
            ext_sources[utils.EXTERNAL_MODULE_SOURCES] = json.load(mmpm_ext_srcs)[utils.EXTERNAL_MODULE_SOURCES]
    except IOError:
        pass
    return ext_sources


@app.route(__api__('register-external-module-source'), methods=['POST', 'OPTIONS'])
def add_external_module_source():
    external_source = request.get_json(force=True)['external-source']
    try:
         core.add_external_module_source(
             title=external_source.get('title'),
             author=external_source.get('author'),
             desc=external_source.get('description'),
             repo=external_source.get('repository')
         )
         return json.dumps(True)
    except Exception:
        return json.dumps(False)


@app.route(__api__('refresh-modules'), methods=['GET', 'OPTIONS'])
def force_refresh_magicmirror_modules():
    return __modules__(force_refresh=True)


@app.route(__api__('get-magicmirror-config'), methods=['GET', 'OPTIONS'])
def get_magicmirror_config():
    path = utils.MAGICMIRROR_CONFIG_FILE
    result = send_file(path, attachment_filename='config.js') if path else ''
    return result

@app.route(__api__('update-magicmirror-config'), methods=['POST', 'OPTIONS'])
def update_magicmirror_config():
    data = request.get_json(force=True)

    try:
        with open(utils.MAGICMIRROR_CONFIG_FILE, 'w') as f:
            f.write(data.get('code'))
    except IOError:
        return json.dumps(False)

    return json.dumps(True)
