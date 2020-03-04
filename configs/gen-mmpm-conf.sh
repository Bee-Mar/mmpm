#!/bin/bash

ip_address="$(ip -o route get to 8.8.8.8 | sed -n 's/.*src \([0-9.]\+\).*/\1/p')"

sed "s/SUBSTITUTE_ME/$ip_address/g" ./mmpm.conf
