.NOTPARALLEL:

all: clean cli gui

clean:
	@printf -- "---------------------------------------------"
	@printf "\n| \e[92mRemoving legacy installation destination\e[0m |"
	@printf "\n---------------------------------------------\n"
	sudo rm -f /usr/local/bin/mmpm

gui: dependencies-gui build-gui install-gui

cli: dependencies-cli build-cli install-cli

dependencies: dependencies-gui

dependencies-cli:
	@printf -- "------------------------------"
	@printf "\n| \e[92mGathering CLI dependencies\e[0m |"
	@printf "\n------------------------------\n"
	@sudo apt install python3-pip
	@pip3 install --user setuptools wheel --upgrade
	@pip3 install --user -r requirements.txt

dependencies-gui:
	@printf -- "------------------------------"
	@printf "\n| \e[92mGathering GUI dependencies\e[0m |"
	@printf "\n------------------------------\n"
	@sudo apt install nginx-full curl -y
	@curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
	@sudo apt install nodejs -y
	@sudo systemctl start nginx
	@npm config set prefix ~/.local
	@npm install -g @angular/cli
	@npm install --prefix gui

build: build-cli build-gui

build-cli:

build-gui:
	@printf -- "---------------------"
	@printf "\n| \e[92mBuilding MMPM GUI\e[0m |"
	@printf "\n---------------------\n"
	@cd gui && ~/.local/bin/ng build --prod --deploy-url static/

install: install-cli install-gui

install-cli:
	@printf -- "------------------------"
	@printf "\n| \e[92mInstalling MMPM CLI \e[0m |"
	@printf "\n------------------------\n"
	@mkdir -p ${HOME}/.config/mmpm/log ${HOME}/.config/mmpm/configs
	@pip3 install --user .
	@printf -- "-------------------------------------------------------"
	@printf "\n| \e[92mNOTE: Ensure \"${HOME}/.local/bin\" is in your PATH\e[0m |"
	@printf "\n-------------------------------------------------------\n"
	@[ ! $? ] && printf "\n\033[1;36mMMPM GUI Installed \e[0m\n"

install-gui:
	@printf -- "------------------------"
	@printf "\n| \e[92mInstalling MMPM GUI \e[0m |"
	@printf "\n------------------------\n"
	@mkdir -p ${HOME}/.config/mmpm/log ${HOME}/.config/mmpm/configs
	@cd configs && \
		bash gen-mmpm-service.sh && \
		sudo cp mmpm.service /etc/systemd/system/ && \
		sudo cp mmpm-webssh.service /etc/systemd/system/
	@cp configs/gunicorn.conf.py ${HOME}/.config/mmpm/configs
	@cp configs/*conf ${HOME}/.config/mmpm/configs
	@cp configs/*service ${HOME}/.config/mmpm/configs
	@touch ${HOME}/.config/mmpm/log/mmpm-gunicorn-error.log ${HOME}/.config/mmpm/log/mmpm-gunicorn-access.log
	@sudo systemctl enable mmpm
	@sudo systemctl start mmpm
	@sudo systemctl enable mmpm-webssh
	@sudo systemctl start mmpm-webssh
	@sudo systemctl status mmpm --no-pager
	@sudo systemctl status mmpm-webssh --no-pager
	@sudo cp configs/mmpm.conf /etc/nginx/sites-available && \
		sudo ln -s /etc/nginx/sites-available/mmpm.conf /etc/nginx/sites-enabled
	@sudo systemctl restart nginx.service --no-pager
	@sudo mkdir -p /var/www/mmpm/templates && \
		sudo cp -r gui/build/static /var/www/mmpm && \
		sudo cp /var/www/mmpm/static/index.html /var/www/mmpm/templates
	@cp ./configs/gunicorn.conf.py ~/.config/mmpm/configs
	@[ ! $? ] && printf "\n\033[1;36mMMPM GUI Installed \e[0m\n"
	@[ ! $? ] && printf "\nThe MMPM GUI is being served the IP address of your default interface at port 7890"
	@[ ! $? ] && printf "\nBest guess: http://$$(ip -o route get to 8.8.8.8 | sed -n 's/.*src \([0-9.]\+\).*/\1/p'):7890\n\n"

reinstall: uninstall cli gui

reinstall-cli: uninstall-cli build-cli install-cli

reinstall-gui: uninstall-gui build-gui install-gui

uninstall: uninstall-cli uninstall-gui

uninstall-cli:
	@printf -- "----------------------"
	@printf "\n| \e[92mRemoving MMPM CLI \e[0m |"
	@printf "\n----------------------\n"
	@pip3 uninstall mmpm -y
	@[ ! $? ] && printf "\n\033[1;36mMMPM CLI Removed\e[0m\n"

uninstall-gui:
	@printf -- "----------------------"
	@printf "\n| \e[92mRemoving MMPM GUI \e[0m |"
	@printf "\n----------------------\n"
	-rm -f ${HOME}/.config/mmpm/configs/gunicorn.conf.py
	-sudo systemctl stop mmpm.service
	-sudo systemctl disable mmpm.service
	-sudo systemctl stop mmpm-webssh.service
	-sudo systemctl disable mmpm-webssh.service
	-sudo rm -f /etc/systemd/system/mmpm* /var/log/mmpm*.log
	-sudo systemctl daemon-reload
	-sudo systemctl reset-failed
	-sudo rm -rf /var/www/mmpm
	-sudo rm -f /etc/nginx/sites-available/mmpm.conf
	-sudo rm -f /etc/nginx/sites-enabled/mmpm.conf
	-sudo systemctl restart nginx
	@[ ! $? ] && printf "\n\033[1;36mMMPM GUI Removed\e[0m\n"
