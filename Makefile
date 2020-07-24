.NOTPARALLEL:

SHELL=/bin/bash
MAKE_SCRIPTS=scripts/make
GUI=$(MAKE_SCRIPTS)/gui
CLI=$(MAKE_SCRIPTS)/cli
DAEMONS=$(MAKE_SCRIPTS)/daemons

all: warn-install-process-changed

reinstall: warn-install-process-changed

from-src:
	@$(SHELL) $(CLI)/dependencies
	@$(SHELL) $(GUI)/dependencies
	@$(SHELL) $(DAEMONS)/dependencies
	@$(SHELL) $(GUI)/build-from-src
	@$(SHELL) $(GUI)/install-from-src
	@$(SHELL) $(CLI)/build-from-src
	@$(SHELL) $(CLI)/install-from-src
	@$(SHELL) $(DAEMONS)/install-from-src

uninstall-from-src:
	@$(SHELL) $(DAEMONS)/uninstall-from-src
	@$(SHELL) $(GUI)/uninstall-from-src
	@$(SHELL) $(CLI)/uninstall-from-src

warn-install-process-changed:
	@$(SHELL) $(MAKE_SCRIPTS)/warn-install-process-changed

uninstall-from-src: uninstall-cli uninstall-daemons uninstall-gui

