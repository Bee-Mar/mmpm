#!/usr/bin/env python3

import mmpm.consts
import json
from mmpm_test import pre_test_setup

with open(mmpm.consts.MMPM_ENV_FILE, "w") as env:
    json.dump(pre_test_setup.ORIGINAL_ENV, env, indent=2)
