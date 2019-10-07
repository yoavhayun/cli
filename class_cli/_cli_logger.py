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

    DEFAULT_FORMAT = logging.Formatter("%(msg)s")

    def __init__(self, name, logLevel=logging.INFO):
        self._log = logging.getLogger(name)
        self._log.setLevel(logLevel)
        self._log

        # Define the styling of the logger
        self._styles = {}
        self._styles[logging.INFO]    = "%(msg)s"
        self._styles[logging.WARNING] = "[WARNING] %(msg)s"
        self._styles[logging.ERROR]   = "%(asctime)s\n[ERROR] %(msg)s"
        self._styles[logging.DEBUG]   = "%(asctime)s\n[DEBUG][%(module)s:%(lineno)d] %(msg)s"

        # Register stdout handler
        handler_stdout = logging.StreamHandler()
        handler_stdout.setLevel(logLevel)
        handler_stdout.setFormatter(CLI_Logger.Styler(self._compile_styles(self._styles, {
                logging.INFO : colors.bold,
                logging.WARNING : colors.fg.yellow,
                logging.ERROR : colors.fg.red,
                logging.DEBUG : colors.fg.darkgrey
            })))
        logging.root.addHandler(handler_stdout)

        # Register log file handler
        if name is not None:
            handler_file = logging.FileHandler(name)
            handler_file.setLevel(logging.DEBUG)
            handler_file.setFormatter(CLI_Logger.Styler(self._compile_styles(self._styles)))
            logging.root.addHandler(handler_file)

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