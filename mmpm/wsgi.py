#!/usr/bin python3
from mmpm.api import app
from flask_cors import CORS

if __name__ == '__main__':
    CORS(app)
    app.run()
