#!/usr/bin/env python3
import os
import unittest
from pathlib import PosixPath
from unittest.mock import patch

import requests
from faker import Faker
from mmpm.utils import (get_host_ip, get_pids, kill_pids_of_process, prompt,
                        run_cmd, safe_get_request, systemctl, validate_input)

fake = Faker()


class TestUtils(unittest.TestCase):
    @patch("mmpm.utils.socket.socket")
    def test_get_host_ip(self, mock_socket):
        ip = fake.ipv4()
        mock_socket.return_value.getsockname.return_value = (ip, 80)
        host_ip = get_host_ip()
        self.assertEqual(host_ip, ip)

    # @patch('mmpm.utils.subprocess.Popen') # FIXME
    # def test_run_cmd(self, mock_popen):
    #    mock_process = mock_popen.return_value
    #    mock_process.poll.return_value = None
    #    mock_process.returncode = 0
    #    mock_stdout = bytes(fake.pystr(), "utf-8")
    #    mock_stderr = bytes(fake.pystr(), "utf-8")
    #    mock_process.communicate.return_value = (mock_stdout, mock_stderr)
    #    returncode, stdout, stderr = run_cmd(['ls', '-l'], progress=False)
    #    self.assertEqual(mock_process.returncode, 0)
    #    self.assertEqual(stdout, mock_stdout.decode("utf-8"))
    #    self.assertEqual(stderr, mock_stderr.decode("utf-8"))

    @patch("mmpm.utils.subprocess.Popen")
    def test_get_pids(self, mock_popen):
        random_proccess_ids = [str(fake.pyint()), str(fake.pyint())]
        mock_process = mock_popen.return_value
        mock_process.__enter__.return_value.communicate.return_value = (bytes("\n".join(random_proccess_ids), "utf-8"), b"")
        process_name = "my_process"
        pids = get_pids(process_name)
        self.assertEqual(pids, random_proccess_ids)

    @patch("mmpm.utils.os.system")
    def test_kill_pids_of_process(self, mock_system):
        process_name = fake.pystr()
        kill_pids_of_process(process_name)
        mock_system.assert_called_with(f"for process in $(pgrep {process_name}); do kill -9 $process; done")

    @patch("builtins.input")
    def test_prompt_valid_ack(self, mock_input):
        mock_input.return_value = "yes"
        response = prompt("Continue?", valid_ack=["yes", "y"], valid_nack=["no", "n"])
        self.assertTrue(response)

    @patch("builtins.input")
    def test_prompt_valid_nack(self, mock_input):
        mock_input.return_value = "no"
        response = prompt("Continue?", valid_ack=["yes", "y"], valid_nack=["no", "n"])
        self.assertFalse(response)

    @patch("builtins.input", side_effect=["maybe", "yes"])
    def test_prompt_invalid_response(self, mock_input):
        response = prompt("Continue?", valid_ack=["yes", "y"], valid_nack=["no", "n"])
        self.assertTrue(response)

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_prompt_keyboard_interrupt(self, mock_input):
        response = prompt("Continue?", valid_ack=["yes", "y"], valid_nack=["no", "n"])
        self.assertFalse(response)

    @patch("builtins.input")
    def test_validate_input_valid_response(self, mock_input):
        user_input = fake.pystr()
        mock_input.return_value = user_input
        user_response = validate_input("Enter a response: ", forbidden_responses=["invalid"], reason="is not allowed")
        self.assertEqual(user_response, user_input)

    @patch("builtins.input", side_effect=["", "invalid", "response"])
    def test_validate_input_invalid_response(self, mock_input):
        user_response = validate_input("Enter a response: ", forbidden_responses=["invalid"], reason="is not allowed")
        self.assertEqual(user_response, "response")

    @patch("mmpm.utils.requests.get")
    def test_safe_get_request_success(self, mock_get):
        mock_response = mock_get.return_value
        data = safe_get_request(fake.url())
        self.assertEqual(data, mock_response)

    @patch("mmpm.utils.requests.get", side_effect=requests.exceptions.RequestException)
    def test_safe_get_request_failure(self, mock_get):
        data = safe_get_request(fake.url())
        self.assertIsInstance(data, requests.Response)

    @patch("mmpm.utils.subprocess.run")
    def test_systemctl(self, mock_run):
        mock_process = mock_run.return_value
        subcommand = fake.pystr()
        services = [fake.pystr(), fake.pystr()]
        process = systemctl(subcommand, services)
        self.assertEqual(process, mock_process)


if __name__ == "__main__":
    unittest.main()
