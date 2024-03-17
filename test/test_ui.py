#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, mock_open, patch

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


if __name__ == "__main__":
    unittest.main()
