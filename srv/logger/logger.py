import logging
import sys
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s — %(funcName)s — %(levelname)s — %(message)s")
CONSOLE_FORMATTER = logging.Formatter("[%(levelname)s]-%(asctime)s : %(message)s")

def get_console_handler(level):
   """
       This function creates the logging handler for console output
   """
   # setting the output stream
   console_handler = logging.StreamHandler(sys.stdout)
   # setting the format of a logging message
   console_handler.setFormatter(CONSOLE_FORMATTER)
   # setting the type of the messages that gets logged
   # For console output only error messages appeares in the output
   console_handler.setLevel(level)
   return console_handler


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
   logger.addHandler(get_console_handler(level))
   # setting the logging to file
   logger.addHandler(get_file_handler(file_name))
   logger.propagate = False
   return logger
