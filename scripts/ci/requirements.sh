#!/usr/bin/env bash
printf "Installing Dev Requirements\n"
pip install --upgrade -r deps/dev-requirements.txt
printf "\nInstalling Prod Requirements\n"
pip install -r deps/requirements.txt

