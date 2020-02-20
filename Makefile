# GREEN = "\e[92m"
# CYAN = "\e[46m"
# RESET = "\e[0m"

all: clean dependencies build install

clean:
	@printf -- "-----------------------------------------"
	@printf "\n| \e[92mRemoving old installation destination\e[0m |"
	@printf "\n-----------------------------------------\n"
	sudo rm -f /usr/local/bin/mmpm

dependencies: dependencies-web dependencies-cli

dependencies-cli:
	@printf -- "----------------------------------"
	@printf "\n| \e[92mGathering Python3 dependencies\e[0m |"
	@printf "\n----------------------------------\n"
	@pip3 install -r requirements.txt --user

dependencies-web:
	@printf -- "----------------------------------"
	@printf "\n| \e[92mGathering Angular dependencies\e[0m |"
	@printf "\n----------------------------------\n"
	@sudo apt install nginx -y
	@sudo service nginx start
	@npm install -g @angular/cli
	@npm install --prefix gui

build: build-web build-cli

build-web:
	@printf -- "---------------------"
	@printf "\n| \e[92mBuilding MMPM GUI\e[0m |"
	@printf "\n---------------------\n"
	@cd gui && ng build --prod

build-cli:
	# nothing yet for this, but keeping for consistency sake

install: install-web install-cli

install-web:
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

install-cli:
	@printf -- "------------------------"
	@printf "\n| \e[92mInstalling MMPM CLI \e[0m |"
	@printf "\n------------------------\n"
	@pip3 install --user .
	@printf -- "-------------------------------------------------------\n"
	@printf "\n| \e[92mNOTE: Ensure \"${HOME}/.local/bin\" is in your PATH\e[0m |"
	@printf "\n-------------------------------------------------------\n"
	@printf "\n\033[1;36mMMPM Successfully Installed \e[0m\n"
	@printf "\nThe MMPM GUI is being served the IP address of your default interface at port 8081"
	@printf "\nBest guess: http://$$(ip -o route get to 8.8.8.8 | sed -n 's/.*src \([0-9.]\+\).*/\1/p'):8081\n\n"

uninstall:
	@printf -- "---------------------------------"
	@printf "\n| \e[92mRemoving MMPM CLI and GUI \e[0m |"
	@printf "\n---------------------------------\n"
	@pip3 uninstall mmpm -y
	sudo rm -rf /var/www/mmpm /etc/nginx/sites-enabled/mmpm-gui /etc/nginx/sites-available/mmpm-gui

