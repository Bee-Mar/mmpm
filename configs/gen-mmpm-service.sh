#!/bin/bash

rm -f ./mmpm.service

printf "[Unit]\n" >> mmpm.service
printf "Description=MMPM Gunicorn daemon server\n" >> mmpm.service
printf "After=network.target\n\n" >> mmpm.service

printf "[Install]\n" >> mmpm.service
printf "WantedBy=multi-user.target\n\n" >> mmpm.service
printf "[Service]\n" >> mmpm.service
printf "Type=notify\n" >> mmpm.service
printf "User=$USER\n" >> mmpm.service
printf "Group=$USER\n" >> mmpm.service
printf "ExecStart=$HOME/.local/bin/gunicorn -c $HOME/.config/mmpm/configs/gunicorn.conf.py  mmpm.wsgi:app -u $USER\n" >> mmpm.service
printf "ExecReload=/bin/kill -s HUP \$MAINPID\n" >> mmpm.service
printf "KillMode=mixed\n" >> mmpm.service
printf "TimeoutStopSec=5\n" >> mmpm.service
printf "PrivateTmp=true\n" >> mmpm.service
