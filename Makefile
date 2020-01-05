install:
	sudo rm -f /usr/local/bin/mmpm
	pip3 install -r requirements.txt --user
	pip3 install --user .
	@printf "\n---------------------------------------------------"
	@printf "\n\nNOTE: Ensure \"$$HOME/.local/bin\" is in your PATH\n"
	@printf "\n---------------------------------------------------\n"

uninstall:
	pip3 uninstall mmpm

