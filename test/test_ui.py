#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, mock_open, patch

from mmpm.ui import MMPMui


class TestMMPMui(unittest.TestCase):
    @patch("mmpm.ui.os.path.exists")
    @patch("mmpm.ui.open", new_callable=mock_open, read_data="listen 8080")
    @patch("mmpm.ui.findall")
    @patch("mmpm.ui.gethostbyname")
    @patch("mmpm.ui.gethostname")
    @patch("mmpm.ui.paths.MMPM_NGINX_CONF_FILE", "dummy/path/to/nginx.conf")
    @patch("mmpm.ui.logger")
    def test_get_uri(self, mock_logger, mock_gethostname, mock_gethostbyname, mock_findall, mock_file_open, mock_exists):
        # Set up mock returns
        mock_exists.return_value = True
        mock_findall.return_value = ["listen 8080"]
        mock_gethostname.return_value = "localhost"
        mock_gethostbyname.return_value = "127.0.0.1"

        # Create an instance of MMPMui and call get_uri
        gui = MMPMui()
        uri = gui.get_uri()

        # Assert that the URI is as expected
        self.assertEqual(uri, "http://127.0.0.1:8080")
