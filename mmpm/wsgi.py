#!/usr/bin python3
from mmpm.api import socketio, app

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=7891)
