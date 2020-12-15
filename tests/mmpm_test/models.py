#!/usr/bin/env python3
import os
import logging
import logging.handlers
import mmpm_test.consts

class MMPMTestLogger():
    """
    Object used for logging while MMPM tests are executing.  Log files can be
    found in "/tmp/MMPM_TEST/log/mmpm-cli-interface.log"
    """

    def __init__(self):
        self.log_file: str = mmpm_test.consts.MMPM_CLI_LOG_FILE

        if not os.path.exists(mmpm_test.consts.MMPM_LOG_DIR):
            os.system(f"mkdir -p {mmpm_test.consts.MMPM_LOG_DIR}")

        os.system(f"touch {mmpm_test.consts.MMPM_CLI_LOG_FILE}")

        self.log_format: str = "%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s"
        logging.basicConfig(filename=self.log_file, format=self.log_format)
        logger: logging.Logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        self.handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            mode="a",
            maxBytes=1024*1024,
            backupCount=2,
            encoding=None,
            delay=0
        )

        logger.addHandler(self.handler)
        self.logger = logger
