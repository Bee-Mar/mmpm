#!/usr/bin/env python3
import os
import logging
import logging.handlers
from mmpm.consts import MMPM_CLI_LOG_FILE, MMPM_LOG_DIR

class MMPMLogger():
    '''
    Object used for logging while MMPM is executing.
    Log files can be found in ~/.config/mmpm/log
    '''

    __logger__ = None

    @staticmethod
    def __init_logger__(name: str):
        if not os.path.exists(MMPM_LOG_DIR):
            os.system(f'mkdir -p {MMPM_LOG_DIR}')

        os.system(f'touch {MMPM_CLI_LOG_FILE}')

        log_format: str = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s'
        logging.basicConfig(filename=MMPM_CLI_LOG_FILE, format=log_format)
        MMPMLogger.__logger__ = logging.getLogger(name)

        MMPMLogger.__logger__.setLevel(getattr(logging, os.getenv("MMPM_LOG_LEVEL", "INFO").upper()))

        handler = logging.handlers.RotatingFileHandler(
            MMPM_CLI_LOG_FILE,
            mode='a',
            maxBytes=1024*1024,
            backupCount=2,
            encoding=None,
            delay=0
        )

        MMPMLogger.__logger__.addHandler(handler)

    @staticmethod
    def get_logger(name: str):
        if MMPMLogger.__logger__ is None:
            MMPMLogger.__init_logger__(name)

        return MMPMLogger.__logger__

