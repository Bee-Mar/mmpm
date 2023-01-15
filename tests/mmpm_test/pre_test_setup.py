#!/usr/bin/env python3

import json
import mmpm.consts
import pathlib
import shutil

from logging import Logger
from mmpm_test import consts as test_consts
from mmpm_test.models import MMPMTestLogger

log: Logger = MMPMTestLogger().logger # type: ignore

log.info(f"Setting MMPM test environment with MMPM_MAGICMIRROR_ROOT as {test_consts.MAGICMIRROR_ROOT}")

ORIGINAL_ENV = {}

with open(mmpm.consts.MMPM_ENV_FILE, "r") as env:
    try:
        ORIGINAL_ENV = json.load(env)
    except json.JSONDecodeError as error:
        log.error(str(error))

with open(mmpm.consts.MMPM_ENV_FILE, "w") as env:
    json.dump(test_consts.MMPM_TEST_ENV, env, indent=2)

for required_dir in test_consts.REQUIRED_DIRS:
    shutil.rmtree(required_dir, ignore_errors=True)
    pathlib.Path(required_dir).mkdir(parents=True, exist_ok=True)

for required_file in test_consts.REQUIRED_FILES:
    pathlib.Path(required_file).touch(exist_ok=True)
