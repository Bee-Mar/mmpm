#!/usr/bin/env bash
python_executable=$([[ $(command -v python3) ]] && echo "python3" || echo "python")

printf "Installing Dev Requirements\n"
$python_executable -m pip install --upgrade -r deps/dev-requirements.txt

printf "\nInstalling Prod Requirements\n"
$python_executable -m pip install -r deps/requirements.txt

