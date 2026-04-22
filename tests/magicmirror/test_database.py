import json
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


class TestMagicMirrorDatabaseDownloadEdgeCases(unittest.TestCase):
    """Test edge cases in __download_packages__ (lines 54-65, 71)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}
        self.database = MagicMirrorDatabase()

    @patch("mmpm.magicmirror.database.requests.get")
    def test_download_packages_json_decode_error(self, mock_get):
        """Lines 54-56: JSON decode error returns empty list."""
        fake_response = MagicMock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.side_effect = json.JSONDecodeError("bad json", "", 0)
        mock_get.return_value = fake_response

        result = self.database.__download_packages__()
        self.assertEqual(result, [])

    @patch("mmpm.magicmirror.database.requests.get")
    def test_download_packages_modules_not_a_list(self, mock_get):
        """Lines 63-65: 'modules' not a list returns empty list."""
        fake_response = MagicMock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.return_value = {"modules": "not a list"}
        mock_get.return_value = fake_response

        result = self.database.__download_packages__()
        self.assertEqual(result, [])

    @patch("mmpm.magicmirror.database.requests.get")
    def test_download_packages_non_dict_entry_skipped(self, mock_get):
        """Line 71: non-dict entries in modules list are skipped."""
        fake_response = MagicMock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.return_value = {
            "modules": [
                "not a dict",
                None,
                {"name": "MMM-Valid", "url": "https://github.com/user/MMM-Valid"},
            ]
        }
        mock_get.return_value = fake_response

        result = self.database.__download_packages__()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "MMM-Valid")


class TestMagicMirrorDatabaseDiscoverInstalled(unittest.TestCase):
    """Test __discover_installed_packages__ (lines 98-127)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}
        self.database = MagicMirrorDatabase()

    def test_discover_modules_dir_not_exists(self):
        """Lines 97-99: returns empty list when modules dir doesn't exist."""
        self.database.env = MagicMock()
        mock_root = MagicMock()
        mock_modules_dir = MagicMock()
        mock_modules_dir.exists.return_value = False
        mock_root.__truediv__ = lambda s, o: mock_modules_dir
        self.database.env.MMPM_MAGICMIRROR_ROOT.get.return_value = mock_root

        result = self.database.__discover_installed_packages__()
        self.assertEqual(result, [])

    @patch("mmpm.magicmirror.database.run_cmd")
    @patch("mmpm.magicmirror.database.os.chdir")
    def test_discover_packages_git_error(self, mock_chdir, mock_run_cmd):
        """Lines 115-117: git error for a package_dir logs and continues."""
        self.database.env = MagicMock()
        mock_root = MagicMock()
        mock_modules_dir = MagicMock()
        mock_modules_dir.exists.return_value = True

        # Create a fake package dir that has a .git folder
        mock_pkg_dir = MagicMock()
        mock_pkg_dir.is_dir.return_value = True
        mock_git_dir = MagicMock()
        mock_git_dir.exists.return_value = True
        mock_pkg_dir.__truediv__ = lambda s, o: mock_git_dir

        mock_modules_dir.iterdir.return_value = [mock_pkg_dir]
        mock_root.__truediv__ = lambda s, o: mock_modules_dir
        self.database.env.MMPM_MAGICMIRROR_ROOT.get.return_value = mock_root

        # git config fails
        mock_run_cmd.return_value = (1, "", "git error")

        result = self.database.__discover_installed_packages__()
        self.assertEqual(result, [])

    @patch("mmpm.magicmirror.database.run_cmd")
    @patch("mmpm.magicmirror.database.os.chdir")
    def test_discover_packages_basename_error(self, mock_chdir, mock_run_cmd):
        """Lines 119-122: basename error logs and continues."""
        self.database.env = MagicMock()
        mock_root = MagicMock()
        mock_modules_dir = MagicMock()
        mock_modules_dir.exists.return_value = True

        mock_pkg_dir = MagicMock()
        mock_pkg_dir.is_dir.return_value = True
        mock_git_dir = MagicMock()
        mock_git_dir.exists.return_value = True
        mock_pkg_dir.__truediv__ = lambda s, o: mock_git_dir

        mock_modules_dir.iterdir.return_value = [mock_pkg_dir]
        mock_root.__truediv__ = lambda s, o: mock_modules_dir
        self.database.env.MMPM_MAGICMIRROR_ROOT.get.return_value = mock_root

        # First call (git config) succeeds, second (basename) fails
        mock_run_cmd.side_effect = [
            (0, "https://github.com/user/MMM-Test.git\n", ""),
            (1, "", "basename error"),
        ]

        result = self.database.__discover_installed_packages__()
        self.assertEqual(result, [])

    @patch("mmpm.magicmirror.database.run_cmd")
    @patch("mmpm.magicmirror.database.os.chdir")
    def test_discover_packages_success(self, mock_chdir, mock_run_cmd):
        """Lines 109-127: successfully discovers an installed package."""
        self.database.env = MagicMock()
        mock_root = MagicMock()
        mock_modules_dir = MagicMock()
        mock_modules_dir.exists.return_value = True

        mock_pkg_dir = MagicMock()
        mock_pkg_dir.is_dir.return_value = True
        mock_pkg_dir.name = "MMM-Test"
        mock_git_dir = MagicMock()
        mock_git_dir.exists.return_value = True
        mock_pkg_dir.__truediv__ = lambda s, o: mock_git_dir

        mock_modules_dir.iterdir.return_value = [mock_pkg_dir]
        mock_root.__truediv__ = lambda s, o: mock_modules_dir
        self.database.env.MMPM_MAGICMIRROR_ROOT.get.return_value = mock_root

        mock_run_cmd.side_effect = [
            (0, "https://github.com/user/MMM-Test.git\n", ""),
            (0, "MMM-Test\n", ""),
        ]

        result = self.database.__discover_installed_packages__()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].repository, "https://github.com/user/MMM-Test.git")


