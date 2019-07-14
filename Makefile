install:
	chmod +x mmpm.py && sudo cp mmpm.py /usr/local/bin/mmpm

uninstall:
	sudo rm /usr/local/bin/mmpm
	rm ~/.magic_mirror_modules_snapshot.json
