#!/usr/bin/env python3
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from faker import Faker

from mmpm.env import MMPM_DEFAULT_ENV, MMPMEnv
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
        package1 = MagicMirrorPackage(
            title="Test Title",
            repository="https://example.com/repo.git",
            directory="same",
        )
        package2 = MagicMirrorPackage(
            title="Test Title",
            repository="https://example.com/repo.git",
            directory="same",
        )
        package3 = MagicMirrorPackage(
            title="Different Title",
            repository="https://example.com/repo.git",
            directory="different",
        )

        self.assertTrue(package1 == package2)
        self.assertFalse(package1 == package3)

    def test_inequality(self):
        package1 = MagicMirrorPackage(
            title="Test Title",
            repository="https://example.com/repo.git",
            directory="different",
        )
        package2 = MagicMirrorPackage(
            title="Different Title",
            repository="https://example.com/repo.git",
            directory="more-different",
        )

        self.assertTrue(package1 != package2)

    @patch("mmpm.magicmirror.package.InstallationHandler")
    def test_install(self, mock_handler):
        mock_install = MagicMock()
        mock_handler.return_value = mock_install
        self.package.is_installed = False
        self.package.install()
        mock_install.install.assert_called_once()

    @patch("mmpm.magicmirror.package.run_cmd")
    def test_remove(self, mock_run_cmd):
        self.package.env = MMPMEnv()
        mock_run_cmd.return_value = (0, "", "")
        success = self.package.remove()
        self.assertTrue(success)
        mock_run_cmd.assert_called()

    @patch("mmpm.magicmirror.package.run_cmd")
    def test_clone(self, mock_run_cmd):
        modules = MMPM_DEFAULT_ENV.get("MMPM_MAGICMIRROR_ROOT") / "modules"
        self.package.env = MMPMEnv()
        self.package.clone()
        mock_run_cmd.assert_called_with(
            [
                "git",
                "clone",
                self.package.repository,
                str(modules / self.package.directory),
            ],
            message="Downloading",
        )

    @patch("os.chdir")
    @patch("mmpm.magicmirror.package.repo_up_to_date")
    @patch("pathlib.PosixPath.exists")
    def test_update(self, mock_exists, mock_repo_up_to_date, mock_chdir):
        mock_exists.return_value = True
        mock_repo_up_to_date.return_value = True
        self.package.env = MMPMEnv()
        expected_dir = MMPM_DEFAULT_ENV.get("MMPM_MAGICMIRROR_ROOT") / "modules" / self.package.directory
        self.package.update()
        mock_chdir.assert_called_with(expected_dir)
        self.assertTrue(self.package.is_upgradable)

    @patch("os.chdir")
    @patch("mmpm.magicmirror.package.repo_up_to_date")
    @patch("pathlib.PosixPath.exists")
    def test_update_no_changes(self, mock_exists, mock_repo_up_to_date, mock_chdir):
        mock_repo_up_to_date.return_value = False
        self.package.env = MMPMEnv()
        expected_dir = MMPM_DEFAULT_ENV.get("MMPM_MAGICMIRROR_ROOT") / "modules" / self.package.directory
        self.package.update()
        mock_chdir.assert_called_with(expected_dir)
        self.assertFalse(self.package.is_upgradable)

    @patch("os.chdir")
    @patch("mmpm.magicmirror.package.run_cmd")
    @patch("mmpm.magicmirror.package.InstallationHandler.install")
    def test_upgrade(self, mock_install_install, mock_run_cmd, mock_chdir):
        mock_run_cmd.return_value = (0, "", "")
        self.package.env = MMPMEnv()
        expected_dir = MMPM_DEFAULT_ENV.get("MMPM_MAGICMIRROR_ROOT") / "modules" / self.package.directory
        self.package.is_upgradable = True
        self.package.upgrade()
        mock_chdir.assert_called_with(expected_dir)

    @patch("os.chdir")
    @patch("mmpm.magicmirror.package.run_cmd")
    def test_upgrade_failure(self, mock_run_cmd, mock_chdir):
        mock_run_cmd.return_value = (1, "", "error")
        expected_dir = MMPM_DEFAULT_ENV.get("MMPM_MAGICMIRROR_ROOT") / "modules" / self.package.directory
        self.package.env = MMPMEnv()
        result = self.package.upgrade()
        mock_chdir.assert_called_with(expected_dir)
        self.assertFalse(result)
