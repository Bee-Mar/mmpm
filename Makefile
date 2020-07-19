.NOTPARALLEL:

SHELL=/bin/bash
MAKE_SCRIPTS=scripts/make
GUI=$(MAKE_SCRIPTS)/gui
CLI=$(MAKE_SCRIPTS)/cli
DAEMONS=$(MAKE_SCRIPTS)/daemons

all: cli gui daemons

cli: dependencies-cli build-cli install-cli

gui: dependencies-gui build-gui install-gui

from-src: cli-from-src gui-from-src daemons

cli-from-src: build-cli-from-src install-cli-from-src

gui-from-src: build-gui-from-src install-gui-from-src

dependencies: dependencies-cli dependencies-gui

dependencies-cli:
	@$(SHELL) $(CLI)/dependencies

dependencies-gui:
	@$(SHELL) $(GUI)/dependencies

build: build-cli build-gui

build-cli:
	@$(SHELL) $(CLI)/build

build-gui:
	@$(SHELL) $(GUI)/build

build-from-src: build-cli-from-src build-gui-from-src

build-cli-from-src:
	@$(SHELL) $(CLI)/build-from-src

build-gui-from-src:
	@$(SHELL) $(GUI)/build-from-src

install: install-cli install-gui

install-cli-from-src:
	@$(SHELL) $(CLI)/install-from-src

install-cli:
	@$(SHELL) $(CLI)/install

install-gui:
	@$(SHELL) $(GUI)/install

install-gui-from-src:
	@$(SHELL) $(GUI)/install-from-src

daemons: install-daemons

install-daemons:
	@$(SHELL) $(DAEMONS)/install

reinstall: uninstall build-cli install-cli build-gui install-gui reinstall-daemons

reinstall-from-src: uninstall cli-from-src gui-from-src reinstall-daemons

reinstall-cli: uninstall-cli build-cli install-cli

reinstall-gui: uninstall-gui build-gui install-gui

reinstall-daemons: uninstall-daemons install-daemons

uninstall: uninstall-cli uninstall-daemons uninstall-gui

uninstall-cli:
	@$(SHELL) $(CLI)/uninstall

uninstall-daemons:
	@$(SHELL) $(DAEMONS)/uninstall

uninstall-gui:
	@$(SHELL) $(GUI)/uninstall
