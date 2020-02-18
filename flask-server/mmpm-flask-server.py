#!/usr/bin/env python3
from flask_cors import CORS
from flask import Flask, request
from os.path import expanduser, join
import mmpm.utils
import json

app = Flask(__name__)
CORS(app)

BASE_CMD = ['mmpm']


@app.route('/modules')
def get_magic_mirror_modules():
    try:
        with open(join(expanduser('~'), '.magic_mirror_modules_snapshot.json')) as data:
            module_data = json.load(data)
    except IOError:
        pass

    return module_data


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
    return_code, std_out, std_err = mmpm.utils.run_cmd(BASE_CMD + ['-f'])
    return std_err if return_code else std_out


if __name__ == '__main__':
    app.run('0.0.0.0', 8008)
