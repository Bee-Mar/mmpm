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
        # right now using actual data to download just to get something here
        result = self.database.__download_packages__()
        self.assertIsInstance(result, list)

    @patch("mmpm.magicmirror.database.run_cmd")
    @patch("mmpm.magicmirror.database.Path.iterdir")
    def test_discover_installed_packages(self, mock_iterdir, mock_run_cmd):
        # Mock the directory iteration and command execution
        mock_iterdir.return_value = []
        mock_run_cmd.return_value = (0, "", "")

        # Test the __discover_installed_packages__ method
        result = self.database.__discover_installed_packages__()
        self.assertIsInstance(result, list)

    @patch("mmpm.magicmirror.database.MagicMirrorPackage.update")
    @patch("mmpm.magicmirror.database.open", new_callable=mock_open)
    def test_update(self, mock_file, mock_update):
        # Mock the open function and the package update method
        self.database.packages = [MagicMirrorPackage(title="Test Package")]

        # Test the update method
        result = self.database.update()
        self.assertIsInstance(result, int)

    @patch("mmpm.magicmirror.database.open", new_callable=mock_open)
    def test_add_mm_pkg(self, mock_file):
        # Mock the open function
        mock_file.return_value.read.return_value = ""

        # Test the add_mm_pkg method
        result = self.database.add_mm_pkg(
            title="Test Package",
            author="Test Author",
            repository="https://example.com",
            description="Test Description",
        )

        self.assertIsInstance(result, bool)

    @patch("mmpm.magicmirror.database.open", new_callable=mock_open)
    def test_remove_mm_pkg(self, mock_file):
        # Mock the open function
        mock_file.return_value.read.return_value = '{"External Packages": [{"title": "Test Package"}]}'

        # Test the remove_mm_pkg method
        result = self.database.remove_mm_pkg(titles=["Test Package"], assume_yes=True)
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
