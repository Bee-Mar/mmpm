#!/usr/bin/env python3
import multiprocessing
import site

loglevel = 'info'
errorlog = "-"
accesslog = "-"
bind = '0.0.0.0:8008'
workers = multiprocessing.cpu_count() // 2
pythonpath = site.getusersitepackages()

max_requests = 0
timeout = 3 * 60  # 3 minutes
keepalive = 24 * 60 * 60  # 1 day

check_config = True
capture_output = True
sendfile = True
preload = True

