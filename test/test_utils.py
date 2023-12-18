#!/usr/bin/env python3
import json
import os
import unittest
from pathlib import Path, PosixPath
from shutil import rmtree
from subprocess import DEVNULL
from unittest.mock import MagicMock, mock_open, patch
from uuid import uuid4

import requests
from faker import Faker

from mmpm.__version__ import major, version
from mmpm.utils import get_host_ip, get_pids, kill_pids_of_process, run_cmd, safe_get_request, update_available

fake = Faker()


class TestUtils(unittest.TestCase):
    @patch("mmpm.utils.socket.socket")
    def test_get_host_ip(self, mock_socket):
        ip = fake.ipv4()
        mock_socket.return_value.getsockname.return_value = (ip, 80)
        host_ip = get_host_ip()
        self.assertEqual(host_ip, ip)

    @patch("mmpm.utils.subprocess.Popen")
    @patch("mmpm.utils.yaspin")
    def test_run_cmd_progress(self, mock_yaspin, mock_popen):
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"output", b"error")
        process_mock.returncode = 0
        mock_popen.return_value.__enter__.return_value = process_mock
        return_code, stdout, stderr = run_cmd(["echo", "hello"], progress=True)

        self.assertEqual(return_code, 0)
        self.assertEqual(stdout, "output")
        self.assertEqual(stderr, "error")

    @patch("mmpm.utils.subprocess.Popen")
    def test_run_cmd_no_progress(self, mock_popen):
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"output", b"error")
        process_mock.returncode = 0
        mock_popen.return_value.__enter__.return_value = process_mock
        return_code, stdout, stderr = run_cmd(["echo", "hello"], progress=False)

        self.assertEqual(return_code, 0)
        self.assertEqual(stdout, "output")
        self.assertEqual(stderr, "error")

    @patch("mmpm.utils.subprocess.Popen")
    def test_get_pids(self, mock_popen):
        random_proccess_ids = [str(fake.pyint()), str(fake.pyint())]
        mock_process = mock_popen.return_value
        mock_process.__enter__.return_value.communicate.return_value = (
            bytes("\n".join(random_proccess_ids), "utf-8"),
            b"",
        )
        process_name = "my_process"
        pids = get_pids(process_name)
        self.assertEqual(pids, random_proccess_ids)

    @patch("mmpm.utils.os.system")
    def test_kill_pids_of_process(self, mock_system):
        process_name = fake.pystr()
        kill_pids_of_process(process_name)
        mock_system.assert_called_with(f"for process in $(pgrep {process_name}); do kill -9 $process; done")

    @patch("mmpm.utils.requests.get")
    def test_safe_get_request_success(self, mock_get):
        mock_response = mock_get.return_value
        data = safe_get_request(fake.url())
        self.assertEqual(data, mock_response)

    @patch("mmpm.utils.requests.get", side_effect=requests.exceptions.RequestException)
    def test_safe_get_request_failure(self, mock_get):
        data = safe_get_request(fake.url())
        self.assertIsInstance(data, requests.Response)

    @patch("mmpm.utils.urllib.request.urlopen")
    def test_no_update_available(self, mock_urlopen):
        latest_version_data = {"info": {"version": version}}

        mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=json.dumps(latest_version_data)))
        self.assertFalse(update_available())

    @patch("mmpm.utils.urllib.request.urlopen")
    def test_update_available(self, mock_urlopen):
        latest_version_data = {"info": {"version": f"{major + 1}.0.0"}}

        mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=json.dumps(latest_version_data)))
        self.assertTrue(update_available())


if __name__ == "__main__":
    unittest.main()
