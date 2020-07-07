#!/usr/bin python3
# pylint: disable=unused-import
from mmpm.api import flask_sio, app

if __name__ == '__main__':
    flask_sio.run(flask_sio, threaded=True)
