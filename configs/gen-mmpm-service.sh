#!/bin/bash

rm -f ./*service

printf "[Unit]\n" >> mmpm.service
printf "Description=MMPM Gunicorn daemon\n" >> mmpm.service
printf "After=network.target\n\n" >> mmpm.service

printf "[Install]\n" >> mmpm.service
printf "WantedBy=multi-user.target\n\n" >> mmpm.service
printf "[Service]\n" >> mmpm.service
printf "Type=notify\n" >> mmpm.service
printf "User=$USER\n" >> mmpm.service
printf "Group=$USER\n" >> mmpm.service
printf "ExecStart=$HOME/.local/bin/gunicorn --worker-class eventlet -w 1 -c $HOME/.config/mmpm/configs/gunicorn.conf.py mmpm.wsgi:app -u $USER\n" >> mmpm.service
printf "ExecReload=/bin/kill -s HUP \$MAINPID\n" >> mmpm.service
printf "KillMode=mixed\n" >> mmpm.service
printf "TimeoutStopSec=5\n" >> mmpm.service
printf "PrivateTmp=true\n" >> mmpm.service

printf "[Unit]\n" >> mmpm-webssh.service
printf "Description=MMPM WebSSH daemon\n" >> mmpm-webssh.service
printf "After=syslog.target network.target\n" >> mmpm-webssh.service
printf "StartLimitBurst=5, StartLimitIntervalSec=1\n\n" >> mmpm-webssh.service
printf "[Service]\n" >> ./mmpm-webssh.service
printf "User=$USER\n" >> mmpm-webssh.service
printf "WorkingDirectory=$HOME\n" >> mmpm-webssh.service
printf "ExecStart=$HOME/.local/bin/wssh --address=127.0.0.1 --port=7893\n" >> mmpm-webssh.service
printf "ExecReload=/bin/kill -s HUP \$MAINPID\n" >> mmpm-webssh.service
printf "Type=simple\n" >> mmpm-webssh.service
printf "PIDFile=/var/run/webssh.pid\n" >> mmpm-webssh.service
printf "Restart=on-failure\n" >> mmpm-webssh.service
printf "RestartSec=1\n\n" >> mmpm-webssh.service
printf "[Install]\n" >> mmpm-webssh.service
printf "WantedBy=multi-user.target\n" >> mmpm-webssh.service
