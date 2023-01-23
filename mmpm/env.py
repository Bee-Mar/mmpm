#!/usr/bin/env python3
import json
import mmpm.consts
from mmpm.logger import MMPMLogger
from mmpm.consts import MMPM_DEFAULT_ENV

logger = MMPMLogger.get_logger(__name__)


def get_env(key: str) -> str:
    '''
    Reads environment variables from the MMPM_ENV_FILE. In order to ensure
    hot-reloading is usable in the GUI, the environment variables need to be
    re-read from the file each time. Otherwise, cached data will be sent back
    to the user.

    Parameters:
        None

    Returns:
        value (str): the value of the environment variable key
    '''

    value: str = ''

    if key not in MMPM_DEFAULT_ENV:
        logger.fatal(f"Environment variable '{key}' does is not valid.")


    with open(mmpm.consts.MMPM_ENV_FILE, 'r', encoding="utf-8") as env:
        env_vars = {}

        try:
            env_vars = json.load(env)
        except json.JSONDecodeError:
            logger.warning(f"Environment variable '{key}' does is not valid.")

        if key not in env_vars:
            print("HERE")
            logger.fatal(f"Value for {key} not in {mmpm.consts.MMPM_ENV_FILE}. Using default value.")
            value = MMPM_DEFAULT_ENV[key]
        else:
            value = env_vars.get(key)

    return value
