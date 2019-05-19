install: -build_depends -place_in_path

-build_depends:
	pip3 install --user bs4 pygit2 colorama

-place_in_path: mmpm.py
	sudo cp mmpm.py /usr/local/bin/mmpm
	sudo chmod +x /usr/local/bin/mmpm

uninstall:
	sudo rm /usr/local/bin/mmpm
	rm ~/.magic_mirror_modules_snapshot.json