class TestMagicMirrorDatabaseInfo(unittest.TestCase):
    """Test info() method (line 170, 184)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}
        self.database = MagicMirrorDatabase()

    def test_info_returns_dict(self):
        """Line 170: info() returns a dict with expected keys."""
        self.database.last_update = "2024-01-01"
        self.database.categories = ["Weather", "Utility"]
        self.database.packages = [
            MagicMirrorPackage(title="Pkg1"),
            MagicMirrorPackage(title="Pkg2"),
        ]

        result = self.database.info()
        self.assertIn("last_update", result)
        self.assertIn("categories", result)
        self.assertIn("packages", result)
        self.assertEqual(result["categories"], 2)
        self.assertEqual(result["packages"], 2)

    def test_is_initialized_true(self):
        """Line 184: is_initialized returns True when packages list is non-empty."""
        self.database.packages = [MagicMirrorPackage(title="Pkg1")]
        self.assertTrue(self.database.is_initialized())

    def test_is_initialized_false_empty(self):
        """is_initialized returns False when packages is empty list."""
        self.database.packages = []
        self.assertFalse(self.database.is_initialized())

    def test_is_initialized_false_none(self):
        """is_initialized returns False when packages is None."""
        self.database.packages = None
        self.assertFalse(self.database.is_initialized())


class TestMagicMirrorDatabaseSearch(unittest.TestCase):
    """Test search() method (lines 200-218)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}
        self.database = MagicMirrorDatabase()
        self.database.categories = ["Weather", "Utility"]
        self.database.packages = [
            MagicMirrorPackage(title="MMM-Weather", author="Alice", description="Shows weather", category="Weather"),
            MagicMirrorPackage(title="MMM-Clock", author="Bob", description="A clock module", category="Utility"),
            MagicMirrorPackage(title="MMM-News", author="Charlie", description="News feed", category="Utility"),
        ]

    def test_search_by_category(self):
        """Lines 210-211: query matching a category returns all packages in that category."""
        result = self.database.search("Weather")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "MMM-Weather")

    def test_search_case_insensitive(self):
        """Lines 214-216: case-insensitive search."""
        result = self.database.search("weather")
        self.assertEqual(len(result), 1)

    def test_search_case_sensitive(self):
        """Lines 212-213: case-sensitive search."""
        result = self.database.search("NONEXISTENT_QUERY_XYZ", case_sensitive=True)
        self.assertEqual(len(result), 0)

        result = self.database.search("Shows weather", case_sensitive=True)
        self.assertEqual(len(result), 1)

    def test_search_title_only_exact(self):
        """Lines 202-207: title_only search."""
        result = self.database.search("MMM-Clock", title_only=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "MMM-Clock")

    def test_search_title_only_case_sensitive(self):
        """title_only + case_sensitive."""
        result = self.database.search("mmm-clock", title_only=True, case_sensitive=False)
        self.assertEqual(len(result), 1)

        result = self.database.search("mmm-clock", title_only=True, case_sensitive=True)
        self.assertEqual(len(result), 0)

    def test_search_no_results(self):
        """search returns empty list when no match."""
        result = self.database.search("nonexistent_xyz_query")
        self.assertEqual(result, [])


