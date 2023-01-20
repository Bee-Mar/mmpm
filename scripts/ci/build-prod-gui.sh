#!/usr/bin/env bash

cd gui
./node_modules/@angular/cli/bin/ng.js build --configuration production --base-href /
cd ..
