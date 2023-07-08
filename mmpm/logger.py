#!/usr/bin/env python3
from mmpm.env import MMPMEnv
from mmpm.constants import paths, symbols, color
from mmpm.__version__ import version

import os
import sys
import shutil
import logging
import logging.handlers
import datetime
from typing import List


class StdOutMessageWriter:
    def __init__(self):
        pass

    def info(self, msg: str) -> None:
        """
        Prints message 'msg' without a new line

        Parameters:
            msg (str): The message to be printed to stdout

        Returns:
            None
        """
        sys.stdout.write(msg)
        sys.stdout.flush()

    def error(self, msg: str) -> None:
        """
        Logs error message, displays error message to user, and continues program execution

        Parameters:
            msg (str): The error message to be printed to stdout

        Returns:
            None
        """
        print(color.b_red("ERROR:"), msg)

    def warning(self, msg: str) -> None:
        """
        Logs warning message, displays warning message to user, and continues program execution

        Parameters:
            msg (str): The warning message to be printed to stdout

        Returns:
            None
        """
        print(color.b_yellow("WARNING:"), msg)

    def fatal(self, msg: str) -> None:
        """
        Logs fatal message, displays fatal message to user, and halts program execution

        Parameters:
            msg (str): The fatal error message to be printed to stdout

        Returns:
            None
        """
        print(color.b_red("FATAL:"), msg)
        sys.exit(127)

    def retrieving(self, url: str, name: str):
        print(f"Retrieving: {url} [{color.n_cyan(name)}] ")


class MMPMLogger:
    """
    Object used for logging while MMPM is executing.
    Log files can be found in ~/.config/mmpm/log
    """

    __logger__: logging.Logger = None

    @staticmethod
    def __init_logger__(name: str) -> None:
        log_format: str = f'{{"time": "%(asctime)s", "version": "{version}" , "level": "%(levelname)s", "location": "%(module)s:%(funcName)s:%(lineno)d", "message": "%(message)s"}}'
        logging.basicConfig(
                filename=paths.MMPM_CLI_LOG_FILE, format=log_format, datefmt="%Y-%m-%d %H:%M:%S"
                )

        MMPMLogger.__logger__ = logging.getLogger(name)
        MMPMLogger.__logger__.__setattr__("msg", StdOutMessageWriter())

        if not MMPMLogger.__logger__.hasHandlers():
            handler = logging.handlers.RotatingFileHandler(
                    paths.MMPM_CLI_LOG_FILE,
                    mode="a",
                    maxBytes=1024 * 1024,
                    backupCount=2,
                    encoding="utf-8",
                    delay=0,
                    )

            MMPMLogger.__logger__.addHandler(handler)

        MMPMLogger.__logger__.setLevel(MMPMEnv().mmpm_log_level.get())

        return MMPMLogger.__logger__

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return MMPMLogger.__init_logger__(name)

    @classmethod
    def display(cls, cli_logs: bool = False, gui_logs: bool = False, tail: bool = False) -> None:
        """
        Displays contents of log files to stdout. If the --tail option is supplied,
        log contents will be displayed in real-time

        Parameters:
            cli_logs (bool): if True, the CLI log files will be displayed
        gui_logs (bool): if True, the Gunicorn log files for the web interface will be displayed
        tail (bool): if True, the contents will be displayed in real time

        Returns:
            None
        """
        logs: List[str] = []

        if cli_logs:
            if paths.MMPM_CLI_LOG_FILE.exists():
                logs.append(str(paths.MMPM_CLI_LOG_FILE))
            else:
                MMPMLogger.msg.error("MMPM log file not found")

        if gui_logs:
            if paths.MMPM_NGINX_ACCESS_LOG_FILE.exists():
                logs.append(str(paths.MMPM_NGINX_ACCESS_LOG_FILE))
            else:
                MMPMLogger.msg.error("Gunicorn access log file not found")
            if paths.MMPM_NGINX_ERROR_LOG_FILE.exists():
                logs.append(str(paths.MMPM_NGINX_ERROR_LOG_FILE))
            else:
                MMPMLogger.msg.error("Gunicorn error log file not found")

        if logs:
            os.system(f"{'tail -F' if tail else 'cat'} {' '.join(logs)}")

    @classmethod
    def zip(cls) -> None:
        """
        Compresses all log files in ~/.config/mmpm/log. The NGINX log files are
        excluded due to mostly irrelevant information the user, or I would need
        when creating GitHub issues

        Parameters:
            None

        Returns:
            None
        """
        today = datetime.datetime.now()

        file_name: str = f"mmpm-logs-{today.year}-{today.month}-{today.day}"
        MMPMLogger.__logger__.msg.info(f"Compressing MMPM log files to {os.getcwd()}/{file_name}.zip ")

        try:
            shutil.make_archive(file_name, "zip", paths.MMPM_LOG_DIR)
        except Exception as error:
            print(symbols.RED_X)
            MMPMLogger.__logger__.msg.error(str(error))
            MMPMLogger.__logger__.msg.error("Failed to create zip archive of log files. See `mmpm log` for details (I know...the irony)")
            return

        print(symbols.GREEN_CHECK_MARK)
