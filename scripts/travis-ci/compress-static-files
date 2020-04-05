#!/bin/bash

cd gui/build

VERSION=$(git describe --tags --abbrev=0)

tar czf mmpm-gui-$VERSION.tar.gz static && mv *gz ../..
cd ../../
