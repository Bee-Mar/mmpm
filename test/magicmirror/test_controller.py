#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, patch

from mmpm.magicmirror.controller import (MagicMirrorClientFactory,
                                         MagicMirrorController)


class TestMagicMirrorController(unittest.TestCase):
    @patch("mmpm.magicmirror.controller.socketio.Client")
    def test_status(self, mock_client):
        client_instance = MagicMock()
        mock_client.return_value = client_instance

        # Instantiate and test
        controller = MagicMirrorController()
        controller.status()
        client_instance.connect.assert_called_with("http://localhost:8080")

    @patch("mmpm.magicmirror.controller.run_cmd")
    @patch("mmpm.magicmirror.controller.shutil.which")
    @patch("mmpm.magicmirror.controller.os.chdir")
    @patch("mmpm.magicmirror.controller.MMPMEnv")
    def test_start_with_npm(self, mock_env, mock_chdir, mock_which, mock_run_cmd):
        # Mock environment and dependencies
        mock_env.return_value.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.get.return_value = None
        mock_env.return_value.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.get.return_value = None
        mock_env.return_value.MMPM_MAGICMIRROR_ROOT.get.return_value = "/path/to/magicmirror"
        mock_which.side_effect = lambda x: "/usr/bin/" + x if x in ["npm"] else None
        mock_run_cmd.return_value = (0, "", "")  # Simulate successful command execution

        # Instantiate and start MagicMirror
        controller = MagicMirrorController()
        success = controller.start()
        self.assertTrue(success)
        mock_run_cmd.assert_called_with(["npm", "run", "start"], progress=False, background=True)

    # Similar structure for test_stop, test_restart, test_is_running

    @patch("mmpm.magicmirror.controller.get_pids")
    def test_is_running(self, mock_get_pids):
        # Mock get_pids to simulate MagicMirror processes running
        mock_get_pids.side_effect = lambda x: [12345] if x == "electron" else []

        # Instantiate and check if MagicMirror is running
        controller = MagicMirrorController()
        self.assertTrue(controller.is_running())

        # Simulate no MagicMirror processes running
        mock_get_pids.side_effect = lambda x: []
        self.assertFalse(controller.is_running())


if __name__ == "__main__":
    unittest.main()
