import logging
import sys
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s — %(funcName)s — %(levelname)s — %(message)s")
CONSOLE_FORMATTER = logging.Formatter("[%(levelname)s]: %(message)s")

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(CONSOLE_FORMATTER)
   return console_handler


def get_file_handler(file_name):
   file_handler = TimedRotatingFileHandler(file_name, when='midnight')
   file_handler.setFormatter(FORMATTER)
   return file_handler


def get_logger(logger_name, level, file_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(level)
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler(file_name))
   logger.propagate = False
   return logger
