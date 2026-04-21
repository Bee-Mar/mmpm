import shutil
import unittest
from pathlib import Path, PosixPath
from unittest.mock import patch

from mmpm.constants.paths import MMPM_CONFIG_DIR
from mmpm.magicmirror.magicmirror import MagicMirror, MagicMirrorConfigs
from tests.helpers import MockedMMPMEnv


class MagicMirrorConfigsTestCase(unittest.TestCase):
    @patch("mmpm.magicmirror.magicmirror.MMPMEnv")
    def test_config_js(self, mock_env):
        mock_env.return_value.MMPM_MAGICMIRROR_ROOT.get.return_value = Path("/tmp/MagicMirror")
        configs = MagicMirrorConfigs()
        self.assertEqual(configs.config_js, Path("/tmp/MagicMirror") / "config" / "config.js")

    @patch("mmpm.magicmirror.magicmirror.MMPMEnv")
    def test_config_js_sample(self, mock_env):
        configs = MagicMirrorConfigs()
        self.assertEqual(configs.config_js_sample, MMPM_CONFIG_DIR / "config" / "config.js.sample")

    @patch("mmpm.magicmirror.magicmirror.MMPMEnv")
    def test_custom_css(self, mock_env):
        mock_env.return_value.MMPM_MAGICMIRROR_ROOT.get.return_value = Path("/tmp/MagicMirror")
        configs = MagicMirrorConfigs()

        # patch the exists method to return True in the case of the legacy path existing
        with patch.object(Path, "exists", return_value=True):
            self.assertEqual(configs.custom_css, Path("/tmp/MagicMirror") / "config" / "custom.css")

        # patch the exists method to return False in the case of the legacy path not existing
        with patch.object(Path, "exists", return_value=False):
            self.assertEqual(configs.custom_css, Path("/tmp/MagicMirror") / "css" / "custom.css")

    @patch("mmpm.magicmirror.magicmirror.MMPMEnv")
    def test_custom_css_sample(self, mock_env):
        mock_env.return_value.MMPM_MAGICMIRROR_ROOT.get.return_value = Path("/tmp/MagicMirror")

        # patch the exists method to return True in the case of the legacy path existing
        with patch.object(Path, "exists", return_value=True):
            configs = MagicMirrorConfigs()
            self.assertEqual(configs.custom_css_sample, Path("/tmp/MagicMirror") / "config" / "custom.css.sample")

        # patch the exists method to return False in the case of the legacy path not existing
        with patch.object(Path, "exists", return_value=False):
            configs = MagicMirrorConfigs()
            self.assertEqual(configs.custom_css_sample, Path("/tmp/MagicMirror") / "css" / "custom.css.sample")

    def test_get(self):
        configs = MagicMirrorConfigs()

        self.assertEqual(configs.get(configs.custom_css.name), configs.custom_css)
        self.assertEqual(configs.get(configs.custom_css_sample.name), configs.custom_css_sample)
        self.assertEqual(configs.get(configs.config_js.name), configs.config_js)
        self.assertEqual(configs.get(configs.config_js_sample.name), configs.config_js_sample)


class MagicMirrorTestCase(unittest.TestCase):
    @patch("mmpm.magicmirror.magicmirror.repo_up_to_date")
    @patch("mmpm.magicmirror.magicmirror.chdir")
    def test_update(self, mock_chdir, mock_repo_up_to_date):
        mock_repo_up_to_date.return_value = True
        mock_chdir.return_value = None

        mm = MagicMirror()
        mm.env = MockedMMPMEnv()

        root: PosixPath = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        (root / ".git").mkdir(parents=True, exist_ok=True)

        can_upgrade = mm.update()

        mock_chdir.assert_called_once_with(root)
        mock_repo_up_to_date.assert_called_with(root)
        self.assertTrue(can_upgrade)
        shutil.rmtree(root)

    @patch("mmpm.magicmirror.magicmirror.run_cmd")
    def test_upgrade(self, mock_run_cmd):
        mock_run_cmd.side_effect = [(0, "", ""), (0, "", ""), (0, "", "")]

        mm = MagicMirror()
        mm.env = MockedMMPMEnv()

        root: PosixPath = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        (root / ".git").mkdir(parents=True, exist_ok=True)

        success = mm.upgrade()

        mock_run_cmd.assert_called_with(["npm", "install"], progress=True)
        self.assertEqual(success, True)
        shutil.rmtree(root)

    @patch("mmpm.magicmirror.magicmirror.run_cmd")
    @patch("mmpm.magicmirror.magicmirror.chdir")
    def test_install(self, mock_chdir, mock_run_cmd):
        mock_run_cmd.return_value = (0, "", "")
        mock_chdir.return_value = None

        mm = MagicMirror()
        mm.env = MockedMMPMEnv()

        success = mm.install()
        self.assertEqual(success, True)

    @patch("mmpm.magicmirror.magicmirror.print")
    @patch("mmpm.magicmirror.magicmirror.shutil")
    @patch("mmpm.magicmirror.magicmirror.os.getcwd")
    def test_remove(self, mock_cwd, mock_shutil, mock_print):
        mock_cwd.return_value = "/tmp"

        mm = MagicMirror()
        mm.env = MockedMMPMEnv()

        root: PosixPath = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        (root / ".git").mkdir(parents=True, exist_ok=True)

        success = mm.remove()

        mock_shutil.rmtree.assert_called_once()
        self.assertEqual(success, True)


