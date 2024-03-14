import logging
import sys
import os
import traceback

# Global configuration for log destination
config = {
    'log_destination': 'stdout',  # Can be 'stdout', 'stderr', 'syslog', or 'file'
    'log_file': 'app.log'  # Specify log file name here
}

# Define log level constants
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"
FATAL = "FATAL"

if os.name == "posix":
    from logging.handlers import SysLogHandler

# ANSI escape codes for colors and formatting
RED_TEXT = "\033[31m"
BOLD_TEXT = "\033[1m"
RESET_FORMATTING = "\033[0m"

# Singleton pattern to ensure setup_logging is called only once
def setup_logging():
    if not hasattr(setup_logging, "configured"):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # Set to the lowest level
        logger.handlers.clear()  # Clear existing handlers

        if config['log_destination'] == 'stderr':
            handler = logging.StreamHandler(sys.stderr)
        elif config['log_destination'] == 'syslog' and os.name == "posix":
            handler = SysLogHandler(address='/dev/log')
        elif config['log_destination'] == 'file':
            handler = logging.FileHandler(config['log_file'])
        else:
            handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        setup_logging.configured = True
        return logger

setup_logging()  # Automatically called when the module is imported

def elog(level, message):
    logger = logging.getLogger()
    formatted_level = level.upper()
    if formatted_level == "FATAL":
        formatted_message = f"{RED_TEXT}{formatted_level} - {message}{RESET_FORMATTING}"
        logger.critical(formatted_message)
        print_traceback()
    elif formatted_level == "ERROR":
        formatted_message = f"{BOLD_TEXT}{formatted_level} - {message}{RESET_FORMATTING}"
        logger.error(formatted_message)
        print_traceback()
    else:
        logger.log(getattr(logging, formatted_level, logging.INFO), message)

def print_traceback():
    traceback_details = traceback.format_stack()
    traceback_str = "".join(traceback_details)
    logging.getLogger().error(traceback_str)

