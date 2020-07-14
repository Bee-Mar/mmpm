#!/bin/bash

gunicorn --worker-class eventlet --bind 0.0.0.0:7890  mmpm.wsgi:app --reload
