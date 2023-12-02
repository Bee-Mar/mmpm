#!/usr/bin/env python3
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from faker import Faker
from mmpm.env import MMPMEnv
from mmpm.magicmirror.package import MagicMirrorPackage, __sanitize__

fake = Faker()


class TestMagicMirrorPackage(unittest.TestCase):
    def setUp(self):
        self.env_mock = MagicMock(spec=MMPMEnv)
        self.package = MagicMirrorPackage(
            title=f"{fake.pystr()} // ",
            author=fake.pystr(),
            repository="https://github.com/test/repo.git",
            description=fake.pystr(),
            category=fake.pystr(),
            directory=fake.pystr(),
            is_installed=True,
        )
        self.package.env = self.env_mock

    def test_str_repr_methods(self):
        expected_str = str(self.package.serialize())
        self.assertEqual(str(self.package), expected_str)
        self.assertEqual(repr(self.package), expected_str)

    def test_serialize_full(self):
        serialized_data = self.package.serialize(full=True)
        self.assertTrue("is_installed" in serialized_data)
        self.assertTrue("is_upgradable" in serialized_data)

    def test_serialize_full(self):
        serialized_data = self.package.serialize()
        self.assertTrue("is_installed" not in serialized_data)
        self.assertTrue("is_upgradable" not in serialized_data)

    def test_equality(self):
        package1 = MagicMirrorPackage(title="Test Title", repository="https://example.com/repo.git", directory="same")
        package2 = MagicMirrorPackage(title="Test Title", repository="https://example.com/repo.git", directory="same")
        package3 = MagicMirrorPackage(title="Different Title", repository="https://example.com/repo.git", directory="different")

        self.assertTrue(package1 == package2)
        self.assertFalse(package1 == package3)

    def test_inequality(self):
        package1 = MagicMirrorPackage(title="Test Title", repository="https://example.com/repo.git", directory="different")
        package2 = MagicMirrorPackage(title="Different Title", repository="https://example.com/repo.git", directory="more-different")

        self.assertTrue(package1 != package2)

    @patch("mmpm.magicmirror.package.InstallationHandler")
    def test_install_already_installed(self, mock_handler):
        package = MagicMirrorPackage(is_installed=True)
        package.install()
        mock_handler.assert_not_called()

    @patch("mmpm.magicmirror.package.InstallationHandler")
    def test_install(self, mock_handler):
        package = MagicMirrorPackage(is_installed=False)
        mock_install = MagicMock()
        mock_handler.return_value = mock_install
        package.install(assume_yes=True)
        mock_install.execute.assert_called_once()

    @patch("mmpm.magicmirror.package.run_cmd")
    def test_remove(self, mock_run_cmd):
        package = MagicMirrorPackage(is_installed=True)
        package.remove(assume_yes=True)
        mock_run_cmd.assert_called()

    def test_remove_not_installed(self):
        package = MagicMirrorPackage(is_installed=False)
        with patch("mmpm.magicmirror.package.run_cmd") as mock_run_cmd:
            package.remove(assume_yes=True)
            mock_run_cmd.assert_not_called()

    # @patch("mmpm.magicmirror.package.run_cmd")
    # def test_clone(self, mock_run_cmd):
    #    package = MagicMirrorPackage(repository="https://example.com/repo.git")
    #    package.clone()
    #    mock_run_cmd.assert_called_with(["git", "clone", package.repository, str(package.directory)], message="Retrieving package")
