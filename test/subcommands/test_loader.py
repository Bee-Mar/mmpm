#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, patch

from mmpm.subcommands.loader import Loader


class TestLoader(unittest.TestCase):
    @patch("mmpm.subcommands.loader.iter_modules")
    @patch("mmpm.subcommands.loader.import_module")
    @patch("mmpm.subcommands.loader.logger")
    def test_loader_success(self, mock_logger, mock_import_module, mock_iter_modules):
        mock_iter_modules.return_value = [MagicMock(name="test_prefix_command")]

        FakeClass = MagicMock()
        FakeClass.return_value.name = "test_command"

        mock_import_module.return_value = MagicMock(TestPrefixCommand=FakeClass)

        loader = Loader([], "module_name", "app_name", "test_prefix_")
        loader.objects["test_command"] = FakeClass()

        self.assertIn("test_command", loader.objects)
        self.assertEqual(loader.objects["test_command"].name, "test_command")

    def test_loader_fail(self):
        loader = Loader([], "non_existent_python_module", "app_name", "test_prefix_")
        self.assertEqual(len(loader.objects.keys()), 0)
