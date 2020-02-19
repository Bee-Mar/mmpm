#!/usr/bin/env python3
from flask_cors import CORS
from flask import Flask, request
from os.path import expanduser, join
import mmpm.utils
import mmpm.core
import json

app = Flask(__name__)
CORS(app)

BASE_CMD = ['mmpm']


@app.route('/modules')
def get_magic_mirror_modules():
    try:
        modules, _, _, _ = mmpm.core.load_modules(mmpm.utils.SNAPSHOT_FILE)
    except Exception:
        pass
    return modules


@app.route('/install')
def install_magic_mirror_modules():
    return_code, std_out, std_err = mmpm.utils.run_cmd(BASE_CMD + ['-i'])
    return std_err if return_code else std_out


@app.route('/remove')
def remove_magic_mirror_modules():
    return_code, std_out, std_err = mmpm.utils.run_cmd(BASE_CMD + ['-r'])
    return std_err if return_code else std_out


@app.route('/installed')
def get_installed_magic_mirror_modules():
    return_code, std_out, std_err = mmpm.utils.run_cmd(BASE_CMD + ['-l'])
    return std_err if return_code else std_out


@app.route('/refresh', methods=['GET'])
def force_refresh_magic_mirror_modules():
    try:
        modules, _, _, _ = mmpm.core.load_modules(mmpm.utils.SNAPSHOT_FILE, force_refresh=True)
    except Exception:
        pass
    return modules


if __name__ == '__main__':
    app.run('0.0.0.0', 8008)
