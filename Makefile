.NOTPARALLEL:

SHELL=/bin/bash
SCRIPTS=scripts/make

all: clean cli gui daemons

cli: dependencies-cli build-cli install-cli

gui: dependencies-gui build-gui install-gui

from-src: clean cli-from-src gui-from-src daemons

cli-from-src: build-cli-from-src install-cli-from-src

gui-from-src: build-gui-from-src install-gui-from-src

clean:
	@$(SHELL) $(SCRIPTS)/clean/all

dependencies: dependencies-cli dependencies-gui

dependencies-cli:
	@$(SHELL) $(SCRIPTS)/cli/dependencies

dependencies-gui:
	@$(SHELL) $(SCRIPTS)/gui/dependencies

build: build-cli build-gui

build-cli:

build-gui:
	@$(SHELL) $(SCRIPTS)/gui/build

build-from-src: build-cli-from-src build-gui-from-src

build-cli-from-src:

build-gui-from-src:
	@$(SHELL) $(SCRIPTS)/gui/build-from-src

install: install-cli install-gui

install-cli-from-src: install-cli

install-cli:
	@$(SHELL) $(SCRIPTS)/cli/install

install-gui:
	@$(SHELL) $(SCRIPTS)/gui/install

daemons: install-daemons

install-daemons:
	@$(SHELL) $(SCRIPTS)/daemons/install

install-gui-from-src:
	@$(SHELL) $(SCRIPTS)/gui/install-from-src

reinstall: uninstall build-cli install-cli build-gui install-gui reinstall-daemons

reinstall-from-src: uninstall cli-from-src gui-from-src reinstall-daemons

reinstall-cli: uninstall-cli build-cli install-cli

reinstall-gui: uninstall-gui build-gui install-gui

reinstall-daemons: uninstall-daemons install-daemons

uninstall: uninstall-cli uninstall-daemons uninstall-gui

uninstall-cli:
	@$(SHELL) $(SCRIPTS)/cli/uninstall

uninstall-daemons:
	@$(SHELL) $(SCRIPTS)/daemons/uninstall

uninstall-gui:
	@$(SHELL) $(SCRIPTS)/gui/uninstall
