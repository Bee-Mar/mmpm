#!/usr/bin/env python3
from flask_cors import CORS
from flask import Flask, request
from mmpm import core, utils
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# BASE_CMD = ['mmpm']

def __modules__():
    modules, _, _, _ = core.load_modules()
    return modules

@app.route('/all-modules', methods=['GET'])
def get_magic_mirror_modules():
    return __modules__()


@app.route('/install-module', methods=['POST'])
def install_magic_mirror_modules():
    core.install_modules(__modules__(), request.args.get('modules_to_install'))
    return True


@app.route('/uninstall-module', methods=['POST'])
def remove_magic_mirror_modules():
    modules, _, _, _ = core.load_modules()
    core.remove_modules(__modules__, request.args.get('modules_to_remove'))
    return True


@app.route('/installed-modules', methods=['GET'])
def get_installed_magic_mirror_modules():
    return core.get_installed_modules(__modules__())


@app.route('/external-module-sources', methods=['GET'])
def get_external_modules_sources():
    modules = __modules__()
    return modules[utils.EXTERNAL_MODULE_SOURCES] if utils.EXTERNAL_MODULE_SOURCES in modules.keys() else {utils.EXTERNAL_MODULE_SOURCES: []}


@app.route('/register-external-module-source', methods=['POST'])
def add_external_module_source():
    core.add_external_module_source(
        request.args.get('title'),
        request.args.get('author'),
        request.args.get('desc'),
        request.args.get('repo')
    )


@app.route('/refresh-modules', methods=['GET'])
def force_refresh_magic_mirror_modules():
    return __modules__()
