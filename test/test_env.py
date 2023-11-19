#!/usr/bin/env python3
from mmpm.singleton import Singleton
from mmpm.env import MMPMEnv, EnvVar, MMPM_DEFAULT_ENV

from faker import Faker

import unittest
import random
from pathlib import Path, PosixPath
from unittest.mock import patch, mock_open


fake = Faker()


class TestEnvVar(unittest.TestCase):
    def test_get_existing_variable(self):
        var = random.choice([key for key in MMPM_DEFAULT_ENV])
        default_value = MMPM_DEFAULT_ENV[var]
        random_value = None

        if isinstance(default_value, PosixPath):
            random_value = Path("/tmp") / fake.pystr() / "MagicMirror"
        elif isinstance(default_value, str):
            random_value = fake.pystr()
        elif isinstance(default_value, bool):
            random_value = fake.pybool()

        env_var = EnvVar(name=var, default=default_value, tipe=type(default_value))

        with patch("builtins.open", mock_open(read_data=f'{{"{var}": "{random_value}"}}')):
            value = env_var.get()

        self.assertEqual(value, random_value)

    def test_get_nonexistent_variable_with_default(self):
        env_var = EnvVar(name="MMPM_NONEXISTENT_VAR", default=fake.pystr(), tipe=str)

        with patch("builtins.open", mock_open(read_data="{}")):
            value = env_var.get()
            self.assertEqual(value, env_var.default)


class TestMMPMEnv(unittest.TestCase):
    def setUp(self):
        Singleton._instances = {}

    def test_singleton_instance(self):
        env1 = MMPMEnv()
        env2 = MMPMEnv()
        self.assertIs(env1, env2)


if __name__ == "__main__":
    unittest.main()
