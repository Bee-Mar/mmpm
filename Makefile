all: clean dependencies build install

clean:
	@printf -- "-----------------------------------------"
	@printf "\n| \e[92mRemoving old installation destination\e[0m |"
	@printf "\n-----------------------------------------\n"
	sudo rm -f /usr/local/bin/mmpm

dependencies: dependencies-cli dependencies-gui

dependencies-gui:
	@printf -- "------------------------------"
	@printf "\n| \e[92mGathering GUI dependencies\e[0m |"
	@printf "\n------------------------------\n"
	@sudo apt install nginx -y
	@sudo service nginx start
	@npm install -g @angular/cli
	@npm install --prefix gui

dependencies-cli:
	@printf -- "------------------------------"
	@printf "\n| \e[92mGathering CLI dependencies\e[0m |"
	@printf "\n------------------------------\n"
	@pip3 install -r requirements.txt --user

build: build-cli build-gui

build-cli:
	# nothing yet for this, but keeping for consistency sake

build-gui:
	@printf -- "---------------------"
	@printf "\n| \e[92mBuilding MMPM GUI\e[0m |"
	@printf "\n---------------------\n"
	@cd gui && ng build --prod

install: install-cli install-gui

install-cli:
	@printf -- "------------------------"
	@printf "\n| \e[92mInstalling MMPM CLI \e[0m |"
	@printf "\n------------------------\n"
	@pip3 install --user .
	@printf -- "-------------------------------------------------------\n"
	@printf "\n| \e[92mNOTE: Ensure \"${HOME}/.local/bin\" is in your PATH\e[0m |"
	@printf "\n-------------------------------------------------------\n"
	@[ ! $? ] && printf "\n\033[1;36mMMPM Successfully Installed \e[0m\n"
	@[ ! $? ] && printf "\nThe MMPM GUI is being served the IP address of your default interface at port 8081"
	@[ ! $? ] && printf "\nBest guess: http://$$(ip -o route get to 8.8.8.8 | sed -n 's/.*src \([0-9.]\+\).*/\1/p'):8081\n\n"

install-gui:
	@printf -- "------------------------"
	@printf "\n| \e[92mInstalling MMPM GUI \e[0m |"
	@printf "\n------------------------\n"
	@mkdir -p ${HOME}/.config/mmpm/configs
	@cp mmpm/gunicorn.conf.py ${HOME}/.config/mmpm/configs
	@cd configs && \
		bash gen-mmpm-service.sh && \
		sudo cp mmpm.service /etc/systemd/system/
	@sudo systemctl enable mmpm && \
		sudo systemctl start mmpm && \
		sudo systemctl status --no-pager mmpm
	@sudo cp configs/mmpm-gui /etc/nginx/sites-available && \
		sudo ln -sf /etc/nginx/sites-available/mmpm-gui /etc/nginx/sites-enabled && \
		sudo mkdir -p /var/www/mmpm && \
		sudo cp -r gui/dist/gui /var/www/mmpm

uninstall: uninstall-cli uninstall-gui
	@[ ! $? ] && printf "\n\033[1;36mSuccessfully Removed MMPM \e[0m\n"

uninstall-cli:
	@printf -- "----------------------"
	@printf "\n| \e[92mRemoving MMPM CLI \e[0m |"
	@printf "\n----------------------\n"
	@pip3 uninstall mmpm -y

uninstall-gui:
	@printf -- "----------------------"
	@printf "\n| \e[92mRemoving MMPM GUI \e[0m |"
	@printf "\n----------------------\n"
	sudo systemctl stop mmpm && \
		sudo systemctl disable mmpm && \
		sudo rm /etc/systemd/system/mmpm.service && \
		sudo systemctl daemon-reload && \
		sudo systemctl reset-failed
	sudo rm -rf /var/www/mmpm \
		/etc/nginx/sites-enabled/mmpm-gui \
		/etc/nginx/sites-available/mmpm-gui

