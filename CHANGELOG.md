# Version 0.1

- Initial creation of MMPM package manager

# Version 0.2

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

# Version 0.25

- Updated `display_modules` to display the output as a formatted table

- Version 0.3 will focus on performance improvements, and code cleanup

# Version 0.26

- Removed `pygit2` from dependencies, and replaced with `os.system` call

# Version 0.261

- Minor change in font color when installing packages

# Version 0.265

- Fixed small bug where checking for updates could happen twice if the snapshot file needed to be
  updated. The enhancement command now will only run once at most in either case.

# Version 0.266

- Accidentally created issue with `npm install` by placing text color in front of `os.system`
  command

- Also, removed unused variables

# Version 0.267

- Tidying up some output messages, nothing important

# Version 0.268

- I'm done tidying up today

# Version 0.269

- forgot to remove debug statement

# Version 0.270

- cleanup

# Version 0.275

- Added new method `install_magicmirror` to handle installation/upgrades of MagicMirror itself
- Can be called with `mmpm -M` or `mmpm --magicmirror`

# Version 0.3

- Resolved major performance issue with `import pip`. Changed logic to only import when needed to
  install packages
- Reduced execution time by a lot, but there is still some issues that can be fixed to speed up more
- Still in need of more code cleanup

# Version 0.31

- Changed error handling and added user help for installing missing modules
- Planning to convert to module with setup.py file for easier installation

# Version 0.32

- Moved to setup.py format. Initial setup works, will add in system requirements later

# Version 0.33

- Adding in the makefile again because I didn't think long term about this and probably locked
  myself into the format of installing with a makefile...

# Version 0.34

- Small fix made to urllib import as well as fixed breaking bug in description collection

# Version 0.35

- Bug fixes to installatio

# Version 0.36

- Issue with checking for version number

# Version 0.37

- Added env variable to allow for non-traditional installation location of MagicMirror

# Version 0.38

- Bug with upgrading module

# Version 0.39

- Readme update and bug fix

# Version 0.5

- Added ability for user to configure external sources for modules
- Bug fixes
- Code cleanup
