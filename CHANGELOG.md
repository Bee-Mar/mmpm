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

## Version 2.15 [DELETED]

- Removed `webssh` and terminal access in GUI
- Moved from `eventlet` to `gevent` to avoid Python 3.10 issues
- some code cleanup

## Version 2.16

- fixed missing leading slash of API URL

## Version 3.0

- upgraded dependencies for GUI
- fixed URL path causing duplicate static endpoints
- changed import path of gevent.monkey `patch_all` call
- changed installation method of MagicMirror via `mmpm install --magicmirror`

## Version 3.1

- hotfix to update parsing based on 3rd Party Modules page changes

## Version 4.0.0

- total rework of the entire application

## Version 4.0.1

- fix for opening UI url from CLI

## Version 4.0.2

- added guard on determining host IP address in `mmpm.constants.paths`
- added import guard for Python3.8 when using `importlib.resources` in `mmpm.ui`
- added check for MMPM being a docker image when self upgrading

## Version 4.0.3

- hotfix of conditional dependency

## Version 4.0.4

- hotfix of calling get on env vars

## Version 4.1.0

- removed extra log messages to reduce log pollution
- changed casing of function names in UI to conform to camelCasing
- using appropriate interpreter based on environment in ecosystem.json
- removed custom package directory extension to prevent naming issues in config.json
- removed multi-threading options from gunicorn servers

## Version 4.1.1

- Update `ui.py` to identify the correct location of gunicorn to resolve issues encountered when
    installing through `pipx`

## Version 4.1.2

- pulled in changes from dependabot

## Version 4.1.3

- updated urls from PR
- Simple cleanup

## Version 4.2.0

- corrected typo in `mmpm/magicmirror/magicmirror.py` instructing user to use outdated `mmpm log`
    command; now directing them to use `mmpm logs`

- Dropped support for  Python<=3.8
- Update dependencies

## Version 4.2.1

- moved to use of PDM package manager to Poetry and adjusted build scripts accordingly

## Version 4.2.2

- updated version of angular to mitigate vulnerabilities
- including pm2 logs in the `mmpm logs -z` subcommand
- removed unnecessary print calls made in the package display method

## Version 4.2.3

- improved performance of displaying packages

## Version 4.2.4

- typo in package.py

## Version 4.2.5

- include assets recursively

## Version 4.3.0

- Replace wiki scraping with official JSON modules index (`modules.magicmirror.builders`)
- Remove `beautifulsoup4` dependency
- Improve test coverage with mocked HTTP requests
- Move `stars` and `last_updated` fields from remote details to the base package fields

## Version 4.4.0

- Add backwards compatibility for `custom.css` and `custom.css.sample` files based on upcoming release of MagicMirror

## Version 4.5.0

### UI

- Complete UI modernization: dark theme built on an oklch color system, redesigned application shell with a collapsible navigation rail, resizable right-side dock panel, and a persistent header
- Angular updated from 19 to 21; PrimeNG updated from 16 to 21; ESLint migrated to v9 flat config
- Added animated splash screen with a minimum 3-second display duration
- Added Mirror Preview panel: visually arrange MagicMirror modules across regions by drag-and-drop, with live read and write of `config.js`
- Marketplace: card and table views with sortable columns (title, category, author, status, stars) and resizable table columns in table view
- Marketplace: card sort controls always visible in the toolbar; per-package progress indicators during cart checkout
- Marketplace: packages flagged with INSTALLED and UPDATE badges; mmpm itself blocked from self-install
- Toggle Modules panel moved from a floating drawer into the dock alongside the cart and other panels, styled consistently with the rest of the design system
- Increased global font sizes for improved readability
- Dock resize capped to always preserve a minimum content area width
- View mode (cards/table) persisted in a cookie across sessions

### Backend

