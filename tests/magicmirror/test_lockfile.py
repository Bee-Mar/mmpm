import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from mmpm.magicmirror.lockfile import Lockfile
from mmpm.magicmirror.package import MagicMirrorPackage

REPO = "https://github.com/test/MMM-Test.git"


class LockFileTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.lock_file = Path(self.tmp.name) / "mmpm.lock"
        self.lock_file.touch()
        self.lockfile = Lockfile()
        patcher = patch.object(self.lockfile, "file", self.lock_file)
        patcher.start()
        self.addCleanup(patcher.stop)


class TestLockFile(LockFileTestCase):
    def test_load_empty_file(self):
        self.assertEqual(self.lockfile.load(), {})

    def test_load_invalid_json(self):
        self.lock_file.write_text("{not json", encoding="utf-8")
        self.assertEqual(self.lockfile.load(), {})

    def test_record_and_get(self):
        self.lockfile.record("MMM-Test", REPO, "abc123")
        entry = self.lockfile.get("MMM-Test")
        self.assertEqual(entry, {"repository": REPO, "sha": "abc123"})
        self.assertIsNone(self.lockfile.get("MMM-Other"))

    def test_record_persists_versioned_format(self):
        self.lockfile.record("MMM-Test", REPO, "abc123")
        contents = json.loads(self.lock_file.read_text(encoding="utf-8"))
        self.assertEqual(contents["version"], Lockfile.VERSION)
        self.assertEqual(contents["packages"]["MMM-Test"]["sha"], "abc123")

    def test_record_pushes_previous_sha_to_history(self):
        self.lockfile.record("MMM-Test", REPO, "sha1", via="install")
        self.lockfile.record("MMM-Test", REPO, "sha2", via="upgrade")

        entry = self.lockfile.get("MMM-Test")
        self.assertEqual(entry["sha"], "sha2")
        self.assertEqual(len(entry["history"]), 1)
        self.assertEqual(entry["history"][0]["sha"], "sha1")
        self.assertEqual(entry["history"][0]["via"], "upgrade")
        self.assertEqual(self.lockfile.previous("MMM-Test"), "sha1")

    def test_record_same_sha_leaves_history_untouched(self):
        self.lockfile.record("MMM-Test", REPO, "sha1")
        self.lockfile.record("MMM-Test", REPO, "sha1")
        self.assertEqual(self.lockfile.history("MMM-Test"), [])

    def test_rolling_back_to_history_sha_does_not_duplicate_it(self):
        self.lockfile.record("MMM-Test", REPO, "sha1", via="install")
        self.lockfile.record("MMM-Test", REPO, "sha2", via="upgrade")
        self.lockfile.record("MMM-Test", REPO, "sha1", via="rollback")

        entry = self.lockfile.get("MMM-Test")
        self.assertEqual(entry["sha"], "sha1")
        shas = [item["sha"] for item in entry["history"]]
        self.assertEqual(shas, ["sha2"])

    def test_history_is_bounded(self):
        for index in range(Lockfile.MAX_HISTORY + 5):
            self.lockfile.record("MMM-Test", REPO, f"sha{index}")

        history = self.lockfile.history("MMM-Test")
        self.assertEqual(len(history), Lockfile.MAX_HISTORY)
        self.assertEqual(history[0]["sha"], f"sha{Lockfile.MAX_HISTORY + 3}")

    def test_previous_without_history(self):
        self.assertIsNone(self.lockfile.previous("MMM-Test"))
        self.lockfile.record("MMM-Test", REPO, "sha1")
        self.assertIsNone(self.lockfile.previous("MMM-Test"))

    def test_remove(self):
        self.lockfile.record("MMM-Test", REPO, "abc123")
        self.assertTrue(self.lockfile.remove("MMM-Test"))
        self.assertIsNone(self.lockfile.get("MMM-Test"))
        self.assertFalse(self.lockfile.remove("MMM-Test"))


