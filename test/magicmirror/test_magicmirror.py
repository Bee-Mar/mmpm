#!/usr/bin/env python3
import shutil
import unittest
from pathlib import Path, PosixPath
from test.helpers import MockedMMPMEnv
from unittest.mock import MagicMock, patch

from mmpm.magicmirror.magicmirror import MagicMirror


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
