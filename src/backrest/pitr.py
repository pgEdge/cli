#!/usr/bin/env python3

import subprocess
import sys
import os
import time
from datetime import datetime

# Setup global configuration
config = {
    "PGPORT": "5432",
    "NEW_PGPORT": "5433",
    "HOSTNAME": "127.0.0.1",
    "DATABASE_NAME": "postgres",
    "TEMP_LOG_FILE": "/tmp/logfile.log",
    "PGBENCH_SCALE_FACTOR": "10",
    "DEBUG_MODE": "0",
    "PSX": os.getenv("PSX", "/home/pgedge/dev/cli/out/posix"),
}

# Update environment variables
os.environ["PATH"] = f"{config['PSX']}/pg16/bin:" + os.environ["PATH"]
config["PGDATA"] = f"{config['PSX']}/restore/pg16/data"
config["PGDATA_PRIMARY"] = f"{config['PSX']}/data/pg16"

# Determine debug mode from command line arguments
if len(sys.argv) > 1:
    if sys.argv[1] == "-d":
        config["DEBUG_MODE"] = "d"
    elif sys.argv[1] == "-d1":
        config["DEBUG_MODE"] = "d1"

def print_bold(message, end="\n"):
    """Prints a message in bold."""
    print(f"\033[1m{message}\033[0m", end=end)

def execute_command(command, step, exit=True):
    """Executes a command based on the configured debug mode and prints accordingly."""
    cmd_str = ' '.join(command)
    try:
        if config["DEBUG_MODE"] == "d1":
            # Print command and execute with output
            print(f"{step} - [ {cmd_str} ", end=" ...] ")
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print_bold("OK")
            print(result.stdout.strip())
        elif config["DEBUG_MODE"] == "d":
            # Print command only and execute without showing output
            print(f"{step} - [ {cmd_str} ", end=" ...] ")
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print_bold("OK")
        else:
            print(f"{step} - ", end=" ...")
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print_bold("OK")
    except subprocess.CalledProcessError:
        if exit == True:
            print_bold("FAIL", end="\n")
            sys.exit(1)
        else:
            print_bold("IGNORED", end="\n")


def check_server_running(step, pgdata_path):
    """Checks if the PostgreSQL server is running."""

    status_command = ["pg_ctl", "-D", pgdata_path, "status"]
    execute_command(status_command, f"{step} - Stopping PostgreSQL", False)

def stop_postgres_and_clean_data(step):
    """Stops PostgreSQL if running and removes the data directory if it exists."""
    if check_server_running(step, config["PGDATA"]):
        execute_command(["pg_ctl", "stop", "-D", config["PGDATA"], "-l", config["TEMP_LOG_FILE"]], f"{step} - Stopping PostgreSQL", False)
    if os.path.exists(config["PGDATA"]):
        execute_command(["rm", "-rf", config["PGDATA"]], f"{step} - Removing Data Directory", False)

def main():

    # Stop PostgreSQL and remove data directory
    step = "1 - Stop PostgreSQL and Clean Data Directory"
    stop_postgres_and_clean_data(step)

    # Insert Rows with pgbench
    step = "2 - Insert Rows"
    execute_command(["pgbench", "-h", config["HOSTNAME"], "-d", config["DATABASE_NAME"], "-i", "-s", config["PGBENCH_SCALE_FACTOR"]], step)

    # Perform a full backup
    step = "3 - Perform Full Backup"
    execute_command(["pgedge", "backrest", "backup"], step)

    # Insert Rows with pgbench
    step = "4 - Insert Rows"
    execute_command(["pgbench", "-h", config["HOSTNAME"], "-d", config["DATABASE_NAME"], "-i", "-s", config["PGBENCH_SCALE_FACTOR"]], step)

    # Perform Point-in-Time Recovery
    step = "5 - Perform PITR"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_command(["pgedge", "backrest", "pitr", f"--recovery-target-time=\"{current_time}\""], step)

    # Insert Rows with pgbench
    step = "6 - Insert Rows"
    execute_command(["pgbench", "-h", config["HOSTNAME"], "-d", config["DATABASE_NAME"], "-i", "-s", config["PGBENCH_SCALE_FACTOR"]], step)
    # Start PostgreSQL

    step = "7 - Start PostgreSQL"
    execute_command(["pg_ctl", "start", "-D", config["PGDATA"], "-l", config["TEMP_LOG_FILE"]], step)

    # Verify the restored database
    step = "8 - Checking primary server rows"
    execute_command(["psql", "-h", "127.0.0.1", "-p", "5432", "postgres", "-c", "SELECT COUNT(*) FROM pgbench_accounts"], step)
    step = "9 - Checking resetored server rows"
    execute_command(["psql", "-h", "127.0.0.1", "-p", "5433", "postgres", "-c", "SELECT COUNT(*) FROM pgbench_accounts"], step)


    print_bold("\nScript execution completed.")

if __name__ == "__main__":
    main()