class TestLockedPackageBehavior(LockFileTestCase):
    def setUp(self):
        super().setUp()

        self.env_mock = MagicMock()
        self.env_mock.MMPM_MAGICMIRROR_ROOT.get.return_value = Path(self.tmp.name)
        env_patcher = patch.object(MagicMirrorPackage, "env", self.env_mock)
        env_patcher.start()
        self.addCleanup(env_patcher.stop)

        (Path(self.tmp.name) / "modules").mkdir()

        self.package = MagicMirrorPackage(
            title="Test Package",
            repository=REPO,
            directory="MMM-Test",
            is_installed=True,
        )

    def test_install_records_lock_entry(self):
        with (
            patch("mmpm.magicmirror.package.InstallationHandler.install", return_value=True),
            patch("mmpm.magicmirror.package.run_cmd", return_value=(0, "abcdef123\n", "")),
        ):
            self.assertTrue(self.package.install())

        self.assertEqual(self.lockfile.get("MMM-Test"), {"repository": REPO, "sha": "abcdef123"})

    def test_failed_install_records_nothing(self):
        with patch("mmpm.magicmirror.package.InstallationHandler.install", return_value=False):
            self.assertFalse(self.package.install())

        self.assertIsNone(self.lockfile.get("MMM-Test"))

    def test_remove_drops_lock_entry(self):
        self.lockfile.record("MMM-Test", REPO, "abc123")

        with patch("mmpm.magicmirror.package.run_cmd", return_value=(0, "", "")):
            self.assertTrue(self.package.remove())

        self.assertIsNone(self.lockfile.get("MMM-Test"))

    def test_upgrade_refreshes_lock_entry(self):
        self.lockfile.record("MMM-Test", REPO, "oldsha")

        def run_cmd_stub(command, **kwargs):
            if command[:2] == ["git", "rev-parse"]:
                return 0, "newsha\n", ""
            if command[:3] == ["git", "symbolic-ref", "-q"]:
                return 0, "refs/heads/master\n", ""  # on a branch, not detached
            if command[:2] == ["git", "pull"]:
                return 0, "Already up to date.", ""
            return 0, "", ""

        with patch("mmpm.magicmirror.package.run_cmd", side_effect=run_cmd_stub):
            success, error = self.package.upgrade()

        self.assertTrue(success)
        self.assertEqual(self.lockfile.get("MMM-Test")["sha"], "newsha")
        self.assertEqual(self.lockfile.previous("MMM-Test"), "oldsha")

    def test_upgrade_returns_to_default_branch_from_detached_head(self):
        """After a rollback (detached HEAD), upgrade checks out the default branch,
        reinstalls dependencies, and moves the lock forward."""
        self.lockfile.record("MMM-Test", REPO, "oldsha")
        executed = []

        def run_cmd_stub(command, **kwargs):
            executed.append(command)
            if command[:3] == ["git", "symbolic-ref", "-q"]:
                return 1, "", ""  # detached HEAD
            if command[:2] == ["git", "symbolic-ref"]:
                return 0, "origin/main\n", ""
            if command[:2] == ["git", "rev-parse"]:
                return 0, "newsha\n", ""
            if command[:2] == ["git", "pull"]:
                return 0, "Already up to date.", ""
            return 0, "", ""

        with (
            patch("mmpm.magicmirror.package.run_cmd", side_effect=run_cmd_stub),
            patch("mmpm.magicmirror.package.InstallationHandler.install", return_value=True) as install_mock,
        ):
            success, error = self.package.upgrade()

        self.assertTrue(success)
        self.assertIn(["git", "checkout", "main"], executed)
        install_mock.assert_called_once()
        self.assertEqual(self.lockfile.get("MMM-Test")["sha"], "newsha")
        self.assertEqual(self.lockfile.previous("MMM-Test"), "oldsha")

    def test_rollback_requires_git_repository(self):
        success, error = self.package.rollback("abc123")
        self.assertFalse(success)
        self.assertIn("not a git repository", error)

    def test_rollback_checks_out_and_locks(self):
        (Path(self.tmp.name) / "modules" / "MMM-Test" / ".git").mkdir(parents=True)

        with (
            patch("mmpm.magicmirror.package.run_cmd", return_value=(0, "oldsha\n", "")),
            patch("mmpm.magicmirror.package.InstallationHandler.install", return_value=True),
        ):
            success, error = self.package.rollback("newsha")

        self.assertTrue(success)
        self.assertEqual(error, "")
        self.assertEqual(self.lockfile.get("MMM-Test"), {"repository": REPO, "sha": "newsha"})

    def test_rollback_restores_previous_on_dependency_failure(self):
        (Path(self.tmp.name) / "modules" / "MMM-Test" / ".git").mkdir(parents=True)

        with (
            patch("mmpm.magicmirror.package.run_cmd", return_value=(0, "oldsha\n", "")) as run_cmd_mock,
            patch("mmpm.magicmirror.package.InstallationHandler.install", return_value=False),
        ):
            success, error = self.package.rollback("newsha")

        self.assertFalse(success)
        self.assertIn("dependency installation failed", error)
        self.assertIsNone(self.lockfile.get("MMM-Test"))
        restore_call = run_cmd_mock.call_args_list[-1]
        self.assertEqual(restore_call.args[0], ["git", "checkout", "oldsha"])

    def test_sync_clones_missing_package_and_installs(self):
        cloned = []

        def run_cmd_stub(command, **kwargs):
            if command[:2] == ["git", "clone"]:
                cloned.append(command)
                (Path(self.tmp.name) / "modules" / "MMM-Test" / ".git").mkdir(parents=True)
                return 0, "", ""
            if command[:2] == ["git", "rev-parse"]:
                return 0, "lockedsha\n", ""
            return 0, "", ""

        with (
            patch("mmpm.magicmirror.package.run_cmd", side_effect=run_cmd_stub),
            patch("mmpm.magicmirror.package.InstallationHandler.install", return_value=True) as install_mock,
        ):
            success, error = self.package.sync("lockedsha")

        self.assertTrue(success)
        self.assertEqual(error, "")
        self.assertEqual(len(cloned), 1)
        install_mock.assert_called_once()

    def test_sync_noop_when_already_at_locked_commit(self):
        (Path(self.tmp.name) / "modules" / "MMM-Test" / ".git").mkdir(parents=True)

        with (
            patch("mmpm.magicmirror.package.run_cmd", return_value=(0, "lockedsha\n", "")),
            patch("mmpm.magicmirror.package.InstallationHandler.install") as install_mock,
        ):
            success, error = self.package.sync("lockedsha")

        self.assertTrue(success)
        install_mock.assert_not_called()

    def test_sync_checks_out_locked_commit_when_drifted(self):
        (Path(self.tmp.name) / "modules" / "MMM-Test" / ".git").mkdir(parents=True)
        executed = []

        def run_cmd_stub(command, **kwargs):
            executed.append(command)
            if command[:2] == ["git", "rev-parse"]:
                return 0, "driftedsha\n", ""
            return 0, "", ""

        with (
            patch("mmpm.magicmirror.package.run_cmd", side_effect=run_cmd_stub),
            patch("mmpm.magicmirror.package.InstallationHandler.install", return_value=True) as install_mock,
        ):
            success, error = self.package.sync("lockedsha")

        self.assertTrue(success)
        self.assertIn(["git", "checkout", "lockedsha"], executed)
        install_mock.assert_called_once()

    def test_sync_reports_checkout_failure(self):
        (Path(self.tmp.name) / "modules" / "MMM-Test" / ".git").mkdir(parents=True)

        def run_cmd_stub(command, **kwargs):
            if command[:2] == ["git", "rev-parse"]:
                return 0, "driftedsha\n", ""
            if command[:2] == ["git", "checkout"]:
                return 1, "", "fatal: reference is not a tree"
            return 0, "", ""

        with patch("mmpm.magicmirror.package.run_cmd", side_effect=run_cmd_stub):
            success, error = self.package.sync("lockedsha")

        self.assertFalse(success)
        self.assertIn("Failed to checkout", error)
