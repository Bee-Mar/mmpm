import unittest
from unittest.mock import patch

from mmpm.ui import MMPMui  # Replace 'mmpm.ui' with the name of your module


class TestMMPMui(unittest.TestCase):
    def setUp(self):
        self.mmpm_ui = MMPMui()

    @patch("mmpm.ui.which")
    @patch("mmpm.ui.MMPMui.create_pm2_config")
    @patch("mmpm.ui.MMPMui.start")
    def test_install_pm2_missing(self, mock_start, mock_create_config, mock_which):
        mock_which.return_value = None
        result = self.mmpm_ui.install()
        self.assertFalse(result)
        mock_create_config.assert_not_called()
        mock_start.assert_not_called()

    @patch("mmpm.ui.which")
    @patch("mmpm.ui.MMPMui.create_pm2_config")
    @patch("mmpm.ui.MMPMui.start")
    def test_install_failure_start(self, mock_start, mock_create_config, mock_which):
        mock_which.return_value = "/usr/bin/pm2"
        mock_start.return_value = (1, "", "error")  # Simulate failure
        result = self.mmpm_ui.install()
        self.assertFalse(result)
        mock_create_config.assert_called_once()
        mock_start.assert_called_once()

    @patch("mmpm.ui.which")
    @patch("mmpm.ui.MMPMui.create_pm2_config")
    @patch("mmpm.ui.MMPMui.start")
    def test_install_success(self, mock_start, mock_create_config, mock_which):
        mock_which.return_value = "/usr/bin/pm2"
        mock_start.return_value = (0, "", "")  # Simulate success
        result = self.mmpm_ui.install()
        self.assertTrue(result)
        mock_create_config.assert_called_once()
        mock_start.assert_called_once()

    # Test remove method
    @patch("mmpm.ui.which")
    @patch("mmpm.ui.MMPMui.create_pm2_config")
    @patch("mmpm.ui.MMPMui.delete")
    @patch("mmpm.ui.rmtree")
    def test_remove_pm2_missing(self, mock_rmtree, mock_delete, mock_create_config, mock_which):
        mock_which.return_value = None
        result = self.mmpm_ui.remove()
        self.assertFalse(result)
        mock_create_config.assert_not_called()
        mock_delete.assert_not_called()
        mock_rmtree.assert_not_called()

    @patch("mmpm.ui.which")
    @patch("mmpm.ui.MMPMui.create_pm2_config")
    @patch("mmpm.ui.MMPMui.delete")
    @patch("mmpm.ui.rmtree")
    def test_remove_success(self, mock_rmtree, mock_delete, mock_create_config, mock_which):
        mock_which.return_value = "/usr/bin/pm2"
        mock_delete.return_value = (0, "", "")  # Simulate success
        result = self.mmpm_ui.remove()
        self.assertTrue(result)
        mock_create_config.assert_called_once()
        mock_delete.assert_called_once()
        mock_rmtree.assert_called_once_with(self.mmpm_ui.pm2_config_path.parent, ignore_errors=True)

    @patch("mmpm.ui.MMPMui.create_pm2_config")
    @patch("mmpm.ui.os.system")
    def test_status(self, mock_os_system, mock_create_config):
        self.mmpm_ui.status()
        mock_os_system.assert_called_once_with("pm2 list mmpm")
        mock_create_config.assert_called_once()

    def test_create_pm2_config(self):
        """Lines 74-81: create_pm2_config creates the file and writes JSON."""
        from pathlib import Path
        from unittest.mock import mock_open

        m = mock_open()
        with patch("mmpm.ui.open", m), patch("mmpm.ui.json.dump") as mock_dump, patch.object(Path, "mkdir"), patch.object(Path, "touch"):
            self.mmpm_ui.create_pm2_config()
            # Verify open was called for writing
            m.assert_called()
            mock_dump.assert_called_once()

    @patch("mmpm.ui.run_cmd")
    def test_stop(self, mock_run_cmd):
        """Line 94: stop calls run_cmd with pm2 stop."""
        mock_run_cmd.return_value = (0, "", "")
        self.mmpm_ui.stop()
        mock_run_cmd.assert_called_once()
        args = mock_run_cmd.call_args[0][0]
        self.assertIn("pm2", args)
        self.assertIn("stop", args)

    @patch("mmpm.ui.run_cmd")
    def test_delete(self, mock_run_cmd):
        """Line 107: delete calls run_cmd with pm2 delete."""
        mock_run_cmd.return_value = (0, "", "")
        self.mmpm_ui.delete()
        mock_run_cmd.assert_called_once()
        args = mock_run_cmd.call_args[0][0]
        self.assertIn("pm2", args)
        self.assertIn("delete", args)

    @patch("mmpm.ui.run_cmd")
    def test_start(self, mock_run_cmd):
        """Line 120: start calls run_cmd with pm2 start."""
        mock_run_cmd.return_value = (0, "", "")
        self.mmpm_ui.start()
        mock_run_cmd.assert_called_once()
        args = mock_run_cmd.call_args[0][0]
        self.assertIn("pm2", args)
        self.assertIn("start", args)

    @patch("mmpm.ui.which")
    @patch("mmpm.ui.MMPMui.create_pm2_config")
    @patch("mmpm.ui.MMPMui.delete")
    @patch("mmpm.ui.rmtree")
    def test_remove_failure_delete(self, mock_rmtree, mock_delete, mock_create_config, mock_which):
        """Lines 176-177: remove returns False when delete fails."""
        mock_which.return_value = "/usr/bin/pm2"
        mock_delete.return_value = (1, "", "deletion error")
        result = self.mmpm_ui.remove()
        self.assertFalse(result)
        mock_rmtree.assert_not_called()


if __name__ == "__main__":
    unittest.main()
