#!/bin/bash

cd gui
eslint "src/app/*ts"
cd ..

if [ $? = 0 ]; then
  echo "ESLint succeeded"
  exit 0
else
  echo "ESLint failed"
  exit 1
fi