- `MagicMirrorController.start()` now detects the active display server at runtime and selects the appropriate npm start script: `npm run start:x11`, `npm run start:wayland`, or `npm run start:windows`
- Fixed latent bug where `ELECTRON_DISABLE_SANDBOX=1` was passed as the first element of the command array, causing `shutil.which` to look for it instead of `npm`
- Flask now serves the Angular SPA directly, injecting `window.MMPM_CONFIG` into `index.html` at request time; the pre-built wheel works behind a reverse proxy without rebuilding (resolves [#190](https://github.com/Bee-Mar/mmpm/issues/190))
- Added `MMPM_UI_API_BASE_URL` and `MMPM_UI_SOCKET_URL` to `MMPMEnv` / `mmpm-env.json`; set these to configure the API base URL and Socket.IO URL when running behind a reverse proxy

### Bug Fixes

- Mirror Preview: fixed config.js save — brace scanning now blanks JS comments before parsing, so `{` / `}` inside comments no longer produce phantom module blocks; newly-dragged modules are correctly appended on save
- Fixed Angular template type cast in sort control binding to avoid pipe parser conflict
- Fixed fragile relative `environments/environment` import path — replaced with `@env/environment` alias defined in `tsconfig.json`

### Tests

- Added 167 new unit tests, raising coverage from 66% to 99%
- Added `TestDetectDisplayServerScript` covering X11, Wayland (via `XDG_SESSION_TYPE` and `WAYLAND_DISPLAY`), Windows, and the fallback path

## Version 4.6.0

### UI

- Added "Currently Installed" tab in the navigation rail showing all installed packages (marketplace and custom) with search, sort, card, and table views
- Mirror Preview: Config Editor save now automatically triggers a layout reset so the visual grid always reflects the saved `config.js` without requiring a manual Reset click
- Mirror Preview: persistent warning banner lists any modules referenced in `config.js` that are not installed; clears automatically when the missing packages are installed
- Config Editor: persistent warning banner below the toolbar lists the same uninstalled modules while `config.js` is active; updates live when packages are installed or the file is saved
- Upgrades panel: replaced `p-listbox` with native-styled list matching the design system
- Package details panel: "Upgrade now" button appears for installed packages that have an available upgrade

### Backend

- `MagicMirrorPackage.upgrade()` rewritten: uses `git stash` / `git stash pop` to preserve local changes before pulling, surfaces error text from git through to the API response and UI toasts, rolls back via `git reset --hard ORIG_HEAD` if dependency installation fails after a successful pull
- `run_cmd()` gained an optional `cwd` parameter; `upgrade()` passes it instead of using process-global `os.chdir()`
- `MMPMEnv` promoted from a per-instance `__init__` assignment to a class-level attribute across all 14 consumer classes, making the singleton relationship explicit
- `mmpm list --categories` package count replaced O(n²) double-scan with a single `Counter` pass

### Bug Fixes

- Mirror Preview warning banner now fires on every code path including the localStorage cache early-return, not only when `config.js` is fetched from the API
- Mirror Preview correctly picks up a `config.js` save made while the panel was off-screen (`@if`-destroyed), via a `configJsDirty` flag checked on remount

### Tests

- Fixed test suite after `MMPMEnv` class-level attribute refactor: replaced instance-attribute assignment (blocked by `__slots__`) with `patch.object(MagicMirrorPackage, "env", ...)` + `addCleanup`
- All 245 tests passing

## Version 4.6.1

### UI

- Fixed 404 errors on `/api/env`, `/api/packages`, and `/api/mmpm/version`: the `mmpm.ui` PM2 process now runs the Flask app (gunicorn) on port 7890 instead of `python -m http.server`, so the Angular SPA is served with `window.MMPM_CONFIG` injection and relative `/api/*` calls resolve correctly
- Log stream viewer: server-side replay buffer (last 500 entries) so logs accumulated while the panel was navigated away are shown immediately on return
- Log stream viewer: auto-follow scrolling rewritten using Monaco's `onDidChangeModelContent` event and `setScrollPosition` — eliminates the timing race that caused follow mode to silently drop out after a few entries
- Log stream viewer: "Follow" button appears in the toolbar when auto-scroll is paused; clicking it jumps to the bottom and re-enables following; scrolling back to the bottom re-enables it automatically
- Log stream viewer: level filter bar (DEBUG / INFO / WARNING / ERROR / CRITICAL) with per-level color coding; selected levels persisted as a cookie (`mmpm-log-level-filter`)
- Log stream viewer: configurable auto-clear window (1 h / 2 h / 4 h / **6 h** default / 12 h / 24 h) with selection persisted as a cookie (`mmpm-log-max-age-h`); old entries pruned every 2 minutes in the background
- Database dropdown (update, upgrades) added to the "Installed" panel header, matching the Marketplace panel
- Category filter bars in Marketplace and Installed panels are now drag-scrollable with the mouse; cursor changes to a grab hand as a visual affordance
- PrimeNG toast notifications restyled to match the dark UI: dark `--bg-2` base, per-severity colored borders and summary text (signal / warn / danger / accent-2), bright `--fg-1` detail text; achieved via `definePreset` dark token overrides and `darkModeSelector: ':root'`

## Version 4.6.2

### CI/CD Pipeline

- Bumping version to 4.6.2 to trigger a new build
- Stale cache within CI/CD pipeline caused incorrect wheels to be built thus producing inconsistent builds

## Version 4.6.3

### Bug Fixes

- Fixed working tree reset in `MagicMirrorPackage.upgrade()` to use `git restore .` instead of the deprecated `git checkout .`; `git restore` is the correct modern command for discarding working tree changes

### Build

- Fixed `nix build` failure caused by Angular attempting to inline Google Fonts over the network during the production build; disabled `optimization.fonts.inline` in the production configuration so fonts continue to load at runtime via `<link>` as intended
- Fixed `postinstall` script bash quoting bug where `[ -x $(command -v b2n) ]` evaluated truthy when `b2n` was absent, causing a spurious "command not found" error in the Nix sandbox
- Updated Python and UI dependencies

### Tooling

- `bun.nix` no longer regenerates on every `direnv reload` / shell entry; the devshell now runs `bun install --ignore-scripts` to skip lifecycle scripts during shell initialization, and `lock` explicitly regenerates `bun.nix` after `bun update`
- Added `sync:version` pre-commit hook that reads the version from `pyproject.toml` and keeps `mmpm/__version__.py` and `ui/package.json` in sync automatically on every commit
- Removed unused `axios` dependency from the UI
- Replaced `npm run` with `node --run` in the MagicMirror start command and CI lint step (requires Node 22+)

## Version 4.6.4

### UI

- Available Upgrades panel: added a "Select All" row at the top of the upgrade list; clicking it selects all upgradable packages at once; the checkbox shows a tri-state appearance (checked / indeterminate / unchecked) reflecting the current selection
- Available Upgrades panel: upgrade operations now show immediate visual feedback — each item transitions to an amber spinner ("working"), then to a green check ("done") or red × ("failed") as results arrive; the "Upgrade selected" button displays "Upgrading…" with a spinning icon while the operation runs; items and the Select All row are disabled during execution to prevent accidental changes mid-run
- Shopping cart: upgradable packages selected from the Installed view are now correctly routed to `postUpgradePackages` rather than `postRemovePackages`; a dedicated "QUEUED · UPGRADE" section appears in the cart above installs and removals
