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

    @patch("mmpm.subcommands.loader.iter_modules")
    @patch("mmpm.subcommands.loader.import_module")
    @patch("mmpm.subcommands.loader.logger")
    def test_loader_with_app_name(self, mock_logger, mock_import_module, mock_iter_modules):
        """Lines 69-70: when app_name is provided, instance is created with app_name arg."""
        # submodule.name = "test_prefix_command"
        # prefix = "test_prefix_" → stripped name = "command"
        # snake_to_pascal("command") → "Command"
        mock_submodule = MagicMock()
        mock_submodule.name = "test_prefix_command"
        mock_iter_modules.return_value = [mock_submodule]

        FakeClass = MagicMock()
        FakeClass.return_value.name = "test_command"

        mock_module = MagicMock()
        mock_module.Command = FakeClass

        mock_import_module.return_value = mock_module

        Loader([], "module_name", "app_name", "test_prefix_")
        # When app_name is provided, objekt(app_name) is called
        FakeClass.assert_called_with("app_name")

    @patch("mmpm.subcommands.loader.iter_modules")
    @patch("mmpm.subcommands.loader.import_module")
    @patch("mmpm.subcommands.loader.logger")
    def test_loader_without_app_name(self, mock_logger, mock_import_module, mock_iter_modules):
        """Lines 69: when no app_name, instance is created without args."""
        mock_submodule = MagicMock()
        mock_submodule.name = "test_prefix_command"
        mock_iter_modules.return_value = [mock_submodule]

        FakeClass = MagicMock()
        FakeClass.return_value.name = "test_command"

        mock_module = MagicMock()
        mock_module.Command = FakeClass
        mock_import_module.return_value = mock_module

        Loader([], "module_name", "", "test_prefix_")
        # When no app_name, objekt() is called with no args
        FakeClass.assert_called_with()

    @patch("mmpm.subcommands.loader.iter_modules")
    @patch("mmpm.subcommands.loader.import_module")
    @patch("mmpm.subcommands.loader.logger")
    def test_loader_exception_logged(self, mock_logger, mock_import_module, mock_iter_modules):
        """Lines 71-72: exception during loading is logged as error."""
        mock_iter_modules.return_value = [MagicMock(name="test_prefix_failing")]
        mock_import_module.side_effect = AttributeError("missing attribute")

        loader = Loader([], "module_name", "", "test_prefix_")
        # The error should have been logged
        mock_logger.error.assert_called()
        # No objects loaded
        self.assertEqual(len(loader.objects), 0)
