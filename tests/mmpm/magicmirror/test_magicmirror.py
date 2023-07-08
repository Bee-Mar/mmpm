#!/usr/bin/env python3
import unittest
import shutil
from mmpm.env import MMPMEnv, EnvVar
from mmpm.magicmirror.magicmirror import MagicMirror
from unittest.mock import patch, MagicMock
from pathlib import PosixPath, Path

class MutableMagicMock(MagicMock):
    def __setattribute__(self, name, value):
        if name == 'get':
            self._mock_children[name] = value
        else:
            super().__setattribute__(name, value)

class MockedMMPMEnv(MMPMEnv):
    def __init__(self):
        super().__init__()

        # Mock the environment variables here
        self.mmpm_magicmirror_root = MutableMagicMock()
        self.mmpm_magicmirror_uri = MutableMagicMock()
        self.mmpm_magicmirror_pm2_process_name = MutableMagicMock()
        self.mmpm_magicmirror_docker_compose_file = MutableMagicMock()
        self.mmpm_is_docker_image = MutableMagicMock()
        self.mmpm_log_level = MutableMagicMock()

        self.mmpm_magicmirror_root.get.return_value = Path("/tmp/MagicMirror")
        self.mmpm_magicmirror_uri.get.return_value = "http://localhost:8080"
        self.mmpm_magicmirror_pm2_process_name.get.return_value = ""
        self.mmpm_magicmirror_docker_compose_file.get.return_value = ""
        self.mmpm_is_docker_image.get.return_value = False
        self.mmpm_log_level.get.return_value = "INFO"


class MagicMirrorTestCase(unittest.TestCase):
    @patch('mmpm.magicmirror.magicmirror.run_cmd')
    @patch('mmpm.magicmirror.magicmirror.chdir')
    def test_update(self, mock_chdir, mock_run_cmd):
        mock_run_cmd.return_value = (0, '', 'output')
        mock_chdir.return_value = None

        mm = MagicMirror()
        mm.env = MockedMMPMEnv()

        root: PosixPath = mm.env.mmpm_magicmirror_root.get()
        (root / ".git").mkdir(parents=True, exist_ok=True)

        can_upgrade = mm.update()

        mock_chdir.assert_called_once_with(root)
        mock_run_cmd.assert_called_once_with(['git', 'fetch', '--dry-run'], progress=False)
        self.assertEqual(can_upgrade, True)
        shutil.rmtree(root)

    @patch('mmpm.magicmirror.magicmirror.run_cmd')
    def test_upgrade(self, mock_run_cmd):
        mock_run_cmd.side_effect = [
            (0, '', ''),
            (0, '', ''),
            (0, '', '')
        ]

        mm = MagicMirror()
        mm.env = MockedMMPMEnv()

        root: PosixPath = mm.env.mmpm_magicmirror_root.get()
        (root / ".git").mkdir(parents=True, exist_ok=True)

        success = mm.upgrade()

        mock_run_cmd.assert_called_with(['npm', 'install'], progress=True)
        self.assertEqual(success, True)
        shutil.rmtree(root)

    @patch('mmpm.magicmirror.magicmirror.run_cmd')
    @patch('mmpm.magicmirror.magicmirror.chdir')
    @patch('mmpm.magicmirror.magicmirror.os')
    def test_install(self, mock_os, mock_chdir, mock_run_cmd):
        mock_run_cmd.return_value = (0, '', '')
        mock_chdir.return_value = None

        mm = MagicMirror()
        mm.env = MockedMMPMEnv()

        with patch('mmpm.magicmirror.magicmirror.prompt') as mock_prompt:
            mock_prompt.return_value = True
            success = mm.install()

        mock_prompt.assert_called_once()
        mock_os.system.assert_called_once()
        self.assertEqual(success, True)

    @patch('mmpm.magicmirror.magicmirror.prompt')
    @patch('mmpm.magicmirror.magicmirror.print')
    @patch('mmpm.magicmirror.magicmirror.shutil')
    def test_remove(self, mock_shutil, mock_print, mock_prompt):
        mock_prompt.return_value = True

        mm = MagicMirror()
        mm.env = MockedMMPMEnv()

        root: PosixPath = mm.env.mmpm_magicmirror_root.get()
        (root / ".git").mkdir(parents=True, exist_ok=True)

        success = mm.remove()

        mock_prompt.assert_called_once_with('Are you sure you want to remove MagicMirror?')
        mock_shutil.rmtree.assert_called_once()
        self.assertEqual(success, True)

if __name__ == '__main__':
    unittest.main()
