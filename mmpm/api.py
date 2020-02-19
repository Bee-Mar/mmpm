#!/usr/bin/env python3
from flask_cors import CORS
from flask import Flask, request
from . import core, utils

app = Flask(__name__)
CORS(app)

BASE_CMD = ['mmpm']
MODULES, _, _, _ = core.load_modules(utils.SNAPSHOT_FILE)


@app.route('/modules', methods=['GET'])
def get_magic_mirror_modules():
    return MODULES


@app.route('/install', methods=['POST'])
def install_magic_mirror_modules():
    return_code, std_out, std_err = utils.run_cmd(BASE_CMD + ['-i'])
    return std_err if return_code else std_out


@app.route('/remove', methods=['POST'])
def remove_magic_mirror_modules():
    return_code, std_out, std_err = utils.run_cmd(BASE_CMD + ['-r'])
    return std_err if return_code else std_out


@app.route('/installed', methods=['GET'])
def get_installed_magic_mirror_modules():
    return_code, std_out, std_err = utils.run_cmd(BASE_CMD + ['-l'])
    return std_err if return_code else std_out


@app.route('/add-external-module-source', methods=['POST'])
def add_external_module_source():
    core.add_external_module_source(
        request.args.get('title'),
        request.args.get('author'),
        request.args.get('desc'),
        request.args.get('repo')
    )


@app.route('/refresh', methods=['GET'])
def force_refresh_magic_mirror_modules():
    try:
        MODULES, _, _, _ = core.load_modules(utils.SNAPSHOT_FILE, force_refresh=True)
    except Exception:
        pass
    return MODULES
