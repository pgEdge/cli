
#     Copyright (c)  2023-2024 PGEDGE  #

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

import sys

bold_start = "\033[1m"
bold_end = "\033[0m"

def echo_action(action, status=None, e=False):

    now = datetime.now()
    t = now.strftime('%B %d, %Y, %H:%M:%S')
    
    if status is None:
        sys.stdout.write(f"{t}: {action}... ")
        sys.stdout.flush()
    else:
        sys.stdout.write("\r")
        if status.lower() == "ok":
            sys.stdout.write(f"{t}: {action}... [OK]\n")
        else:
            sys.stdout.write(f"{t}: {action}... [Failed]\n")
            if e == True:
                exit(1)
        sys.stdout.flush()

def echo_message(msg, bold=False, level="info"):
    now = datetime.now()
    t = now.strftime('%B %d, %Y, %H:%M:%S')

    if bold == True:
        util.message(t + ": " + bold_start + msg + bold_end, level)
    else:
        util.message(t + ": " + msg,level)

    if level == "error":
        exit(1)

def echo_node(data):
    nodes = data.get('nodes', [])
    for node in nodes:
        print('#' * 30)
        for key, value in node.items():
            print(bold_start + f"* {key}:" + bold_end +"{value}")
        print(bold_start + '#'*30 + bold_end)

def echo_cmd(cmd, echo=False, sleep_secs=0, host="", usr="", key=""):
    if host > "":
        ssh_cmd = "ssh -o StrictHostKeyChecking=no -q -t "
        if usr > "":
            ssh_cmd = ssh_cmd + str(usr) + "@"

        ssh_cmd = ssh_cmd + str(host) + " "

        if key > "":
            ssh_cmd = ssh_cmd + "-i " + str(key) + " "

        cmd = cmd.replace('"', '\\"')

        if os.getenv("pgeDebug", "") > "":
            cmd = f"{cmd} --debug"

        cmd = ssh_cmd + ' "' + str(cmd) + '"'

    isSilent = os.getenv("isSilent", "False")
    if isSilent == "False":
        s_cmd = scrub_passwd(cmd)
        if echo:
            print("#  " + str(s_cmd))

    rc = os.system(str(cmd))
    if rc == 0:
        if int(sleep_secs) > 0:
            os.system("sleep " + str(sleep_secs))
        return 0

    return 1

def scrub_passwd(p_cmd):
    ll = p_cmd.split()
    flag = False
    new_s = ""
    key_wd = ""

    for i in ll:
        if ((i == "PASSWORD") or (i == "-P")) and (flag is False):
            flag = True
            key_wd = str(i)
            continue

        if flag:
            new_s = new_s + " " + key_wd + " '???'"
            flag = False
        else:
            new_s = new_s + " " + i

    return new_s

def run_command(command_args, max_attempts=1, timeout=None, capture_output=True, env=None, cwd=None, verbose=False):
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
                print(f"Command executed successfully.")
            return {"success": True, "output": output, "error": error, "attempts": attempts}

        except subprocess.CalledProcessError as e:
            error = e.stderr if capture_output else str(e)
            if verbose:
                print(f"Error executing command: {error}")
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
    try:
        dt = parser.parse(date_string)
        if dt.tzinfo is None:
            from datetime import timezone
            dt = dt.replace(tzinfo=timezone.utc)

        if target_timezone.upper() != 'UTC':
            from zoneinfo import ZoneInfo
            dt = dt.astimezone(ZoneInfo(target_timezone))

        formatted_time_with_timezone = dt.strftime("%Y-%m-%d %H:%M:%S")

        return formatted_time_with_timezone

    except ValueError as e:
        raise ValueError(f"Invalid date string format: {e}")

def guc_set(guc_name, guc_value, pg=None):
    if pg is None:
        pg_v = util.get_pg_v(pg)
        pg = pg_v[2:]

    cmd_prefix = f"./pgedge pgbin {pg} "

    alter_system_cmd = f'psql -q -c "ALTER SYSTEM SET {guc_name} = {guc_value}" postgres'

    rc1 = util.echo_cmd(f'{cmd_prefix}"{alter_system_cmd}"', False)

    reload_conf_cmd = 'psql -q -c "SELECT pg_reload_conf()" postgres'

    rc2 = util.echo_cmd(f'{cmd_prefix}"{reload_conf_cmd}"', False)

    if rc1 == 0 and rc2 == 0:
        util.message(f"Set GUC {guc_name} to {guc_value}", "info")
    else:
        util.message("Unable to set GUC", "error")