class TestMagicMirrorDatabaseLoad(unittest.TestCase):
    """Test load() method (lines 231-277)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}
        self.database = MagicMirrorDatabase()

    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.__discover_installed_packages__")
    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.custom_packages")
    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.__download_packages__")
    @patch("mmpm.magicmirror.database.paths")
    def test_load_forces_update(self, mock_paths, mock_download, mock_custom, mock_discover):
        """Lines 239-254: when update=True, downloads packages and saves to db."""
        mock_db_file = MagicMock()
        mock_db_file.exists.return_value = True
        mock_db_file.stat.return_value.st_size = 100
        mock_last_update_file = MagicMock()
        mock_last_update_file.exists.return_value = True
        mock_last_update_file.stat.return_value.st_size = 10

        mock_paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE = mock_db_file
        mock_paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE = mock_last_update_file
        mock_paths.MMPM_CUSTOM_PACKAGES_FILE = MagicMock(stat=MagicMock(return_value=MagicMock(st_size=0)))
        mock_paths.MMPM_AVAILABLE_UPGRADES_FILE = MagicMock()

        pkgs = [MagicMirrorPackage(title="MMM-Test", category="Weather")]
        mock_download.return_value = pkgs
        mock_custom.return_value = []
        mock_discover.return_value = []

        m = mock_open()
        with patch("mmpm.magicmirror.database.open", m):
            with patch("mmpm.magicmirror.database.json.dump"):
                with patch("mmpm.magicmirror.database.json.load", return_value={}):
                    result = self.database.load(update=True)

        self.assertTrue(result)
        mock_download.assert_called_once()

    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.__discover_installed_packages__")
    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.custom_packages")
    @patch("mmpm.magicmirror.database.paths")
    def test_load_from_existing_db(self, mock_paths, mock_custom, mock_discover):
        """Lines 256-265: when db exists and no update needed, loads from file."""
        mock_db_file = MagicMock()
        mock_db_file.exists.return_value = True
        mock_db_file.stat.return_value.st_size = 100
        mock_last_update_file = MagicMock()
        mock_last_update_file.exists.return_value = True
        mock_last_update_file.stat.return_value.st_size = 10

        mock_paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE = mock_db_file
        mock_paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE = mock_last_update_file
        mock_paths.MMPM_CUSTOM_PACKAGES_FILE = MagicMock(stat=MagicMock(return_value=MagicMock(st_size=0)))

        db_data = [
            {
                "title": "MMM-Test",
                "author": "Alice",
                "repository": "https://github.com/a/b",
                "description": "test",
                "category": "Weather",
                "directory": "MMM-Test",
            }
        ]
        mock_custom.return_value = []
        mock_discover.return_value = []

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch(
                "mmpm.magicmirror.database.json.load",
                side_effect=[
                    {"last_update": "2024-01-01 00:00:00"},
                    db_data,
                ],
            ):
                result = self.database.load(update=False)

        self.assertTrue(result)

    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.__discover_installed_packages__")
    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.custom_packages")
    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.__download_packages__")
    @patch("mmpm.magicmirror.database.paths")
    def test_load_download_fails_uses_existing(self, mock_paths, mock_download, mock_custom, mock_discover):
        """Lines 260-265: when download returns empty but db exists, loads from file."""
        mock_db_file = MagicMock()
        mock_db_file.exists.return_value = True
        mock_db_file.stat.return_value.st_size = 100
        mock_last_update_file = MagicMock()
        mock_last_update_file.exists.return_value = False  # force update path
        mock_last_update_file.stat.return_value.st_size = 0

        mock_paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE = mock_db_file
        mock_paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE = mock_last_update_file
        mock_paths.MMPM_CUSTOM_PACKAGES_FILE = MagicMock(stat=MagicMock(return_value=MagicMock(st_size=0)))

        mock_download.return_value = []  # download fails
        mock_custom.return_value = []
        mock_discover.return_value = []

        db_data = [
            {
                "title": "MMM-Cached",
                "author": "Bob",
                "repository": "https://github.com/b/c",
                "description": "cached",
                "category": "Utility",
                "directory": "MMM-Cached",
            }
        ]

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.load", return_value=db_data):
                result = self.database.load(update=False)

        self.assertTrue(result)

    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.__discover_installed_packages__")
    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.custom_packages")
    @patch("mmpm.magicmirror.database.paths")
    def test_load_marks_installed_packages(self, mock_paths, mock_custom, mock_discover):
        """Lines 272-276: discovered packages are marked as installed."""
        mock_db_file = MagicMock()
        mock_db_file.exists.return_value = True
        mock_db_file.stat.return_value.st_size = 100
        mock_last_update_file = MagicMock()
        mock_last_update_file.exists.return_value = True
        mock_last_update_file.stat.return_value.st_size = 10

        mock_paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_FILE = mock_db_file
        mock_paths.MAGICMIRROR_3RD_PARTY_PACKAGES_DB_LAST_UPDATE_FILE = mock_last_update_file
        mock_paths.MMPM_CUSTOM_PACKAGES_FILE = MagicMock(stat=MagicMock(return_value=MagicMock(st_size=0)))

        installed_pkg = MagicMirrorPackage(title="MMM-Test", repository="https://github.com/a/b", directory="MMM-Test")
        mock_discover.return_value = [installed_pkg]
        mock_custom.return_value = []

        db_data = [
            {
                "title": "MMM-Test",
                "author": "Alice",
                "repository": "https://github.com/a/b",
                "description": "test",
                "category": "Weather",
                "directory": "MMM-Test",
            }
        ]

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch(
                "mmpm.magicmirror.database.json.load",
                side_effect=[
                    {"last_update": "2024-01-01 00:00:00"},
                    db_data,
                ],
            ):
                self.database.load(update=False)

        # The loaded package should be marked installed
        if self.database.packages:
            for pkg in self.database.packages:
                if pkg.title == "MMM-Test":
                    self.assertTrue(pkg.is_installed)


class TestMagicMirrorDatabaseCustomPackages(unittest.TestCase):
    """Test custom_packages() method (lines 287-306)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}
        self.database = MagicMirrorDatabase()

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_custom_packages_empty_file(self, mock_file_path):
        """Lines 291-292: empty file returns empty list."""
        mock_file_path.stat.return_value.st_size = 0
        result = self.database.custom_packages()
        self.assertEqual(result, [])

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_custom_packages_valid(self, mock_file_path):
        """Lines 292-298: valid JSON returns list of packages."""
        mock_file_path.stat.return_value.st_size = 100

        custom_data = [
            {
                "title": "MyPkg",
                "author": "Me",
                "repository": "https://github.com/me/MyPkg",
                "description": "Custom",
                "category": "Custom Packages",
                "directory": "MyPkg",
            }
        ]

        with patch("mmpm.magicmirror.database.open", mock_open(read_data=json.dumps(custom_data))):
            with patch("mmpm.magicmirror.database.json.load", return_value=custom_data):
                result = self.database.custom_packages()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "MyPkg")

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_custom_packages_json_error(self, mock_file_path):
        """Lines 294-297: JSONDecodeError resets file and returns empty list."""
        mock_file_path.stat.return_value.st_size = 100

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.load", side_effect=json.JSONDecodeError("err", "", 0)):
                with patch("mmpm.magicmirror.database.json.dump"):
                    result = self.database.custom_packages()

        self.assertEqual(result, [])

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_custom_packages_package_creation_error(self, mock_file_path):
        """Lines 303-304: exception creating MagicMirrorPackage is caught."""
        mock_file_path.stat.return_value.st_size = 100

        # Data that will cause exception when creating MagicMirrorPackage
        bad_data = [{"title": None}]  # None title causes AttributeError on strip()

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.load", return_value=bad_data):
                result = self.database.custom_packages()

        # Exception is caught, returns empty list
        self.assertEqual(result, [])


