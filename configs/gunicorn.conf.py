#!/usr/bin/env python3
import os
import multiprocessing
import site

_ROOT = os.path.abspath(os.path.join(site.getusersitepackages(), 'mmpm'))
_VAR = os.path.join(_ROOT, 'var')
_ETC = os.path.join(_ROOT, 'etc')

loglevel = 'info'
errorlog = "-"
accesslog = "-"
bind = 'localhost:7891'
workers = multiprocessing.cpu_count()

timeout = 3 * 60  # 3 minutes
keepalive = 24 * 60 * 60  # 1 day

capture_output = True
