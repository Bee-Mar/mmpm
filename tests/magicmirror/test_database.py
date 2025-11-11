import unittest
from unittest.mock import MagicMock, mock_open, patch

import requests

from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.magicmirror.package import MagicMirrorPackage


class TestMagicMirrorDatabase(unittest.TestCase):
    def setUp(self):
        self.database = MagicMirrorDatabase()

    @patch("mmpm.magicmirror.database.requests.get")
    def test_download_packages(self, mock_get):
        """Test downloading and parsing modules from the JSON API with realistic data"""
        # Provide a realistic JSON response matching the actual format from modules.magicmirror.builders
        fake_response = MagicMock()
        fake_response.json.return_value = {
            "modules": [
                {
                    "name": "MMM-TestModule",
                    "category": "Utility / Testing",
                    "url": "https://github.com/testuser/MMM-TestModule",
                    "id": "testuser/MMM-TestModule",
                    "maintainer": "testuser",
                    "maintainerURL": "https://github.com/testuser",
                    "description": "A test module for unit testing",
                    "issues": True,
                    "stars": 5,
                    "license": "MIT",
                    "tags": ["test", "example"],
                    "defaultSortWeight": 10,
                    "lastCommit": "2024-01-01T12:00:00+00:00",
                },
                {
                    "name": "MMM-AnotherTest",
                    "category": "Weather",
                    "url": "https://github.com/anotheruser/MMM-AnotherTest",
                    "id": "anotheruser/MMM-AnotherTest",
                    "maintainer": "anotheruser",
                    "description": "Another test module",
                    "stars": 10,
                },
                # Test with minimal fields
                {
                    "name": "MMM-MinimalModule",
                    "url": "https://github.com/minimal/MMM-MinimalModule",
                },
            ]
        }
        fake_response.raise_for_status.return_value = None
        mock_get.return_value = fake_response

        result = self.database.__download_packages__()

        # Verify the result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

        # Check first module
        self.assertEqual(result[0].title, "MMM-TestModule")
        self.assertEqual(result[0].author, "testuser")
        self.assertEqual(result[0].repository, "https://github.com/testuser/MMM-TestModule")
        self.assertEqual(result[0].description, "A test module for unit testing")
        self.assertEqual(result[0].category, "Utility / Testing")
        self.assertEqual(result[0].directory.name, "MMM-TestModule")

        # Check second module
        self.assertEqual(result[1].title, "MMM-AnotherTest")
        self.assertEqual(result[1].category, "Weather")

        # Check minimal module (should handle missing fields gracefully)
        self.assertEqual(result[2].title, "MMM-MinimalModule")
        self.assertEqual(result[2].repository, "https://github.com/minimal/MMM-MinimalModule")
        # Missing fields default to "N/A", but author/title are sanitized (/ removed) -> "NA"
        self.assertEqual(result[2].author, "NA")
        self.assertEqual(result[2].description, "N/A")

        # Verify categories were extracted
        self.assertIn("Utility / Testing", self.database.categories)
        self.assertIn("Weather", self.database.categories)

    @patch("mmpm.magicmirror.database.requests.get")
    def test_download_packages_invalid_structure(self, mock_get):
        """Test handling of invalid JSON structure"""
        fake_response = MagicMock()
        # Missing "modules" key
        fake_response.json.return_value = {"invalid": "structure"}
        fake_response.raise_for_status.return_value = None
        mock_get.return_value = fake_response

        result = self.database.__download_packages__()
        self.assertEqual(result, [])

    @patch("mmpm.magicmirror.database.requests.get")
    def test_download_packages_network_error(self, mock_get):
        """Test handling of network errors"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = self.database.__download_packages__()
        self.assertEqual(result, [])

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
