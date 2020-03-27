#!/bin/bash

wget https://github.com/Bee-Mar/mmpm/releases/download/$(git describe --tags --abbrev=0)/mmpm-gui.tar.gz

sudo rm -rf /var/www/mmpm/static
sudo mkdir -p /var/www/mmpm/{static,templates}
sudo tar xvf mmpm-gui.tar.gz -C /var/www/mmpm
sudo cp /var/www/mmpm/static/index.html /var/www/mmpm/templates/

rm mmpm-gui.tar.gz
