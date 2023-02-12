#!/usr/bin/env python3
import os
import sys
import shutil
import logging
import logging.handlers
import datetime
import mmpm.color
import mmpm.utils
from mmpm.consts import MMPM_CLI_LOG_FILE, MMPM_LOG_DIR


class StdOutMessageWriter:
    def __init__(self):
        pass

    def info(self, msg: str) -> None:
        '''
        Prints message 'msg' without a new line

        Parameters:
            msg (str): The message to be printed to stdout

        Returns:
            None
        '''
        sys.stdout.write(msg)
        sys.stdout.flush()


    def error(self, msg: str) -> None:
        '''
        Logs error message, displays error message to user, and continues program execution

        Parameters:
            msg (str): The error message to be printed to stdout

        Returns:
            None
        '''
        print(mmpm.color.bright_red('ERROR:'), msg)


    def warning(self, msg: str) -> None:
        '''
        Logs warning message, displays warning message to user, and continues program execution

        Parameters:
            msg (str): The warning message to be printed to stdout

        Returns:
            None
        '''
        print(mmpm.color.bright_yellow('WARNING:'), msg)


    def fatal(self, msg: str) -> None:
        '''
        Logs fatal message, displays fatal message to user, and halts program execution

        Parameters:
            msg (str): The fatal error message to be printed to stdout

        Returns:
            None
        '''
        print(mmpm.color.bright_red('FATAL:'), msg)
        sys.exit(127)


    def env_variables_error(self, preamble: str = '') -> None:
        '''
        Helper method to log and display an error relating to a common issue of not
        setting environment variables properly

        Parameters:
            preamble (str): an optional argument to provide more specific error messaging

        Returns:
            None
        '''
        msg: str = mmpm.consts.MMPM_ENV_ERROR_MESSAGE

        if preamble:
            msg = f'{preamble} {msg}'

        self.error(msg)


    def env_variables_fatal(self, preamble: str = '') -> None:
        '''
        Helper method to log and display a fatal error relating to a common issue of not
        setting environment variables properly

        Parameters:
            preamble (str): an optional argument to provide more specific error messaging

        Returns:
            None
        '''
        msg: str = mmpm.consts.MMPM_ENV_ERROR_MESSAGE

        if preamble:
            msg = f'{preamble} {msg}'

        self.fatal(msg)



class MMPMLogger():
    '''
    Object used for logging while MMPM is executing.
    Log files can be found in ~/.config/mmpm/log
    '''

    __logger__: logging.Logger = None


    @staticmethod
    def __init_logger__(name: str) -> None:
        MMPM_LOG_DIR.mkdir(exist_ok=True)
        MMPM_CLI_LOG_FILE.touch(exist_ok=True)

        log_format: str = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s'
        logging.basicConfig(filename=MMPM_CLI_LOG_FILE, format=log_format)

        MMPMLogger.__logger__ = logging.getLogger(name)
        MMPMLogger.__logger__.__setattr__("msg", StdOutMessageWriter())

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
    def get_logger(name: str) -> logging.Logger:
        if MMPMLogger.__logger__ is None:
            MMPMLogger.__init_logger__(name)

        return MMPMLogger.__logger__


    @classmethod
    def display_log_files(cls, cli_logs: bool = False, gui_logs: bool = False, tail: bool = False) -> None:
        '''
        Displays contents of log files to stdout. If the --tail option is supplied,
        log contents will be displayed in real-time

        Parameters:
        cli_logs (bool): if True, the CLI log files will be displayed
        gui_logs (bool): if True, the Gunicorn log files for the web interface will be displayed
        tail (bool): if True, the contents will be displayed in real time

        Returns:
            None
        '''
        logs: List[str] = []

        if cli_logs:
            if mmpm.consts.MMPM_CLI_LOG_FILE.exists():
                logs.append(str(mmpm.consts.MMPM_CLI_LOG_FILE))
            else:
                mmpm.utils.error_msg('MMPM log file not found')

        if gui_logs:
            if mmpm.consts.MMPM_NGINX_ACCESS_LOG_FILE.exists():
                logs.append(str(mmpm.consts.MMPM_NGINX_ACCESS_LOG_FILE))
            else:
                mmpm.utils.error_msg('Gunicorn access log file not found')
            if mmpm.consts.MMPM_NGINX_ERROR_LOG_FILE.exists():
                logs.append(str(mmpm.consts.MMPM_NGINX_ERROR_LOG_FILE))
            else:
                mmpm.utils.error_msg('Gunicorn error log file not found')

        if logs:
            os.system(f"{'tail -F' if tail else 'cat'} {' '.join(logs)}")


    @classmethod
    def zip_mmpm_log_files(cls) -> None:
        '''
        Compresses all log files in ~/.config/mmpm/log. The NGINX log files are
        excluded due to mostly irrelevant information the user, or I would need
        when creating GitHub issues

        Parameters:
            None

        Returns:
            None
        '''
        today = datetime.datetime.now()

        zip_file_name: str = f'mmpm-logs-{today.year}-{today.month}-{today.day}'
        MMPMLogger.__logger__.msg.info(f'{mmpm.consts.GREEN_PLUS} Compressing MMPM log files to {os.getcwd()}/{zip_file_name}.zip ')

        try:
            shutil.make_archive(zip_file_name, 'zip', mmpm.consts.MMPM_LOG_DIR)
        except Exception as error:
            print(mmpm.consts.RED_X)
            MMPMLogger.__logger__.msg.error(str(error))
            MMPMLogger.__logger__.msg.error('Failed to create zip archive of log files. See `mmpm log` for details (I know...the irony)')
            return

        print(mmpm.consts.GREEN_CHECK_MARK)


