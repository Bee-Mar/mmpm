#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, patch

from faker import Faker

from mmpm.env import MMPMEnv
from mmpm.magicmirror.controller import MagicMirrorClientFactory, MagicMirrorController

fake = Faker()


class TestMagicMirrorClientFactory(unittest.TestCase):
    @patch("mmpm.magicmirror.controller.socketio.Client")
    def test_create_client_valid(self, mock_client):
        client = MagicMirrorClientFactory.create_client("test_event", {"data": "test"})
        self.assertIsNotNone(client)
        mock_client.assert_called()

    @patch("mmpm.magicmirror.controller.socketio.Client")
    def test_create_client_invalid(self, mock_client):
        client = MagicMirrorClientFactory.create_client("", {})
        self.assertIsNone(client)
        mock_client.assert_not_called()


class TestMagicMirrorController(unittest.TestCase):
    @patch("mmpm.magicmirror.controller.socketio.Client")
    def test_status(self, mock_client):
        client_instance = MagicMock()
        mock_client.return_value = client_instance

        controller = MagicMirrorController()
        controller.status()

        client_instance.connect.assert_called_with(MMPMEnv().MMPM_MAGICMIRROR_URI.get())

    @patch("mmpm.magicmirror.controller.Path.exists")
    @patch("mmpm.magicmirror.controller.run_cmd")
    @patch("mmpm.magicmirror.controller.shutil.which")
    @patch("mmpm.magicmirror.controller.os.chdir")
    @patch("mmpm.magicmirror.controller.MMPMEnv")
    def test_start_with_npm(self, mock_env, mock_chdir, mock_which, mock_run_cmd, mock_exists):
        # Mock environment and dependencies
        mock_env.return_value.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.get.return_value = None
        mock_env.return_value.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.get.return_value = None
        mock_env.return_value.MMPM_MAGICMIRROR_ROOT.get.return_value = "/path/to/magicmirror"
        mock_exists.return_value = True
        mock_which.side_effect = lambda x: "/usr/bin/" + x if x in ["npm"] else None
        mock_run_cmd.return_value = (0, "", "")  # Simulate successful command execution

        # Instantiate and start MagicMirror
        controller = MagicMirrorController()
        success = controller.start()
        self.assertTrue(success)
        mock_run_cmd.assert_called_with(["npm", "run", "start"], message="Starting MagicMirror", background=True)

    @patch("mmpm.magicmirror.controller.socketio.Client")
    def test_hide_modules(self, mock_client):
        client_instance = MagicMock()
        mock_client.return_value = client_instance

        # Test hide
        controller = MagicMirrorController()
        controller.env = MMPMEnv()

        modules = [fake.pystr() for _ in range(5)]

        controller.hide(modules)
        client_instance.connect.assert_called_with(controller.env.MMPM_MAGICMIRROR_URI.get())

    @patch("mmpm.magicmirror.controller.socketio.Client")
    def test_show_modules(self, mock_client):
        client_instance = MagicMock()
        mock_client.return_value = client_instance

        controller = MagicMirrorController()
        controller.env = MMPMEnv()

        modules = [fake.pystr() for _ in range(5)]

        controller.show(modules)
        client_instance.connect.assert_called_with(controller.env.MMPM_MAGICMIRROR_URI.get())


if __name__ == "__main__":
    unittest.main()