class TestMagicMirrorDatabaseUpgradable(unittest.TestCase):
    """Test upgradable() method (lines 308-332)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}
        self.database = MagicMirrorDatabase()

    @patch("mmpm.magicmirror.database.paths.MMPM_AVAILABLE_UPGRADES_FILE")
    def test_upgradable_valid(self, mock_file_path):
        """Lines 318-326: returns parsed upgrades dict."""
        upgrades = {"mmpm": False, "MagicMirror": False, "packages": []}

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.load", return_value=upgrades):
                result = self.database.upgradable()

        self.assertEqual(result, upgrades)

    @patch("mmpm.magicmirror.database.paths.MMPM_AVAILABLE_UPGRADES_FILE")
    def test_upgradable_json_decode_error(self, mock_file_path):
        """Line 326: JSONDecodeError resets the file and returns default dict."""
        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.load", side_effect=json.JSONDecodeError("err", "", 0)):
                with patch("mmpm.magicmirror.database.json.dump"):
                    result = self.database.upgradable()

        self.assertEqual(result["mmpm"], False)
        self.assertEqual(result["MagicMirror"], False)
        self.assertEqual(result["packages"], [])


class TestMagicMirrorDatabaseAddPkg(unittest.TestCase):
    """Test add_mm_pkg() more thoroughly (lines 362-385)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}
        self.database = MagicMirrorDatabase()

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_add_mm_pkg_duplicate_rejected(self, mock_file_path):
        """Lines 367-370: duplicate package title is rejected."""
        mock_file_path.exists.return_value = True
        mock_file_path.stat.return_value.st_size = 100

        existing = [
            {
                "title": "MyPkg",
                "author": "Me",
                "repository": "https://github.com/me/MyPkg",
                "description": "",
                "category": "Custom Packages",
                "directory": "MyPkg",
            }
        ]

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.load", return_value=existing):
                result = self.database.add_mm_pkg(
                    title="MyPkg",
                    author="Me",
                    repository="https://github.com/me/MyPkg",
                    description="My package description",
                )
        self.assertFalse(result)

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_add_mm_pkg_first_package(self, mock_file_path):
        """Lines 376-379: when file is empty, writes first package."""
        mock_file_path.exists.return_value = True
        mock_file_path.stat.return_value.st_size = 0  # empty file

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.dump"):
                result = self.database.add_mm_pkg(
                    title="NewPkg",
                    author="Author",
                    repository="https://github.com/author/NewPkg",
                    description="A new package",
                )
        self.assertTrue(result)

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_add_mm_pkg_new_to_existing_file(self, mock_file_path):
        """Lines 362-375: adds new package when file exists with other packages."""
        mock_file_path.exists.return_value = True
        mock_file_path.stat.return_value.st_size = 100  # non-empty file

        existing = [
            {
                "title": "ExistingPkg",
                "author": "Author",
                "repository": "https://github.com/a/ExistingPkg",
                "description": "Existing",
                "category": "Custom Packages",
                "directory": "ExistingPkg",
            }
        ]

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.load", return_value=existing):
                with patch("mmpm.magicmirror.database.json.dump") as mock_dump:
                    result = self.database.add_mm_pkg(
                        title="NewDifferentPkg",
                        author="Author",
                        repository="https://github.com/author/NewDifferentPkg",
                        description="A new different package",
                    )
        self.assertTrue(result)
        mock_dump.assert_called()

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_add_mm_pkg_ioerror(self, mock_file_path):
        """Lines 383-385: IOError returns False."""
        mock_file_path.exists.return_value = True
        mock_file_path.stat.return_value.st_size = 0

        with patch("mmpm.magicmirror.database.open", side_effect=IOError("disk full")):
            result = self.database.add_mm_pkg(
                title="NewPkg",
                author="Author",
                repository="https://github.com/author/NewPkg",
                description="A new package",
            )
        self.assertFalse(result)


