#!/bin/bash

gunicorn --worker-class gevent --bind 0.0.0.0:7890  mmpm.wsgi:app --reload
