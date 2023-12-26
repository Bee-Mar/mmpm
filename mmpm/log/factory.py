#!/usr/bin/env python3
import datetime
import json
import logging
import logging.handlers
import os
import shutil
from threading import Lock

import socketio

from mmpm.__version__ import version
from mmpm.constants import paths
from mmpm.env import MMPMEnv


class JsonFormatter(logging.Formatter):
    """
    A custom formatter for logging, which outputs log records in a JSON format.
    """

    def format(self, record):
        """
        Formats the log record into JSON.

        Parameters:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: A JSON string representation of the log record.
        """

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
        """
        Initializes the SocketIOHandler with a specified host and port for the SocketIO server.

        Parameters:
            host (str): The host name of the SocketIO server.
            port (int): The port number of the SocketIO server.
        """

        super().__init__()
        self.formatter = JsonFormatter()
        self.sio = socketio.Client()

        try:
            self.sio.connect(f"http://{host}:{port}", wait=False)
        except socketio.exceptions.ConnectionError:
            pass

    def emit(self, record):
        """
        Emits the log record to the connected SocketIO server.

        Parameters:
            record (logging.LogRecord): The log record to be emitted.
        """

        if self.sio.connected:
            try:
                self.sio.emit("logs", self.formatter.format(record))
            except Exception:
                pass

    def close(self):
        """
        Closes the connection to the SocketIO server and performs any necessary cleanup.

        Parameters:
            None
        """

        if self.sio.connected:
            self.sio.disconnect()
            super().close()


class StdoutFormatter(logging.Formatter):
    """
    A custom formatter for logging, which outputs log records to stdout with a simplified format.
    """

    def format(self, record):
        """
        Formats the log record for stdout.

        Parameters:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: A string representation of the log record for stdout.
        """

        label = "+" if record.levelname == "INFO" else record.levelname

        return f"[{label}] {record.getMessage()}"


class MMPMLogFactory:
    """
    A custom logging class for MMPM, providing functionalities for logging to files, stdout, and SocketIO.
    Logs can be found in ~/.config/mmpm/log.
    """

    __logger: logging.Logger = None
    __socketio_handler: SocketIOHandler = None
    __lock: Lock = Lock()

    @staticmethod
    def __setup__(name: str) -> None:
        MMPMLogFactory.__logger = logging.getLogger(name)

        file_handler = logging.handlers.RotatingFileHandler(
            paths.MMPM_CLI_LOG_FILE,
            mode="a",
            maxBytes=1024 * 1024,
            backupCount=2,
            encoding="utf-8",
            delay=False,
        )

        level = MMPMEnv().MMPM_LOG_LEVEL.get()
        MMPMLogFactory.__logger.setLevel(logging.DEBUG)  # set the main logging handler set to the lowest level possible

        file_handler.setFormatter(JsonFormatter())
        file_handler.setLevel(logging.DEBUG)  # always have the log files be DEBUG
        MMPMLogFactory.__logger.addHandler(file_handler)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(StdoutFormatter())
        stdout_handler.setLevel(level)

        MMPMLogFactory.__logger.addHandler(stdout_handler)

        socketio_handler = SocketIOHandler("localhost", 6789)

        if socketio_handler.sio.connected:
            MMPMLogFactory.__socketio_handler = socketio_handler
            MMPMLogFactory.__socketio_handler.setLevel(logging.DEBUG)
            MMPMLogFactory.__logger.addHandler(MMPMLogFactory.__socketio_handler)
        else:
            MMPMLogFactory.__logger.debug("Failed to connect to SocketIO server")

    @staticmethod
    def shutdown() -> None:
        """
        Shuts down the logger, closing any SocketIO connections.

        Parameters:
            None
        """

        if MMPMLogFactory.__socketio_handler is not None:
            MMPMLogFactory.__logger.debug("Disconnecting from SocketIO server")
            MMPMLogFactory.__socketio_handler.close()

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Retrieves a logger instance with the given name, initializing it if necessary.

        Parameters:
            name (str): The name of the logger.

        Returns:
            logging.Logger: The logger instance associated with the given name.
        """

        if MMPMLogFactory.__logger is None:
            with MMPMLogFactory.__lock:
                if MMPMLogFactory.__logger is None:
                    MMPMLogFactory.__setup__(name)

        return MMPMLogFactory.__logger

    @classmethod
    def display(cls, tail: bool = False) -> None:
        """
        Displays contents of log files to stdout. If the tail option is supplied, log contents will be displayed in real-time.

        Parameters:
            tail (bool): If True, displays the log contents in real time.

        Returns:
            None
        """
        if paths.MMPM_CLI_LOG_FILE.exists():
            os.system(f"{'tail -F' if tail else 'cat'} {paths.MMPM_CLI_LOG_FILE}")
        else:
            MMPMLogFactory.__logger.error("MMPM log file not found")

    @classmethod
    def archive(cls) -> None:
        """
        Compresses all log files in ~/.config/mmpm/log, excluding NGINX logs.

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
            MMPMLogFactory.__logger.error(f"{error}")
            return

        MMPMLogFactory.__logger.info(f"Compressed MMPM log files to {os.getcwd()}/{file_name}.zip ")
