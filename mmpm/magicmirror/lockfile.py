"""The MMPM lock file (~/.config/mmpm/mmpm.lock).

Similar in spirit to uv.lock: every installed package is automatically recorded
here with the exact commit it is checked out at, and stays locked there until a
deliberate operation moves it. Install locks the version, upgrade moves the lock
forward, rollback moves it back, remove drops the entry — the user never edits
the file directly. Entries are keyed by the package's directory name.

Each entry also keeps a bounded history of previously locked commits, recorded
automatically whenever the lock moves, so users can roll back precisely to a
version they actually had installed:

{
  "version": 1,
  "packages": {
    "MMM-Example": {
      "repository": "https://github.com/user/MMM-Example",
      "sha": "<commit>",
      "history": [
        {"sha": "<previous commit>", "replaced": "YYYY-MM-DD", "via": "upgrade"}
      ]
    }
  }
}
"""

import json
from datetime import date
from typing import Any, Dict, List, Optional

from mmpm.constants import paths
from mmpm.log.factory import MMPMLogFactory
from mmpm.singleton import Singleton

logger = MMPMLogFactory.get_logger(__name__)


class Lockfile(Singleton):
    """
    Singleton wrapper around the MMPM lock file. The file itself is the source
    of truth — every read goes back to disk so concurrent CLI/API processes
    always see the latest state.
    """

    VERSION: int = 1

    # How many previously installed commits to keep per package
    MAX_HISTORY: int = 10

    def __init__(self):
        self.file = paths.MMPM_LOCK_FILE

    def load(self) -> Dict[str, Dict[str, Any]]:
        """
        Reads the package entries from the lock file.

        Parameters:
            None

        Returns:
            Dict[str, Dict[str, Any]]: A mapping of package directory names to their lock entries.
        """
        try:
            contents = self.file.read_text(encoding="utf-8").strip()
            return json.loads(contents).get("packages", {}) if contents else {}
        except (OSError, json.JSONDecodeError) as error:
            logger.error(f"Failed to read {self.file}: {error}")
            return {}

    def save(self, packages: Dict[str, Dict[str, Any]]) -> None:
        """
        Writes the package entries to the lock file.

        Parameters:
            packages (Dict[str, Dict[str, Any]]): A mapping of package directory names to their lock entries.

        Returns:
            None
        """
        with open(self.file, mode="w", encoding="utf-8") as lock_file:
            json.dump({"version": self.VERSION, "packages": packages}, lock_file, indent=2)

    def get(self, directory: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the lock entry for a package, if any.

        Parameters:
            directory (str): The package's directory name.

        Returns:
            Optional[Dict[str, Any]]: The lock entry, or None if the package is not recorded.
        """
        return self.load().get(directory)

    def record(self, directory: str, repository: str, sha: str, via: str = "install") -> None:
        """
        Records (or updates) a package's lock entry. When the lock moves off an
        existing commit, that commit is pushed onto the entry's history so the user
        can precisely roll back to a version they previously had installed.

        Parameters:
            directory (str): The package's directory name.
            repository (str): The package's repository URL.
            sha (str): The commit sha the package is checked out at.
            via (str): The operation that moved the lock (install, upgrade, rollback).

        Returns:
            None
        """
        packages = self.load()
        entry = packages.get(directory) or {}
        previous_history: List[Dict[str, str]] = entry.get("history", [])
        previous_sha = entry.get("sha", "")

        if previous_sha and previous_sha != sha:
            # Rolling back to a commit already in the history shouldn't duplicate it.
            previous_history = [item for item in previous_history if item.get("sha") != sha]
            previous_history.insert(0, {"sha": previous_sha, "replaced": date.today().isoformat(), "via": via})
            previous_history = previous_history[: self.MAX_HISTORY]

        packages[directory] = {"repository": repository, "sha": sha}

        if previous_history:
            packages[directory]["history"] = previous_history

        self.save(packages)
        logger.debug(f"Locked {directory} at {sha} (via {via})")

    def remove(self, directory: str) -> bool:
        """
        Removes a package's lock entry.

        Parameters:
            directory (str): The package's directory name.

        Returns:
            bool: True if an entry was removed, False if the package was not recorded.
        """
        packages = self.load()

        if directory not in packages:
            return False

        del packages[directory]
        self.save(packages)
        logger.debug(f"Removed {directory} from lock file")
        return True

    def history(self, directory: str) -> List[Dict[str, str]]:
        """
        Retrieves the previously locked commits for a package, most recent first.

        Parameters:
            directory (str): The package's directory name.

        Returns:
            List[Dict[str, str]]: History items with 'sha', 'replaced', and 'via' keys.
        """
        entry = self.get(directory)
        return entry.get("history", []) if entry else []

    def previous(self, directory: str) -> Optional[str]:
        """
        Retrieves the most recently replaced commit sha for a package — the natural
        target for a no-argument rollback.

        Parameters:
            directory (str): The package's directory name.

        Returns:
            Optional[str]: The previous locked sha, or None if there is no history.
        """
        items = self.history(directory)
        return items[0]["sha"] if items else None
