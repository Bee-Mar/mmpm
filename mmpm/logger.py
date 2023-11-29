#!/usr/bin/env python3
import datetime
import json
import logging
import logging.handlers
import os
import shutil
import sys
from typing import List

import jsonpickle

from mmpm.__version__ import version
from mmpm.constants import color, paths
from mmpm.env import MMPMEnv


# TODO: GET RID OF THIS
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

    def no_args(self, subcmd: str) -> None:
        """
        Helper method to return a standardized error message when the user provides no arguments

        Parameters:
            subcommand (str): the name of the mmpm subcommand

        Returns:
            None
        """
        self.fatal(f"no arguments provided. See `mmpm {subcmd} --help` for usage")

    def extra_args(self, subcmd: str) -> None:
        """
        Helper method to return a standardized error message when the user provides too many arguments

        Parameters:
            subcommand (str): the name of the mmpm subcommand

        Returns:
            None
        """
        self.fatal(f"`mmpm {subcmd}` does not accept additional arguments. See `mmpm {subcmd} --help`")

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


# FIXME
class JSONSocketHandler(logging.handlers.SocketHandler):
    def makePickle(self, record):
        """
        Pickles the record in binary format with a length prefix and
        returns it ready for transmission across the socket.

        Instead of using Python's `pickle` module, we will use `jsonpickle`
        to serialize the LogRecord object to JSON format. This JSON data
        will be sent over the socket.
        """

        # Convert the LogRecord object to a plain dictionary for serialization
        log_record_dict = {
            "name": record.name,
            "msg": record.msg,
            "args": None,
            "levelname": record.levelname,
            "levelno": record.levelno,
            "pathname": record.pathname,
            "filename": record.filename,
            "module": record.module,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "created": record.created,
            "asctime": record.asctime,
            "msecs": record.msecs,
            "relativeCreated": record.relativeCreated,
            "thread": record.thread,
            "threadName": record.threadName,
            "processName": record.processName,
            "process": record.process,
            "exc_info": None,
            "exc_text": None,
            "stack_info": record.stack_info,
            "lineno": record.lineno,
            "msg": record.msg,
            "args": None,
            "exc_info": None,
            "created": record.created,
            "msecs": record.msecs,
            "relativeCreated": record.relativeCreated,
            "thread": record.thread,
            "threadName": record.threadName,
            "processName": record.processName,
            "process": record.process,
            "exc_text": None,
            "stack_info": record.stack_info,
        }

        serialized_data = jsonpickle.encode(log_record_dict)
        pickled_data = f"{len(serialized_data):08x}{serialized_data}"
        return pickled_data.encode("utf-8")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "version": version,
            "message": record.getMessage(),
            "logger_name": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        return json.dumps(log_data, ensure_ascii=False)


class StdoutFormatter(logging.Formatter):
    def format(self, record):
        label = ""

        if record.levelname == "INFO":
            label = "+"
        elif record.levelname == "WARNING":
            label = "X"
        else:
            label = record.levelname

        return f"[{label}] {record.getMessage()}"


class MMPMLogger:
    """
    Object used for logging while MMPM is executing.
    Log files can be found in ~/.config/mmpm/log
    """

    __logger__: logging.Logger = None

    @staticmethod
    def __init_logger__(name: str) -> None:
        MMPMLogger.__logger__ = logging.getLogger(name)
        MMPMLogger.__logger__.__setattr__("msg", StdOutMessageWriter())

        file_handler = logging.handlers.RotatingFileHandler(
            paths.MMPM_CLI_LOG_FILE,
            mode="a",
            maxBytes=1024 * 1024,
            backupCount=2,
            encoding="utf-8",
            delay=False,
        )

        level = MMPMEnv().MMPM_LOG_LEVEL.get()

        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JsonFormatter())

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(StdoutFormatter())
        stdout_handler.setLevel(level)

        # TODO: override the makePickle function in the SocketHandler
        # port = logging.handlers.DEFAULT_TCP_LOGGING_PORT
        # socket_handler = JSONSocketHandler('localhost', port)

        # MMPMLogger.__logger__.addHandler(socket_handler) # TODO
        MMPMLogger.__logger__.addHandler(file_handler)
        MMPMLogger.__logger__.addHandler(stdout_handler)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        if MMPMLogger.__logger__ is None:
            MMPMLogger.__init_logger__(name)
        return MMPMLogger.__logger__

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
                MMPMLogger.__logger__.error("MMPM log file not found")

        if gui_logs:
            if paths.MMPM_NGINX_ACCESS_LOG_FILE.exists():
                logs.append(str(paths.MMPM_NGINX_ACCESS_LOG_FILE))
            else:
                MMPMLogger.__logger__.error("Gunicorn access log file not found")
            if paths.MMPM_NGINX_ERROR_LOG_FILE.exists():
                logs.append(str(paths.MMPM_NGINX_ERROR_LOG_FILE))
            else:
                MMPMLogger.__logger__.error("Gunicorn error log file not found")

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
            MMPMLogger.__logger__.error(str(error))
            MMPMLogger.__logger__.error("Failed to create zip archive of log files. See `mmpm log` for details (I know...the irony)")
            return

        MMPMLogger.__logger__.info(f"Compressed MMPM log files to {os.getcwd()}/{file_name}.zip ")
