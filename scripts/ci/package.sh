#!/usr/bin/env bash

python_executable=$([[ $(command -v python3) ]] && echo "python3" || echo "python")
mkdir -p mmpm/ui
cp -r ui/build/static mmpm/ui
pdm build
