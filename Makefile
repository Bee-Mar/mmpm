install:
	sudo rm -f /usr/local/bin/mmpm
	pip3 install -r requirements.txt --user
	pip3 install --user .
	cd gui/src && npm i
	@printf "\n---------------------------------------------------\n"
	@printf "\n\e[92mNOTE: Ensure \"$$HOME/.local/bin\" is in your PATH\e[0m\n"
	@printf "\n---------------------------------------------------\n"

uninstall:
	pip3 uninstall mmpm

