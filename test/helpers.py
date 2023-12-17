#!/usr/bin/env python3
from pathlib import Path
from unittest.mock import MagicMock

from pytest import fixture

from mmpm.env import EnvVar, MMPMEnv

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
        self.MMPM_MAGICMIRROR_ROOT = MutableMagicMock()
        self.MMPM_MAGICMIRROR_URI = MutableMagicMock()
        self.MMPM_MAGICMIRROR_PM2_PROCESS_NAME = MutableMagicMock()
        self.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE = MutableMagicMock()
        self.MMPM_IS_DOCKER_IMAGE = MutableMagicMock()
        self.mmpm_log_level = MutableMagicMock()

        self.MMPM_MAGICMIRROR_ROOT.get.return_value = Path("/tmp/MagicMirror")
        self.MMPM_MAGICMIRROR_URI.get.return_value = "http://localhost:8080"
        self.MMPM_MAGICMIRROR_PM2_PROCESS_NAME.get.return_value = ""
        self.MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE.get.return_value = ""
        self.MMPM_IS_DOCKER_IMAGE.get.return_value = False
        self.mmpm_log_level.get.return_value = "INFO"
