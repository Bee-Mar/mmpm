#!/bin/bash
pylint mmpm

# pylint exit code is a bit-OR of the following
# 0 if everything went fine
# 1 if a fatal message was issued
# 2 if an error message was issued
# 4 if a warning message was issued
# 8 if a refactor message was issued
# 16 if a convention message was issued
# 32 on usage error

status=$?

if [ $status = 0 ]; then
  echo "Everything looks perfect"
  exit 0
elif [ $(( $status & 3 )) != 0 ]; then
  echo "$status: Errors detected"
  exit $status
else
  echo "$status: Not perfect, but good enough"
  exit 0
fi

