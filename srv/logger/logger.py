import logging
import sys
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s — %(funcName)s — %(levelname)s — %(message)s")
CONSOLE_FORMATTER = logging.Formatter("[%(levelname)s]-%(asctime)s : %(message)s")

def get_console_handler():
   """
       This function creates the logging handler for console output
   """
   # setting the output stream
   console_handler = MConsoleHandler()
   # setting the format of a logging message
   console_handler.setFormatter(CONSOLE_FORMATTER)
   # setting the type of the messages that gets logged
   # For console output only error messages appeares in the output
   console_handler.setLevel(logging.INFO)
   return console_handler


class MConsoleHandler(logging.StreamHandler):
    """
          Handler that controls the writing of the newline character
    """
    def __init__(self):
          logging.StreamHandler.__init__(self, sys.stdout)

    # if this symbol is included in the message then
    # the message would be printed out on the same line
    special_code = '[!n]'

    def emit(self, record) -> None:
        """
            This function analyzes the message and
            if the special symbol is specified in the message
            then the function insert some special control symbols
        """
        # find the special symbol in the message
        if self.special_code in record.msg:
            # remove the special symbol from the message
            record.msg = record.msg.replace( self.special_code, '' )
            # set the control symbol of clearing the last line in cosole
            # output
            self.terminator = '\r'
        else:
            # if there is no special symbol in the message
            # then we set control symbol to end the line and
            # start output on the new line
            self.terminator = '\n'

        return super().emit(record)


def get_file_handler(file_name):
   """
       This function creates the logging handler for output to a file
   """
   # setting the way a new log file would be created if the application
   # runs without stopping
   file_handler = TimedRotatingFileHandler(file_name, when='midnight')
   # setting the forma of logging message
   file_handler.setFormatter(FORMATTER)
   return file_handler


def get_logger(logger_name, level, file_name):
   """
       This function returns the logging handler which
       can be used to put a message to logging output
   """
   # setting the name of logging channel
   logger = logging.getLogger(logger_name)
   # setting the message level. The level takes from
   # the input parameters
   logger.setLevel(level)
   # setting the logging to console
   logger.addHandler(get_console_handler())
   # setting the logging to file
   logger.addHandler(get_file_handler(file_name))
   logger.propagate = False
   return logger
