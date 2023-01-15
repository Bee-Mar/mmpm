# MMPM Changelog

## Version 0.1

- Initial creation of MMPM package manager

## Version 0.2

- Some code cleanup

- renamed some function calls to be more idiomatic

- Added doc-strings to functions

- Added new method `check_for_mmpm_enhancements` to check for updates to MMPM, which will run
    intermittently, and prompt the user when one is found

- The user may also run `check_for_mmpm_enhancements` by specifying the `-e` flag

- Removed onus of installing required Python modules on user during `make install` process by
  including `try` and `except` blocks in `mmpm.py`. Primary reason for this was based on odd
  segmentation faults when attempting to handle original `make install` from within
  `check_for_mmpm_enhancements`. This will be cleaned up later on, but since it seems to work, no
  reason to go overboard just yet.

- Still a lot more code cleanup can be done...like A LOT more.

- Planning to break up MMPM into a module, and add functionality which will include scraping of the
  module pages to find any configs that can be placed into the main config, `config.js`
  automatically for the user. This should be pretty doable considering it's just a JSON file, and it
  call be indexed into

- Next version will focus on more code cleanup, and presentation of module names. Rather than
  displaying everything in a large list, they will be shown in a table, that is more compact and
  readable.

## Version 0.25

- Updated `display_modules` to display the output as a formatted table

- Version 0.3 will focus on performance improvements, and code cleanup

## Version 0.26

- Removed `pygit2` from dependencies, and replaced with `os.system` call

## Version 0.261

- Minor change in font color when installing packages

## Version 0.265

- Fixed small bug where checking for updates could happen twice if the snapshot file needed to be
  updated. The enhancement command now will only run once at most in either case.

## Version 0.266

- Accidentally created issue with `npm install` by placing text color in front of `os.system`
  command

- Also, removed unused variables

## Version 0.267

- Tidying up some output messages, nothing important

## Version 0.268

- I'm done tidying up today

## Version 0.269

- forgot to remove debug statement

## Version 0.270

- cleanup

## Version 0.275

- Added new method `install_magicmirror` to handle installation/upgrades of MagicMirror itself
- Can be called with `mmpm -M` or `mmpm --magicmirror`

## Version 0.3

- Resolved major performance issue with `import pip`. Changed logic to only import when needed to
  install packages
- Reduced execution time by a lot, but there is still some issues that can be fixed to speed up more
- Still in need of more code cleanup

## Version 0.31

- Changed error handling and added user help for installing missing modules
- Planning to convert to module with setup.py file for easier installation

## Version 0.32

- Moved to setup.py format. Initial setup works, will add in system requirements later

## Version 0.33

- Adding in the makefile again because I didn't think long term about this and probably locked
  myself into the format of installing with a makefile...

## Version 0.34

- Small fix made to urllib import as well as fixed breaking bug in description collection

## Version 0.35

- Bug fixes to installatio

## Version 0.36

- Issue with checking for version number

## Version 0.37

- Added env variable to allow for non-traditional installation location of MagicMirror

## Version 0.38

- Bug with upgrading module

## Version 0.39

- Readme update and bug fix

## Version 0.50

- Added ability for user to configure external sources for modules
- Bug fixes
- Code cleanup

## Version 0.98

- Major code cleanup (added typing hinting, and docstrings)
- Added web interface, and daemons to run on system restart that will be accessible from any device in
  the users home network which allows user to perform maintenance on their MagicMirror packages
- Added better terminal output during installation process
- Added mypy and pylint configs
- Added logging for CLI

## Version 0.981

- Wrong wiki url

## Version 0.99

- integrated Travis-CI builds
- quickened installation process by retrieving artifacts from tagged builds
- Modified Makefile to reflect the changes

## Version 0.992

- Upping the tag number

## Version 0.998

- added tab for user to control Restart, Start, and Stop the MagicMirror, as well as Reboot and
  Power-off the RaspberryPi

## Version 0.999

- Merging into master

## Version 1.0

- Travis CI doesn't read 4 decimals on tag precision

## Version 1.05

- Prettified stdout messaging, and added upgrade option for MMPM from GUI

## Version 1.08

- Added installation rules for Arch Linux, and broke apart Makefile

## Version 1.09

- Updated url for MagicMirror installer script, (contributor: herostrat)
- Fixed installation by placing version lock on `shelljob` module (contributor: herostrat)

## Version 1.10

- Bug fix. Changed method of loading requirements from requirements.txt within setup.py

## Version 1.11

- Bug fix. Added module name santizing, fixing installation issues with module names with slashes (contributor: herostrat)
- Bug fix. Confusing messaging when multiple modules are installed, making it unclear which modules
  failed to install properly

## Version 1.12

- Bug fix (#23). Added `electron` to the list of processes to kill when stopping MagicMirror, and
  updated util functions to use pm2 for MagicMirror controls

## Version 1.13

- Enhancment (#26). Added command line option to display the MMPM web interface URL
- Enhancment (#27). Added command line option to display the currently enabled modules
- Bug fix (#29). Corrected log.info to log.logger.info in utils.py within the
  kill_magicmirror_processes function

## Version 1.14

- Bug fix (#no number). Fixed issue with update command, where git commands place stdout in stderr
  position

## Version 1.15

- Code cleanup. Split up files more appropriately
- Enhancment. Split up functionality of command line options into groups
- Enhancment. Added options for user to control MagicMirror from CLI (similar to GUI)
- Enhancment. Added ability for user to add new external module title, author, repo, and description
  from CLI without prompt required
- Enhancment. Added ability for user to open the MMPM GUI from terminal, and display the URL
- Enhancement. Added ability for user to view log files from CLI

## Version 1.25

- Enhancement. Reworked installation commands to handle conflicting names
- Enhancement. Reworked listing commands to display installed modules more accurately
- Bug fix (#29). Corrected `log.info` to `log.logger.info` in utils.py within the
  `kill_magicmirror_processes` function

## Version 2.01

- Massive, massive, upgrades. Total CLI, and GUI redo. Far too many changes to list.

## Version 2.02

- added `--guided-setup` option on the CLI to assist users with setting up MMPM when first installing
- cleaned up some error handling as well

## Version 2.03

- fixed small typos for the keyword `upgradeable`

## Version 2.04

- Bug fix (#44): fixed screen rotation from GUI due to key in dictionary not being cast to int from string

## Version 2.05

- Bug fix (#49): added logic to skip package with containing a `<del>` tag

## Version 2.06

- fixed location of custom.css

## Version 2.07

- fixed other references to custom.css

## Version 2.08

- Bug fix (#58) custom.css

## Version 2.09

- Added additional serialization to reduce loading package data bugs

## Version 2.12

- Fixes for bugs related to active modules and directories found in upgrade command

## Version 2.13

- security fixes and reorganized files (moved requirements.txt into deps folder and created dev-requirements.txt)

## Version 2.14

- updated dependency versions and fix for missing jinja module causing failed installation

## Version 2.15

- Removed `webssh` and terminal access in GUI
- Moved from `eventlet` to `gevent` to avoid Python 3.10 issues
- some code cleanup
