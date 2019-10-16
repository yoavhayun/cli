"""
This module handels the logger for the cli library

Author: Hayun, Yoav 
Email: YoavHayun@gmail.com
"""

import logging
from class_cli._colors import colors

class CLI_Logger():
    """
    A class for logging and printing messages and errors
    """
    ACTIVE_HANDLERS = []
    DEFAULT_FORMAT = logging.Formatter("%(msg)s")

    def __init__(self, filepath=None, logLevel=logging.INFO):
        self.handler_stdout = None
        self.handler_file = None

        self._log = logging.getLogger(filepath)
        if logLevel is not None:
            self._log.setLevel(logLevel)
        
        self._silent = logLevel is None

        # Define the styling of the logger
        self._styles = {}
        self._styles[logging.INFO]    = "%(msg)s"
        self._styles[logging.WARNING] = "[WARNING] %(msg)s"
        self._styles[logging.ERROR]   = "%(asctime)s\n[ERROR] %(msg)s"
        self._styles[logging.DEBUG]   = "%(asctime)s\n[DEBUG][%(module)s:%(lineno)d] %(msg)s"

        # Register stdout handler
        if logLevel is not None:
            self.handler_stdout = logging.StreamHandler()
            self.handler_stdout.setLevel(logLevel)
            self.handler_stdout.setFormatter(CLI_Logger.Styler(self._compile_styles(self._styles, {
                    logging.INFO : colors.bold,
                    logging.WARNING : colors.fg.yellow,
                    logging.ERROR : colors.fg.red,
                    logging.DEBUG : colors.fg.darkgrey
                })))

        # Register log file handler
        if filepath is not None:
            self.handler_file = logging.FileHandler(filepath)
            self.handler_file.setLevel(logging.DEBUG)
            self.handler_file.setFormatter(CLI_Logger.Styler(self._compile_styles(self._styles)))

    def isSilent(self):
        return self._silent

    def disable(self):
        self._disable_logs()

        if len(CLI_Logger.ACTIVE_HANDLERS) > 1 and self == CLI_Logger.ACTIVE_HANDLERS[-1]:
            CLI_Logger.ACTIVE_HANDLERS[-2]._enable_logs()
        
        if self in CLI_Logger.ACTIVE_HANDLERS:
            CLI_Logger.ACTIVE_HANDLERS.remove(self)


    def _disable_logs(self):
        if self.handler_stdout is not None:
            logging.root.removeHandler(self.handler_stdout)
        if self.handler_file is not None:
            logging.root.removeHandler(self.handler_file)

    def enable(self):
        if len(CLI_Logger.ACTIVE_HANDLERS) > 0:
            CLI_Logger.ACTIVE_HANDLERS[-1]._disable_logs()
        CLI_Logger.ACTIVE_HANDLERS.append(self)
        self._enable_logs()
    
    def _enable_logs(self):
        if self.handler_stdout is not None:
            logging.root.addHandler(self.handler_stdout)
        if self.handler_file is not None:
            logging.root.addHandler(self.handler_file)



    def _compile_styles(self, styles, modifiers={}):
        """
        Wraps a given style dictionary

        Accepts:
            @styles     A logger styles dictionary
            @modifiers  A dictionary to override the prefix of a logger style and reset as a suffix
        """
        _styles = {k : logging.Formatter("{}{}{}".format(modifiers[k], styles[k], colors.reset) if k in modifiers else styles[k]) for k in styles}
        return _styles
    
    def get_logger(self):
        """
        returns the logger instance to log messages.
        """
        return self._log

    class Styler(logging.Formatter):
        """
        Handles the styling and formatting of message logging and printing
        """
        def __init__(self, styles):
            super().__init__(datefmt='%Y-%m-%d %H:%M:%S')
            self._styles = styles
        
        def format(self, record):
            self._style = self._styles.get(record.levelno, CLI_Logger.DEFAULT_FORMAT)
            return logging.Formatter.format(self, record)