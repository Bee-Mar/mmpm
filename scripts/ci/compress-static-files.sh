#!/usr/bin/env bash

VERSION=$(git describe --tags --abbrev=0)

cd gui/build
mkdir -p templates
cp static/index.html templates
tar czf mmpm-gui-$VERSION.tar.gz * && mv *gz ../..
cp -r {static,templates} ../../mmpm
cd ../../
