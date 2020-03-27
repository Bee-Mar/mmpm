#!/bin/bash

cd gui/build
tar czfv mmpm-gui.tar.gz static && mv *gz ../..
cd ../../
