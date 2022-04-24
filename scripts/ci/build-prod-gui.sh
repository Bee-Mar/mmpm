#!/usr/bin/env bash

cd gui
./node_modules/@angular/cli/bin/ng build --prod --deploy-url static/
cd ..
