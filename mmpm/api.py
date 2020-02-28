#!/usr/bin/env python3
from flask_cors import CORS
from flask import Flask, request, send_file, send_from_directory
from mmpm import core, utils
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# BASE_CMD = ['mmpm']


def __json__(val):
    return json.dumps(val)


def __modules__():
    modules, _, _, _ = core.load_modules()
    return modules


@app.route('/all-modules', methods=['GET'])
def get_magicmirror_modules():
    return __json__(__modules__())


@app.route('/install-module', methods=['POST'])
def install_magicmirror_modules():
    core.install_modules(__modules__(), request.args.get('modules_to_install'))
    return True


@app.route('/uninstall-module', methods=['POST'])
def remove_magicmirror_modules():
    modules, _, _, _ = core.load_modules()
    core.remove_modules(__modules__, request.args.get('modules_to_remove'))
    return True


@app.route('/installed-modules', methods=['GET'])
def get_installed_magicmirror_modules():
    return __json__(core.get_installed_modules(__modules__()))


@app.route('/external-module-sources', methods=['GET'])
def get_external_modules_sources():
    modules = __modules__()
    ext_sources = modules[utils.EXTERNAL_MODULE_SOURCES] if utils.EXTERNAL_MODULE_SOURCES in modules.keys() else []
    return __json__({ utils.EXTERNAL_MODULE_SOURCES: ext_sources })


@app.route('/register-external-module-source', methods=['POST'])
def add_external_module_source():
    core.add_external_module_source(
        request.args.get('title'),
        request.args.get('author'),
        request.args.get('desc'),
        request.args.get('repo')
    )


@app.route('/refresh-modules', methods=['GET'])
def force_refresh_magicmirror_modules():
    return __json__(__modules__())


@app.route('/get-magicmirror-config', methods=['GET'])
def get_magicmirror_config():
    path = utils.get_magicmirror_config_file_path()
    config = ''

    if not path:
        return __json__(None)

    result = send_file(path, attachment_filename='config.js')
    return result


@app.route('/update-magicmirror-config', methods=['GET'])
def update_magicmirror_config():
    return __json__(__modules__())
