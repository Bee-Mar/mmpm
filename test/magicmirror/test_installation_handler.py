#!/usr/bin/env python3

import unittest
from multiprocessing import cpu_count
from pathlib import Path
from unittest.mock import MagicMock, patch

from mmpm.magicmirror.package import InstallationHandler, MagicMirrorPackage


class TestInstallationHandler(unittest.TestCase):
    def setUp(self):
        self.mock_package = MagicMock(spec=MagicMirrorPackage)
        self.handler = InstallationHandler(self.mock_package)

    def test_constructor(self):
        self.assertEqual(self.handler.package, self.mock_package)

    @patch("os.chdir")
    @patch("os.system")
    def test_install_with_no_modules_dir(self, mock_system, mock_chdir):
        self.mock_package.env.MMPM_MAGICMIRROR_ROOT.get.return_value = Path("/invalid/root")
        self.mock_package.directory = "test_dir"

        result = self.handler.install()

        self.assertFalse(result)
        mock_chdir.assert_not_called()
        mock_system.assert_not_called()

    @patch("pathlib.Path.exists")
    def test_deps_file_exists(self, mock_exists):
        mock_exists.return_value = False
        file_name = "garbage"
        result = self.handler.exists(file_name)
        self.assertFalse(result)

    @patch("pathlib.Path.exists")
    def test_deps_file_exists(self, mock_exists):
        mock_exists.return_value = True
        file_name = "package.json"
        result = self.handler.exists(file_name)
        self.assertTrue(result)

    @patch("mmpm.magicmirror.package.run_cmd")
    def test_bundle_install(self, mock_run_cmd):
        mock_run_cmd.return_value = (0, "stdout", "stderr")
        error_code, stdout, stderr = self.handler.bundle_install()

        self.assertEqual(error_code, 0)
        self.assertEqual(stdout, "stdout")
        self.assertEqual(stderr, "stderr")
        mock_run_cmd.assert_called_with(["bundle", "install"], message="Installing Ruby dependencies")

    @patch("mmpm.magicmirror.package.run_cmd")
    def test_npm_install(self, mock_run_cmd):
        mock_run_cmd.return_value = (0, "stdout", "stderr")
        error_code, stdout, stderr = self.handler.npm_install()

        self.assertEqual(error_code, 0)
        self.assertEqual(stdout, "stdout")
        self.assertEqual(stderr, "stderr")
        mock_run_cmd.assert_called_with(["npm", "install"], message="Installing Node dependencies")

    @patch("mmpm.magicmirror.package.run_cmd")
    @patch("os.cpu_count", return_value=4)
    def test_make(self, mock_cpu_count, mock_run_cmd):
        mock_run_cmd.return_value = (0, "stdout", "stderr")
        error_code, stdout, stderr = self.handler.make()

        self.assertEqual(error_code, 0)
        self.assertEqual(stdout, "stdout")
        self.assertEqual(stderr, "stderr")
        mock_run_cmd.assert_called_with(["make", "-j", f"{cpu_count()}"], message="Building with 'make'")

    @patch("mmpm.magicmirror.package.run_cmd")
    def test_pip_install(self, mock_run_cmd):
        mock_run_cmd.return_value = (0, "stdout", "stderr")
        error_code, stdout, stderr = self.handler.pip_install()

        self.assertEqual(error_code, 0)
        self.assertEqual(stdout, "stdout")
        self.assertEqual(stderr, "stderr")
        mock_run_cmd.assert_called_with(
            ["pip", "install", "-r", "requirements.txt"],
            message="Installing Python dependencies",
        )

    @patch("mmpm.magicmirror.package.run_cmd")
    def test_maven_install(self, mock_run_cmd):
        mock_run_cmd.return_value = (0, "stdout", "stderr")
        error_code, stdout, stderr = self.handler.maven_install()

        self.assertEqual(error_code, 0)
        self.assertEqual(stdout, "stdout")
        self.assertEqual(stderr, "stderr")
        mock_run_cmd.assert_called_with(["mvn", "install"], message="Building with Maven")

    @patch("mmpm.magicmirror.package.run_cmd")
    def test_go_build(self, mock_run_cmd):
        mock_run_cmd.return_value = (0, "stdout", "stderr")
        error_code, stdout, stderr = self.handler.go_build()

        self.assertEqual(error_code, 0)
        self.assertEqual(stdout, "stdout")
        self.assertEqual(stderr, "stderr")
        mock_run_cmd.assert_called_with(["go", "build"], message="Building Go project")

    @patch("mmpm.magicmirror.package.run_cmd")
    @patch("os.chdir")
    @patch("os.system")
    @patch("pathlib.Path.mkdir")
    def test_cmake(self, mock_mkdir, mock_system, mock_chdir, mock_run_cmd):
        mock_run_cmd.return_value = (0, "stdout", "stderr")
        build_dir = Path("fake/dir/build")
        self.mock_package.directory = Path("fake/dir")

        mock_mkdir.return_value = build_dir
        error_code, stdout, stderr = self.handler.cmake()

        self.assertEqual(error_code, 0)
        self.assertEqual(stdout, "stdout")
        self.assertEqual(stderr, "stderr")

        mock_mkdir.assert_called_with(exist_ok=True)
        mock_system.assert_called_with(f"rm -rf {build_dir}/*")
        mock_chdir.assert_called_with(build_dir)
        mock_run_cmd.assert_called_with(["cmake", ".."], message="Building with CMake")
