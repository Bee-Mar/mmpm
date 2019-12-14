install:
	sudo rm -f /usr/local/bin/mmpm
	pip install . --user
	@printf "\n---------------------------------------------------"
	@printf "\n\nNOTE: Ensure \"$$HOME/.local/bin\" is in your PATH\n"
	@printf "\n---------------------------------------------------\n"

uninstall:
	pip uninstall mmpm

