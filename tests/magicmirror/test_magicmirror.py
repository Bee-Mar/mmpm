#!/usr/bin/env python3
import unittest
import shutil
from mmpm.magicmirror.magicmirror import MagicMirror
from unittest.mock import patch, MagicMock
from pathlib import PosixPath, Path
from tests.helpers import MockedMMPMEnv


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
