#!/bin/bash

CONFIGS_DIR="configs"

rm -f $CONFIGS_DIR/*service

printf "[Unit]\n" >> $CONFIGS_DIR/mmpm.service
printf "Description=MMPM Gunicorn daemon\n" >> $CONFIGS_DIR/mmpm.service
printf "After=network.target\n\n" >> $CONFIGS_DIR/mmpm.service

printf "[Install]\n" >> $CONFIGS_DIR/mmpm.service
printf "WantedBy=multi-user.target\n\n" >> $CONFIGS_DIR/mmpm.service
printf "[Service]\n" >> $CONFIGS_DIR/mmpm.service
printf "Type=notify\n" >> $CONFIGS_DIR/mmpm.service
printf "User=$USER\n" >> $CONFIGS_DIR/mmpm.service
printf "Group=$USER\n" >> $CONFIGS_DIR/mmpm.service
printf "ExecStart=$HOME/.local/bin/gunicorn --worker-class eventlet -w 1 -c $HOME/.config/mmpm/configs/gunicorn.conf.py mmpm.wsgi:app -u $USER\n" >> $CONFIGS_DIR/mmpm.service
printf "ExecReload=/bin/kill -s HUP \$MAINPID\n" >> $CONFIGS_DIR/mmpm.service
printf "KillMode=mixed\n" >> $CONFIGS_DIR/mmpm.service
printf "TimeoutStopSec=5\n" >> $CONFIGS_DIR/mmpm.service
printf "PrivateTmp=true\n" >> $CONFIGS_DIR/mmpm.service

printf "[Unit]\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "Description=MMPM WebSSH daemon\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "After=syslog.target network.target\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "StartLimitBurst=5, StartLimitIntervalSec=1\n\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "[Service]\n" >> ./$CONFIGS_DIR/mmpm-webssh.service
printf "User=$USER\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "WorkingDirectory=$HOME\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "ExecStart=$HOME/.local/bin/wssh --address=127.0.0.1 --port=7893\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "ExecReload=/bin/kill -s HUP \$MAINPID\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "Type=simple\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "PIDFile=/var/run/webssh.pid\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "Restart=on-failure\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "RestartSec=1\n\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "[Install]\n" >> $CONFIGS_DIR/mmpm-webssh.service
printf "WantedBy=multi-user.target\n" >> $CONFIGS_DIR/mmpm-webssh.service
