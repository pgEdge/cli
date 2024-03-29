#!/usr/bin/env python3
#     Copyright (c)  2022-2024 PGEDGE  #
import subprocess
import os
import fire
import util
import json
import sys
from datetime import datetime
from tabulate import tabulate
import subprocess
import time
from dateutil import parser
from datetime import datetime
import logging

def run_command(command_args, max_attempts=1, timeout=None, capture_output=False, env=None, cwd=None, verbose=True):
    """
    Executes an external command, with options to retry, set timeout, and capture output.

    Args:
        command_args (list): Command and its arguments as a list, e.g., ['ls', '-l'].
        max_attempts (int): Maximum number of attempts to execute the command.
        timeout (int, optional): Time in seconds to wait for the command to complete.
        capture_output (bool): Whether to capture and return the command's output.
        env (dict, optional): Environment variables to set for the command.
        cwd (str, optional): Set the working directory for the command.
        verbose (bool): Print detailed execution logs.

    Returns:
        dict: A dictionary with keys 'success', 'output', 'error', and 'attempts',
              indicating the execution status, captured output, error message, and number of attempts.
    """
    attempts = 0
    output, error = "", ""

    while attempts < max_attempts:
        try:
            attempts += 1
            result = subprocess.run(command_args, check=True, text=True,
                                    capture_output=capture_output, timeout=timeout,
                                    env=env, cwd=cwd)
            if capture_output:
                output = result.stdout
                error = result.stderr
            if verbose:
                print(f"Attempt {attempts}: Command executed successfully.")
            return {"success": True, "output": output, "error": error, "attempts": attempts}

        except subprocess.CalledProcessError as e:
            error = e.stderr if capture_output else str(e)
            if verbose:
                print(f"Attempt {attempts}: Error executing command: {error}")
            time.sleep(1)  # Simple backoff strategy
        except subprocess.TimeoutExpired as e:
            error = f"Command timed out after {timeout} seconds."
            if verbose:
                print(f"Attempt {attempts}: {error}")
            break  # No retry after timeout

    return {"success": False, "output": output, "error": error, "attempts": attempts}


def check_directory_status(directory_path):
    """
    Checks if a specified directory exists and if it is readable and writable.

    Args:
        directory_path (str): The path to the directory to check.

    Returns:
        dict: A dictionary with the following keys:
              - 'exists' (bool): True if the directory exists, False otherwise.
              - 'is_directory' (bool): True if the path is a directory, False if it exists but is not a directory.
              - 'readable' (bool): True if the directory is readable, False if it is not readable or does not exist.
              - 'writable' (bool): True if the directory is writable, False if it is not writable or does not exist.
              - 'message' (str): A message describing the status of the directory.
    """
    status = {
        'exists': False,
        'is_directory': False,
        'readable': False,
        'writable': False,
        'message': ''
    }

    if os.path.exists(directory_path):
        status['exists'] = True
        if os.path.isdir(directory_path):
            status['is_directory'] = True

            # Check for readability
            if os.access(directory_path, os.R_OK):
                status['readable'] = True

            # Check for writability
            if os.access(directory_path, os.W_OK):
                status['writable'] = True

            status['message'] = f"Directory '{directory_path}' exists, " + \
                                ("is readable, " if status['readable'] else "is not readable, ") + \
                                ("and is writable." if status['writable'] else "and is not writable.")
        else:
            status['message'] = f"The path '{directory_path}' exists but is not a directory."
    else:
        status['message'] = f"Directory '{directory_path}' does not exist."

    return status


def sfmt_time(date_string, target_timezone='UTC'):
    """
    Formats a given date string to 'YYYY-MM-DD HH:MM:SS' format including timezone conversion.

    Args:
        date_string (str): The date string to format.
        target_timezone (str): The target timezone for the formatted datetime. Defaults to 'UTC'.

    Returns:
        str: Formatted datetime string with timezone.

    Raises:
        ValueError: If the input date string is in an invalid format.
    """
    try:
        # Use dateutil.parser to automatically parse the date string
        dt = parser.parse(date_string)

        # Check if the datetime object is timezone-aware. If not, assume UTC.
        if dt.tzinfo is None:
            from datetime import timezone
            dt = dt.replace(tzinfo=timezone.utc)

        # Convert to target timezone if necessary
        if target_timezone.upper() != 'UTC':
            from zoneinfo import ZoneInfo
            dt = dt.astimezone(ZoneInfo(target_timezone))

        # Format the datetime object to the required format with timezone information
        formatted_time_with_timezone = dt.strftime("%Y-%m-%d %H:%M:%S")
        #formatted_time_with_timezone = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

        return formatted_time_with_timezone

    except ValueError as e:
        raise ValueError(f"Invalid date string format: {e}")

# Setup the logger
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)  # This could be configurable

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(levelname)s - %(message)s')

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
logger.addHandler(ch)


def ereport(severity, message, detail=None, hint=None, context=None):
    """
    Mimics PostgreSQL's ereport function for logging messages in a style that closely resembles PostgreSQL log format.

    Args:
        severity (str): The severity level ('ERROR', 'WARNING', 'NOTICE', 'DEBUG', etc.).
        message (str): The primary human-readable error message.
        detail (str, optional): An optional detail message providing more context.
        hint (str, optional): An optional hint message suggesting how to fix the problem.
        context (str, optional): An optional context message where the error occurred.
    """
    parts = [f"{message}"]
    if detail:
        parts.append(f" |\tDETAIL: {detail}")
    if hint:
        parts.append(f" |\tHINT: {hint}")
    if context:
        parts.append(f" |\tCONTEXT: {context}")

    full_message = "\n".join(parts)

    # Assuming logger is already configured
    if severity.upper() == 'ERROR':
        logger.error(full_message)
    elif severity.upper() == 'WARNING':
        logger.warning(full_message)
    elif severity.upper() == 'NOTICE':
        logger.info(full_message)  # NOTICE is mapped to INFO in logging
    elif severity.upper() == 'DEBUG':
        logger.debug(full_message)
    else:
        logger.info(full_message)  # Default to INFO for unrecognized severity levels

def guc_set(guc_name, guc_value, pg=None):
    """
    Sets a PostgreSQL GUC (Grand Unified Configuration) parameter.

    Args:
        guc_name (str): The name of the GUC parameter to set.
        guc_value (str): The value to set for the GUC parameter.
        pg (str, optional): The PostgreSQL version. If not provided, uses a default or derives it.
    """
    if pg is None:
        # If pg version is not specified, obtain it using util.get_pg_v function
        pg_v = util.get_pg_v(pg)
        pg = pg_v[2:]  # Assuming util.get_pg_v returns a version string with a prefix to trim

    # Base command prefix for using the appropriate PostgreSQL binary
    cmd_prefix = f"./pgedge pgbin {pg} "

    # Command to alter the system setting for the specified GUC
    alter_system_cmd = f'psql -q -c "ALTER SYSTEM SET {guc_name} = {guc_value}" postgres'

    # Execute the ALTER SYSTEM command
    rc1 = util.echo_cmd(f'{cmd_prefix}"{alter_system_cmd}"', False)

    # Command to reload the configuration to apply the change
    reload_conf_cmd = 'psql -q -c "SELECT pg_reload_conf()" postgres'

    # Execute the RELOAD CONFIGURATION command
    rc2 = util.echo_cmd(f'{cmd_prefix}"{reload_conf_cmd}"', False)

    # Check if both commands executed successfully
    if rc1 == 0 and rc2 == 0:
        util.message(f"Set GUC {guc_name} to {guc_value}", "info")
    else:
        util.message("Unable to set GUC", "error")