class MagicMirrorConfigsGetTestCase(unittest.TestCase):
    """Test MagicMirrorConfigs.get() for the unknown-file case (lines 32-36)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}

    @patch("mmpm.magicmirror.magicmirror.MMPMEnv")
    def test_get_unknown_file_returns_none(self, mock_env):
        """Lines 35-36: get() returns None for unknown file names."""
        configs = MagicMirrorConfigs()
        result = configs.get("nonexistent_file.txt")
        self.assertIsNone(result)

    @patch("mmpm.magicmirror.magicmirror.MMPMEnv")
    def test_mmpm_env_json(self, mock_env):
        """Lines 60-62: mmpm_env_json property returns correct path."""
        configs = MagicMirrorConfigs()
        result = configs.mmpm_env_json
        self.assertTrue(str(result).endswith("mmpm-env.json"))

    @patch("mmpm.magicmirror.magicmirror.MMPMEnv")
    def test_get_mmpm_env_json(self, mock_env):
        """get() for mmpm_env_json returns the correct path."""
        configs = MagicMirrorConfigs()
        result = configs.get(configs.mmpm_env_json.name)
        self.assertEqual(result, configs.mmpm_env_json)


class MagicMirrorUpdateTestCase(unittest.TestCase):
    """More thorough update() tests (lines 87-88, 97-99)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}

    def test_update_no_git_repo(self):
        """Lines 87-88: returns False when .git dir doesn't exist."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()

        # Create root but NOT the .git directory
        root.mkdir(parents=True, exist_ok=True)

        result = mm.update()
        self.assertFalse(result)
        shutil.rmtree(root, ignore_errors=True)

    def test_update_root_not_exists(self):
        """Lines 86-88: returns False when root doesn't exist."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()

        # Ensure it doesn't exist
        shutil.rmtree(root, ignore_errors=True)

        result = mm.update()
        self.assertFalse(result)

    @patch("mmpm.magicmirror.magicmirror.sys.exit", side_effect=SystemExit(127))
    @patch("mmpm.magicmirror.magicmirror.repo_up_to_date", side_effect=KeyboardInterrupt)
    @patch("mmpm.magicmirror.magicmirror.chdir")
    def test_update_keyboard_interrupt(self, mock_chdir, mock_repo, mock_exit):
        """Lines 97-99: KeyboardInterrupt calls sys.exit(127)."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        (root / ".git").mkdir(parents=True, exist_ok=True)

        with self.assertRaises(SystemExit) as ctx:
            mm.update()
        self.assertEqual(ctx.exception.code, 127)
        shutil.rmtree(root, ignore_errors=True)


class MagicMirrorUpgradeTestCase(unittest.TestCase):
    """Tests for upgrade() error paths (lines 120-122, 129-131, 136-138, 143-144)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}

    def test_upgrade_root_not_exists(self):
        """Lines 120-122: returns False when root dir doesn't exist."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        shutil.rmtree(root, ignore_errors=True)

        result = mm.upgrade()
        self.assertFalse(result)

    @patch("mmpm.magicmirror.magicmirror.run_cmd")
    def test_upgrade_git_checkout_fails(self, mock_run_cmd):
        """Lines 129-131: returns stderr string when git checkout fails."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        root.mkdir(parents=True, exist_ok=True)

        mock_run_cmd.return_value = (1, "", "checkout failed")

        result = mm.upgrade()
        # Returns the stderr string on checkout failure
        self.assertEqual(result, "checkout failed")
        shutil.rmtree(root, ignore_errors=True)

    @patch("mmpm.magicmirror.magicmirror.run_cmd")
    def test_upgrade_git_pull_fails(self, mock_run_cmd):
        """Lines 136-138: returns stderr string when git pull fails."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        root.mkdir(parents=True, exist_ok=True)

        mock_run_cmd.side_effect = [(0, "", ""), (1, "", "pull failed")]

        result = mm.upgrade()
        self.assertEqual(result, "pull failed")
        shutil.rmtree(root, ignore_errors=True)

    @patch("mmpm.magicmirror.magicmirror.run_cmd")
    def test_upgrade_npm_install_fails(self, mock_run_cmd):
        """Lines 143-144: returns False when npm install fails."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        root.mkdir(parents=True, exist_ok=True)

        mock_run_cmd.side_effect = [(0, "", ""), (0, "", ""), (1, "", "npm error")]

        result = mm.upgrade()
        self.assertFalse(result)
        shutil.rmtree(root, ignore_errors=True)


