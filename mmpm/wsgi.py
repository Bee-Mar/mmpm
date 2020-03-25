#!/usr/bin python3
# pylint: disable=unused-import
from mmpm.api import socketio, app

if __name__ == '__main__':
    socketio.run(socketio, debug=True)
