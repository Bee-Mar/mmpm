#!/usr/bin/env python3
"""
An incredibly simplistic SocketIO server used for repeating logs from the MMPM CLI to the UI.
"""
import eventlet
import socketio

sio = socketio.Server(cors_allowed_origins="*")


@sio.event
def connect(sid, environ):
    print("Client connected:", sid)


@sio.event
def logs(sid, data):
    sio.emit("logs", data, skip_sid=sid)


@sio.event
def disconnect(sid):
    print("Client disconnected:", sid)


app = socketio.WSGIApp(sio)

if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("", 6789)), app)
