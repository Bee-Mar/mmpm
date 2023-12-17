#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, mock_open, patch

from mmpm.env import MMPMEnv
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.package import MagicMirrorPackage


class TestMagicMirrorDatabase(unittest.TestCase):
    def setUp(self):
        self.database = MagicMirrorDatabase()

    def test_download_packages(self):
        result = self.database.__download_packages__()
        self.assertIsInstance(result, list)

    @patch("mmpm.magicmirror.database.run_cmd")
    @patch("mmpm.magicmirror.database.Path.iterdir")
    def test_discover_installed_packages(self, mock_iterdir, mock_run_cmd):
        mock_iterdir.return_value = []
        mock_run_cmd.return_value = (0, "", "")

        # Test the __discover_installed_packages__ method
        result = self.database.__discover_installed_packages__()
        self.assertIsInstance(result, list)

    @patch("mmpm.magicmirror.database.MagicMirrorPackage.update")
    @patch("mmpm.magicmirror.database.open", new_callable=mock_open)
    def test_update(self, mock_file, mock_update):
        self.database.packages = [MagicMirrorPackage(title="Test Package")]

        result = self.database.update()
        self.assertFalse(result)

    @patch("mmpm.magicmirror.database.open", new_callable=mock_open)
    def test_add_mm_pkg(self, mock_file):
        mock_file.return_value.read.return_value = "[]"

        result = self.database.add_mm_pkg(
            title="Test Package",
            author="Test Author",
            repository="https://github.com/repo/test-package",
            description="Test Description",
        )

        self.assertTrue(result)

    @patch("mmpm.magicmirror.database.open", new_callable=mock_open)
    def test_remove_mm_pkg_success(self, mock_file):
        mock_file.return_value.read.return_value = '[{"title": "Test Package"}]'

        result = self.database.remove_mm_pkg(title="Test Package")
        self.assertTrue(result)

    @patch("mmpm.magicmirror.database.open", new_callable=mock_open)
    def test_remove_mm_pkg_failure(self, mock_file):
        mock_file.return_value.read.return_value = '[{"title": "Test Package"}]'

        result = self.database.remove_mm_pkg(title="Not found")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