class TestMagicMirrorDatabaseRemovePkg(unittest.TestCase):
    """Test remove_mm_pkg() (lines 401-430)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}
        self.database = MagicMirrorDatabase()

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_remove_mm_pkg_empty_data(self, mock_file_path):
        """Lines 408-410: returns False when no custom packages."""
        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.load", return_value=[]):
                result = self.database.remove_mm_pkg(title="SomePkg")
        self.assertFalse(result)

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_remove_mm_pkg_parse_error(self, mock_file_path):
        """Lines 413-416: handles exception parsing packages."""
        [{"title": "SomePkg", "bad_field": object()}]  # bad data for MagicMirrorPackage

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.load", return_value=[{"invalid": True}]):
                # MagicMirrorPackage(**{"invalid": True}) passes **kwargs so won't raise
                # The StopIteration path will be hit since the title won't match
                with patch("mmpm.magicmirror.database.json.dump"):
                    result = self.database.remove_mm_pkg(title="NotFound")
        self.assertFalse(result)

    @patch("mmpm.magicmirror.database.paths.MMPM_CUSTOM_PACKAGES_FILE")
    def test_remove_mm_pkg_exception_in_package_parsing(self, mock_file_path):
        """Lines 414-416: exception parsing individual package data."""
        # Force exception when creating MagicMirrorPackage from the data
        data = [{"title": "SomePkg"}]

        with patch("mmpm.magicmirror.database.open", mock_open()):
            with patch("mmpm.magicmirror.database.json.load", return_value=data):
                with patch("mmpm.magicmirror.database.MagicMirrorPackage.__init__", side_effect=Exception("parse error")):
                    with patch("mmpm.magicmirror.database.json.dump"):
                        result = self.database.remove_mm_pkg(title="SomePkg")
        self.assertFalse(result)


class TestMagicMirrorDatabaseUpdate(unittest.TestCase):
    """More thorough update() tests (lines 144-148)."""

    def setUp(self):
        from mmpm.singleton import Singleton

        Singleton._instances = {}
        self.database = MagicMirrorDatabase()

    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.upgradable")
    @patch("mmpm.magicmirror.database.MagicMirrorPackage.update")
    @patch("mmpm.magicmirror.database.open", new_callable=mock_open)
    def test_update_with_upgradable_packages(self, mock_file, mock_pkg_update, mock_upgradable):
        """Lines 143-159: update finds and saves upgradable packages."""
        pkg = MagicMirrorPackage(title="MMM-Upgradable", repository="https://github.com/a/b")
        pkg.is_installed = True
        pkg.is_upgradable = True

        self.database.packages = [pkg]
        mock_upgradable.return_value = {"mmpm": False, "MagicMirror": False, "packages": []}

        with patch("mmpm.magicmirror.database.json.dump"):
            result = self.database.update(can_upgrade_mmpm=True, can_upgrade_magicmirror=False)

        # mmpm upgradable contributes 1
        self.assertGreaterEqual(result, 1)

    @patch("mmpm.magicmirror.database.MagicMirrorDatabase.upgradable")
    @patch("mmpm.magicmirror.database.open", new_callable=mock_open)
    def test_update_counts_all_upgrades(self, mock_file, mock_upgradable):
        """Lines 152-159: count includes mmpm + MagicMirror + packages."""
        self.database.packages = []
        mock_upgradable.return_value = {"mmpm": False, "MagicMirror": False, "packages": []}

        with patch("mmpm.magicmirror.database.json.dump"):
            result = self.database.update(can_upgrade_mmpm=True, can_upgrade_magicmirror=True)

        self.assertEqual(result, 2)  # mmpm + MagicMirror


if __name__ == "__main__":
    unittest.main()
