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


if __name__ == "__main__":
    unittest.main()