class MagicMirrorInstallTestCase(unittest.TestCase):
    """Tests for install() error paths (lines 164-166, 170-171, 184-185, 196-197)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}

    def test_install_already_installed(self):
        """Lines 163-166: returns False when MagicMirror is already installed."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()

        # Create the directories that indicate MM is already installed
        (root / "modules").mkdir(parents=True, exist_ok=True)
        (root / "node_modules").mkdir(parents=True, exist_ok=True)

        result = mm.install()
        self.assertFalse(result)
        shutil.rmtree(root, ignore_errors=True)

    @patch("mmpm.magicmirror.magicmirror.shutil.which")
    def test_install_missing_git(self, mock_which):
        """Lines 169-171: returns False when git is not in PATH."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        shutil.rmtree(root, ignore_errors=True)

        mock_which.return_value = None  # neither git nor npm found

        result = mm.install()
        self.assertFalse(result)

    @patch("mmpm.magicmirror.magicmirror.run_cmd")
    @patch("mmpm.magicmirror.magicmirror.shutil.which")
    @patch("mmpm.magicmirror.magicmirror.chdir")
    def test_install_git_clone_fails(self, mock_chdir, mock_which, mock_run_cmd):
        """Lines 183-185: returns False when git clone fails."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        shutil.rmtree(root, ignore_errors=True)

        mock_which.return_value = "/usr/bin/git"
        mock_run_cmd.return_value = (1, "", "clone failed")

        result = mm.install()
        self.assertFalse(result)
        shutil.rmtree(root, ignore_errors=True)

    @patch("mmpm.magicmirror.magicmirror.run_cmd")
    @patch("mmpm.magicmirror.magicmirror.shutil.which")
    @patch("mmpm.magicmirror.magicmirror.chdir")
    def test_install_npm_install_fails(self, mock_chdir, mock_which, mock_run_cmd):
        """Lines 196-197: returns False when npm install-mm fails."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        root.mkdir(parents=True, exist_ok=True)  # already exists, skip clone

        mock_which.return_value = "/usr/bin/npm"
        mock_run_cmd.return_value = (1, "", "npm install failed")

        result = mm.install()
        self.assertFalse(result)
        shutil.rmtree(root, ignore_errors=True)


class MagicMirrorRemoveTestCase(unittest.TestCase):
    """Tests for remove() (lines 218-220, 223)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}

    def test_remove_root_not_exists(self):
        """Lines 218-220: returns False when root doesn't exist."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        shutil.rmtree(root, ignore_errors=True)

        result = mm.remove()
        self.assertFalse(result)

    @patch("mmpm.magicmirror.magicmirror.os.getcwd")
    @patch("mmpm.magicmirror.magicmirror.os.chdir")
    @patch("mmpm.magicmirror.magicmirror.shutil.rmtree")
    def test_remove_when_cwd_is_root(self, mock_rmtree, mock_chdir, mock_getcwd):
        """Line 223: when cwd == root, chdirs to /tmp first."""
        mm = MagicMirror()
        mm.env = MockedMMPMEnv()
        root = mm.env.MMPM_MAGICMIRROR_ROOT.get()
        root.mkdir(parents=True, exist_ok=True)
        mock_getcwd.return_value = str(root)

        result = mm.remove()
        mock_chdir.assert_called_once_with("/tmp")
        self.assertTrue(result)
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
