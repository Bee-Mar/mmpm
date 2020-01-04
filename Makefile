PIP=pip3

install:
	sudo rm -f /usr/local/bin/mmpm # cleaning out older versions
	$(PIP) install . --user --force-reinstall
	@printf "\n---------------------------------------------------"
	@printf "\n\nNOTE: Ensure \"$$HOME/.local/bin\" is in your PATH\n"
	@printf "\n---------------------------------------------------\n"

uninstall:
	$(PIP) uninstall mmpm

