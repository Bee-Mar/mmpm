#!/usr/bin/env python3
from mmpm.env import MMPMEnv, EnvVar
from pathlib import Path
from unittest.mock import MagicMock
from pytest import fixture

# TODO: get this to work with the conftest.py for pytest
# not sure why using a helper fixture isn't working properly, but thats the
# easiest way to do it in the long run


class MutableMagicMock(MagicMock):
    def __setattribute__(self, name, value):
        if name == "get":
            self._mock_children[name] = value
        else:
            super().__setattribute__(name, value)


class MockedMMPMEnv(MMPMEnv):
    def __init__(self):
        super().__init__()

        # Mock the environment variables here
        self.mmpm_magicmirror_root = MutableMagicMock()
        self.MMPM_MAGICMIRROR_URI = MutableMagicMock()
        self.mmpm_magicmirror_pm2_process_name = MutableMagicMock()
        self.mmpm_magicmirror_docker_compose_file = MutableMagicMock()
        self.mmpm_is_docker_image = MutableMagicMock()
        self.mmpm_log_level = MutableMagicMock()

        self.mmpm_magicmirror_root.get.return_value = Path("/tmp/MagicMirror")
        self.MMPM_MAGICMIRROR_URI.get.return_value = "http://localhost:8080"
        self.mmpm_magicmirror_pm2_process_name.get.return_value = ""
        self.mmpm_magicmirror_docker_compose_file.get.return_value = ""
        self.mmpm_is_docker_image.get.return_value = False
        self.mmpm_log_level.get.return_value = "INFO"
