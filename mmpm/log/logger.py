#!/usr/bin/env python3
import datetime
import json
import logging
import logging.handlers
import os
import shutil
from threading import Lock
from typing import List

import socketio

from mmpm.__version__ import version
from mmpm.constants import paths
from mmpm.env import MMPMEnv


class JsonFormatter(logging.Formatter):
    def format(self, record):
        try:
            message = record.getMessage()
        except TypeError:
            # Handling the case where formatting fails
            message = {"raw_message": record.msg, "args": record.args}

        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "version": version,
            "message": message,
            "logger_name": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        return json.dumps(log_data, ensure_ascii=False)


class SocketIOHandler(logging.Handler):
    """A logging handler that emits records with SocketIO."""

    def __init__(self, host, port):
        super().__init__()
        self.formatter = JsonFormatter()
        self.sio = socketio.Client()

        try:
            self.sio.connect(f"http://{host}:{port}", wait=False)
        except socketio.exceptions.ConnectionError:
            pass

    def emit(self, record):
        if self.sio.connected:
            try:
                self.sio.emit("logs", self.formatter.format(record))
            except Exception:
                pass

    def close(self):
        if self.sio.connected:
            self.sio.disconnect()
            super().close()


class StdoutFormatter(logging.Formatter):
    def format(self, record):
        label = "+" if record.levelname == "INFO" else record.levelname

        return f"[{label}] {record.getMessage()}"


class MMPMLogger:
    """
    Object used for logging while MMPM is executing.
    Log files can be found in ~/.config/mmpm/log
    """

    __logger: logging.Logger = None
    __socketio_handler: SocketIOHandler = None
    __lock: Lock = Lock()

    @staticmethod
    def __setup__(name: str) -> None:
        MMPMLogger.__logger = logging.getLogger(name)

        file_handler = logging.handlers.RotatingFileHandler(
            paths.MMPM_CLI_LOG_FILE,
            mode="a",
            maxBytes=1024 * 1024,
            backupCount=2,
            encoding="utf-8",
            delay=False,
        )

        level = MMPMEnv().MMPM_LOG_LEVEL.get()
        MMPMLogger.__logger.setLevel(logging.DEBUG)  # set the main logging handler set to the lowest level possible

        file_handler.setFormatter(JsonFormatter())
        file_handler.setLevel(logging.DEBUG)  # always have the log files be DEBUG
        MMPMLogger.__logger.addHandler(file_handler)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(StdoutFormatter())
        stdout_handler.setLevel(level)

        MMPMLogger.__logger.addHandler(stdout_handler)

        socketio_handler = SocketIOHandler("localhost", 6789)

        if socketio_handler.sio.connected:
            MMPMLogger.__socketio_handler = socketio_handler
            MMPMLogger.__socketio_handler.setLevel(logging.DEBUG)
            MMPMLogger.__logger.addHandler(MMPMLogger.__socketio_handler)
        else:
            MMPMLogger.__logger.debug("Failed to connect to SocketIO server")

    @staticmethod
    def shutdown() -> None:
        if MMPMLogger.__socketio_handler is not None:
            MMPMLogger.__logger.debug("Disconnecting from SocketIO server")
            MMPMLogger.__socketio_handler.close()

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        if MMPMLogger.__logger is None:
            with MMPMLogger.__lock:
                if MMPMLogger.__logger is None:
                    MMPMLogger.__setup__(name)

        return MMPMLogger.__logger

    @classmethod
    def display(cls, cli_logs: bool = False, ui_logs: bool = False, tail: bool = False) -> None:
        """
        Displays contents of log files to stdout. If the --tail option is supplied,
        log contents will be displayed in real-time

        Parameters:
            cli_logs (bool): if True, the CLI log files will be displayed
        ui_logs (bool): if True, the Gunicorn log files for the web interface will be displayed
        tail (bool): if True, the contents will be displayed in real time

        Returns:
            None
        """
        logs: List[str] = []

        if cli_logs:
            if paths.MMPM_CLI_LOG_FILE.exists():
                logs.append(str(paths.MMPM_CLI_LOG_FILE))
            else:
                MMPMLogger.__logger.error("MMPM log file not found")

        if ui_logs:
            if paths.MMPM_NGINX_ACCESS_LOG_FILE.exists():
                logs.append(str(paths.MMPM_NGINX_ACCESS_LOG_FILE))
            else:
                MMPMLogger.__logger.error("Gunicorn access log file not found")
            if paths.MMPM_NGINX_ERROR_LOG_FILE.exists():
                logs.append(str(paths.MMPM_NGINX_ERROR_LOG_FILE))
            else:
                MMPMLogger.__logger.error("Gunicorn error log file not found")

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

        try:
            shutil.make_archive(file_name, "zip", paths.MMPM_LOG_DIR)
        except Exception as error:
            MMPMLogger.__logger.error(f"{error}")
            return

        MMPMLogger.__logger.info(f"Compressed MMPM log files to {os.getcwd()}/{file_name}.zip ")
