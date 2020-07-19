#!/usr/bin/env python3
import os
import multiprocessing
import site

loglevel = 'info'
accesslog = os.path.join(os.getenv('HOME'),'.config/mmpm/log/mmpm-gunicorn-access.log')
errorlog = os.path.join(os.getenv('HOME'), '.config/mmpm/log/mmpm-gunicorn-error.log')
bind = 'localhost:7891'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'eventlet'

timeout = 3 * 60  # 3 minutes
keepalive = 24 * 60 * 60  # 1 day

capture_output = True
