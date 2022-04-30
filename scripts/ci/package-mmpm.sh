#!/usr/bin/env bash

python_executable=$([[ $(command -v python3) ]] && echo "python3" || echo "python")

$python_executable setup.py sdist bdist_wheel
