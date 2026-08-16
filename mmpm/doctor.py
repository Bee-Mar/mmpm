"""Shared diagnostics used by the 'doctor' CLI subcommand and the /api/doctor endpoint"""

import datetime
import json
import socket
from os import getenv
from pathlib import Path
from shutil import which
from typing import Callable, List, Optional

import requests

from mmpm.constants import paths, urls
from mmpm.env import MMPM_DEFAULT_ENV, MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.lockfile import Lockfile
from mmpm.magicmirror.magicmirror import MagicMirror, MagicMirrorConfigs
from mmpm.magicmirror.package import RemotePackage

logger = MMPMLogFactory.get_logger(__name__)

PASS = "pass"
WARN = "warn"
FAIL = "fail"


class Doctor:
    """
    Runs read-only diagnostics on the MMPM installation: environment sanity,
    external dependencies, database health, installed package integrity,
    running services, and remote API availability.

    Attributes:
        app_name (str): The CLI application name, used in remediation hints.
        database (MagicMirrorDatabase): An instance of the MagicMirrorDatabase class for managing the database.
        lockfile (Lockfile): An instance of the Lockfile class for reading recorded package versions.
        env (MMPMEnv): A singleton of MMPMEnv which contains environment variables
        results (List[dict]): The diagnostic results accumulated by run().
    """

    env: MMPMEnv = MMPMEnv()

    def __init__(self, app_name: str = "mmpm"):
        self.app_name = app_name
        self.database = MagicMirrorDatabase()
        self.lockfile = Lockfile()
        self.magicmirror = MagicMirror()
        self.mm_configs = MagicMirrorConfigs()
        self.results: List[dict] = []
        self.on_check: Optional[Callable[[dict], None]] = None

    def check(self, status: str, category: str, label: str, hint: str = "") -> None:
        """
        Records a single diagnostic result and notifies the on_check callback, if set.

        Parameters:
            status (str): one of 'pass', 'warn', 'fail'
            category (str): the diagnostic group the check belongs to
            label (str): short description of the check
            hint (str): suggested remediation, shown for non-passing checks

        Returns:
            None
        """

        result = {"status": status, "category": category, "check": label, "hint": hint}
        self.results.append(result)

        if self.on_check:
            self.on_check(result)

    def run(self, on_check: Optional[Callable[[dict], None]] = None) -> List[dict]:
        """
        Runs all diagnostic checks.

        Parameters:
            on_check (Callable): optional callback invoked with each result as it is produced

        Returns:
            List[dict]: all diagnostic results, each with status, category, check, and hint keys
        """

        self.results = []
        self.on_check = on_check

        self.check_env()
        self.check_magicmirror()
        self.check_dependencies()
        self.check_database()
        self.check_packages()
        self.check_services()
        self.check_remote_apis()

        return self.results

    def check_env(self) -> None:
        category = "environment"

        try:
            contents = paths.MMPM_ENV_FILE.read_text(encoding="utf-8").strip()
            env_vars: dict = json.loads(contents) if contents else {}
        except (OSError, json.JSONDecodeError) as error:
            self.check(
                FAIL,
                category,
                f"Environment file is not valid JSON ({paths.MMPM_ENV_FILE})",
                f"Fix or delete the file, then run `{self.app_name} guided-setup`. Error: {error}",
            )
            return

        self.check(PASS, category, f"Environment file is valid JSON ({paths.MMPM_ENV_FILE})")

        unknown = set(env_vars) - set(MMPM_DEFAULT_ENV)

        if unknown:
            self.check(
                WARN,
                category,
                f"Unrecognized environment variable(s): {', '.join(sorted(unknown))}",
                f"Check for typos with `{self.app_name} env --describe`",
            )
        else:
            self.check(PASS, category, "No unrecognized environment variables")

        pm2_proc = self.env.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.get()
        compose_file = str(self.env.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.get() or "")

        if pm2_proc and compose_file:
            self.check(
                WARN,
                category,
                "Both MMPM_MAGICMIRROR_PM2_PROCESS_NAME and MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE are set",
                f"Only one is used to control MagicMirror. Clear one with `{self.app_name} open env`",
            )
        elif pm2_proc and not which("pm2"):
            self.check(FAIL, category, f"PM2 process '{pm2_proc}' is configured, but pm2 is not in your PATH", "Run `npm install -g pm2`")
        elif compose_file and not Path(compose_file).exists():
            self.check(
                FAIL,
                category,
                f"MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE does not exist: {compose_file}",
                f"Correct the path with `{self.app_name} open env`",
            )
        else:
            self.check(PASS, category, "MagicMirror process manager configuration is coherent")

    def check_magicmirror(self) -> None:
        category = "magicmirror"
        root: Path = self.env.MMPM_MAGICMIRROR_ROOT.get()

        if not root.exists():
            self.check(
                FAIL,
                category,
                f"MagicMirror root does not exist: {root}",
                f"Run `{self.app_name} mm install`, or correct MMPM_MAGICMIRROR_ROOT with `{self.app_name} open env`",
            )
        else:
            self.check(PASS, category, f"MagicMirror root exists ({root})")

            if not self.magicmirror.is_installed:
                self.check(WARN, category, f"MagicMirror does not appear to be fully installed in {root}", f"Run `{self.app_name} mm install`")

            if not (root / ".git").exists():
                self.check(
                    WARN,
                    category,
                    f"{root} is not a git repository",
                    f"`{self.app_name} update` and `{self.app_name} upgrade MagicMirror` will not work for MagicMirror",
                )

            config_js = self.mm_configs.config_js

            if not config_js.exists() or not config_js.stat().st_size:
                self.check(WARN, category, "MagicMirror config/config.js is missing or empty", f"Run `{self.app_name} open config` to create it")
            else:
                self.check(PASS, category, "MagicMirror config/config.js exists")

        uri = self.env.MMPM_MAGICMIRROR_URI.get()

        try:
            reachable = requests.get(uri, timeout=3).status_code == 200
        except requests.exceptions.RequestException:
            reachable = False

        if reachable:
            self.check(PASS, category, f"MagicMirror is reachable at {uri}")
        else:
            self.check(
                WARN,
                category,
                f"MagicMirror is not responding at {uri}",
                f"Start it with `{self.app_name} mm start`, or correct MMPM_MAGICMIRROR_URI with `{self.app_name} open env`",
            )

    def check_dependencies(self) -> None:
        category = "dependencies"

        for binary in ("git", "node", "npm"):
            if which(binary):
                self.check(PASS, category, f"'{binary}' found in PATH")
            else:
                self.check(FAIL, category, f"'{binary}' not found in PATH", f"Install '{binary}' — it is required for package management")

        if which("pm2"):
            self.check(PASS, category, "'pm2' found in PATH")
        else:
            self.check(
                WARN,
                category,
                "'pm2' not found in PATH",
                f"Required for `{self.app_name} ui` and PM2-managed MagicMirror control. Run `npm install -g pm2`",
            )

        if getenv("EDITOR") or getenv("VISUAL"):
            self.check(PASS, category, "$EDITOR is set")
        else:
            self.check(WARN, category, "$EDITOR is not set", f"`{self.app_name} open config` will fall back to nano")

    def check_database(self) -> None:
        category = "database"

        if not self.database.is_initialized():
            self.database.load()

        if not self.database.packages:
            self.check(FAIL, category, "Package database is empty or failed to load", f"Run `{self.app_name} update`")
            return

        self.check(PASS, category, f"Package database loaded ({len(self.database.packages)} packages)")

        info = self.database.info()
        last_update = str(info.get("last_update", ""))

        try:
            age = datetime.datetime.now() - datetime.datetime.fromisoformat(last_update)

            if age.days > 7:
                self.check(WARN, category, f"Package database is {age.days} days old", f"Run `{self.app_name} update`")
            else:
                self.check(PASS, category, f"Package database is up to date (last update: {last_update})")
        except ValueError:
            self.check(WARN, category, "Unable to determine when the package database was last updated", f"Run `{self.app_name} update`")

        try:
            contents = paths.MMPM_AVAILABLE_UPGRADES_FILE.read_text(encoding="utf-8").strip()

            if contents:
                json.loads(contents)

            self.check(PASS, category, "Available-upgrades file is valid")
        except (OSError, json.JSONDecodeError):
            self.check(WARN, category, "Available-upgrades file is corrupted", f"It will be reset the next time `{self.app_name} update` runs")

    def check_packages(self) -> None:
        category = "packages"
        modules_dir: Path = self.env.MMPM_MAGICMIRROR_ROOT.get() / "modules"

        if not modules_dir.exists():
            return

        known_directories = {package.directory.name for package in self.database.packages}
        installed_directories = {path.name for path in modules_dir.iterdir() if path.is_dir() and not path.name.startswith(".")}

        orphans = sorted(installed_directories - known_directories - {"default"})

        if orphans:
            self.check(
                WARN,
                category,
                f"Module(s) not tracked by {self.app_name}: {', '.join(orphans)}",
                f"Add them as custom packages with `{self.app_name} custom-pkg add` to manage them",
            )
        else:
            self.check(PASS, category, f"All installed modules are tracked ({len(installed_directories)} found)")

        dirty = sorted(directory for directory in installed_directories & known_directories if not (modules_dir / directory / ".git").exists())

        if dirty:
            self.check(
                WARN,
                category,
                f"Module(s) missing a .git directory: {', '.join(dirty)}",
                f"`{self.app_name} upgrade` cannot update them; reinstall with `{self.app_name} add`",
            )

        stale_lock = sorted(set(self.lockfile.load()) - installed_directories)

        if stale_lock:
            self.check(
                WARN,
                category,
                f"Lockfile entries for module(s) no longer installed: {', '.join(stale_lock)}",
                f"Run `{self.app_name} sync` to reinstall them, or ignore if removal was intentional",
            )
        else:
            self.check(PASS, category, "Lockfile agrees with installed modules")

        if any(package.title == "MMM-mmpm" and package.is_installed for package in self.database.packages):
            self.check(PASS, category, "MMM-mmpm module is installed (module hide/show available)")
        else:
            self.check(
                WARN,
                category,
                "MMM-mmpm module is not installed",
                f"`{self.app_name} mm hide/show` requires it. Install with `{self.app_name} add MMM-mmpm`",
            )

    def check_services(self) -> None:
        category = "services"

        for label, port, hint in (
            (f"{self.app_name} UI", urls.MMPM_UI_PORT, f"Start it with `{self.app_name} ui start`, or install it with `{self.app_name} ui install`"),
            (f"{self.app_name} API server", urls.MMPM_API_SERVER_PORT, f"Start it with `{self.app_name} ui start`"),
        ):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)

                if sock.connect_ex(("127.0.0.1", port)) == 0:
                    self.check(PASS, category, f"{label} is listening on port {port}")
                else:
                    self.check(WARN, category, f"{label} is not listening on port {port}", hint)

    def check_remote_apis(self) -> None:
        category = "remote"

        try:
            health = RemotePackage.health()
        except Exception as error:  # the health check parses remote responses and may raise on malformed data
            self.check(WARN, category, "Unable to check remote API health", str(error))
            return

        for api, status in health.items():
            if status["error"]:
                self.check(WARN, category, f"{api}: {status['error']}")
            elif status["warning"]:
                self.check(WARN, category, f"{api}: {status['warning']}")
            else:
                self.check(PASS, category, f"{api} API is reachable")
