#!/usr/bin/env python3
import json
import random
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from faker import Faker

from mmpm.env import MMPM_DEFAULT_ENV, EnvVar, MMPMEnv
from mmpm.singleton import Singleton

fake = Faker()


class TestEnvVar(unittest.TestCase):
    def setUp(self):
        self.key = random.choice([key for key in MMPM_DEFAULT_ENV])
        self.default_value = MMPM_DEFAULT_ENV[self.key]

    def generate_random_value(self, value_type):
        if isinstance(value_type, Path):
            return Path("/tmp") / fake.file_path()
        elif isinstance(value_type, str):
            return fake.pystr()
        elif isinstance(value_type, bool):
            return fake.pybool()

    @patch("mmpm.env.open", new_callable=mock_open)
    def test_get_existing_variable(self, mock_file):
        random_value = self.generate_random_value(self.default_value)
        env_var = EnvVar(name=self.key, default=self.default_value)

        primitive = random_value if isinstance(random_value, bool) else str(random_value)
        mock_file.return_value.read.return_value = json.dumps({self.key: primitive})

        self.assertEqual(env_var.get(), random_value)

    def test_get_nonexistent_variable_with_default(self):
        env_var = EnvVar(name="MMPM_NONEXISTENT_VAR", default=fake.pystr())

        with patch("mmpm.env.open", mock_open(read_data="{}")):
            value = env_var.get()
            self.assertEqual(value, env_var.default)

    @patch("mmpm.env.open", new_callable=mock_open)
    def test_modified_file_detection(self, mock_file):
        env_var = EnvVar(name=self.key, default=self.default_value)
        new_value = self.generate_random_value(self.default_value)

        primitive = new_value if isinstance(new_value, bool) else str(new_value)
        mock_file.return_value.read.return_value = json.dumps({self.key: primitive})

        with patch("mmpm.env.getmtime", return_value=12345):
            self.assertEqual(env_var.get(), new_value)


class TestMMPMEnv(unittest.TestCase):
    def setUp(self):
        Singleton._instances = {}

    def test_singleton_instance(self):
        env1 = MMPMEnv()
        env2 = MMPMEnv()
        self.assertIs(env1, env2)

    def test_environment_variable_loading(self):
        env = MMPMEnv()
        self.assertIsInstance(env.MMPM_MAGICMIRROR_ROOT, EnvVar)
        self.assertIsInstance(env.MMPM_MAGICMIRROR_URI, EnvVar)
        # Test other environment variables similarly

    def test_environment_variable_update(self):
        env = MMPMEnv()
        new_uri = "http://example.com:8080"
        with patch(
            "mmpm.env.open",
            mock_open(read_data=json.dumps({"MMPM_MAGICMIRROR_URI": new_uri})),
        ):
            self.assertEqual(env.MMPM_MAGICMIRROR_URI.get(), new_uri)

    def test_environment_file_error_handling(self):
        with patch("mmpm.env.open", mock_open(read_data="{invalid_json")):
            env = MMPMEnv()
            # Test default values are used in case of JSON error
            self.assertEqual(
                env.MMPM_MAGICMIRROR_ROOT.get(),
                MMPM_DEFAULT_ENV["MMPM_MAGICMIRROR_ROOT"],
            )


if __name__ == "__main__":
    unittest.main()
