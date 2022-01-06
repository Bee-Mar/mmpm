#!/bin/bash
pylint mmpm

return_code=$?

[[ $return_code = 0 ]] && echo "PyLint test succeeded" && exit 0
[[ $(( $return_code & 3 )) != 0 ]] && echo "$return_code: Errors detected" && exit $return_code

echo "$return_code: Not perfect, but good enough"
exit 0

