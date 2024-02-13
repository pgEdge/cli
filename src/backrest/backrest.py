#!/usr/bin/env python3
import argparse
import subprocess
import os
import json
import schedule
import time
import sys

thisDir = os.getcwd()

# Function to get PostgreSQL binary directory
def get_pg_data_dir():
    pg_version_dirs = ["pg14", "pg15", "pg16"]
    for version_dir in pg_version_dirs:
        if os.path.isdir(version_dir):
            return "data/" + version_dir
    exit_rm_backrest("pg14, 15, or 16 must be installed")

# Function to get PostgreSQL data directory
def get_pg_bin_dir():
    pg_version_dirs = ["pg14", "pg15", "pg16"]
    for version_dir in pg_version_dirs:
        if os.path.isdir(version_dir):
            return version_dir + "/bin"
    exit_rm_backrest("pg14, 15, or 16 must be installed")


# Function to perform full backup
def perform_full_backup(username, stanza, config_file, bin_dir, data_dir):
    backup_type = "full"
    backup_command = f"/usr/bin/pgbackrest --db-user={username} --pg1-host=localhost --config=/etc/pgbackrest/pgbackrest.conf --stanza={stanza} --pg1-path={thisDir}/{data_dir} --type={backup_type} backup"
    print(f"Performing {backup_type} backup...")
    subprocess.run(backup_command, shell=True, check=True)
    print("Backup completed.")

# Function to perform incremental backup
def perform_incremental_backup(username, stanza, config_file, bin_dir, data_dir):
    backup_type = "incr"
    backup_command = f"/usr/bin/pgbackrest --db-user={username} --pg1-host=localhost  --config=/etc/pgbackrest/pgbackrest.conf --stanza={stanza} --pg1-path={thisDir}/{data_dir} --type={backup_type} backup"
    print(f"Performing {backup_type} backup...")
    subprocess.run(backup_command, shell=True, check=True)
    print("Backup completed.")

# Function to read the backup schedule from JSON configuration
def read_schedule(conf_file):
    try:
        with open(f'{conf_file}', 'r') as file:
            schedule_data = json.load(file)
        return schedule_data
    except FileNotFoundError:
        print("Schedule configuration file not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON file.")
        return None

# Function to handle the --version command
def handle_version():
    print("1.0.0")
    sys.exit(0)

# Function to exit if pg version is not found
def exit_rm_backrest(message):
    print(message)
    sys.exit(1)

# Main function
def main():
    parser = argparse.ArgumentParser(description='pgBackRest Backup Scheduler')
    parser.add_argument('--version', action='store_true', help='Display version information')
    parser.add_argument('--user', help='Specify PostgreSQL username')
    parser.add_argument('--stanza', help='Specify PostgreSQL stanza name')
    parser.add_argument('--config', help='Specify configuration file')
    args = parser.parse_args()

    if args.version:
        handle_version()
    elif not all([args.user, args.stanza, args.config]):
        print("Please provide PostgreSQL username, stanza name, and configuration file.")
        sys.exit(1)

    bin_dir = get_pg_bin_dir();
    data_dir = get_pg_data_dir();

    schedule_data = read_schedule(args.config)

    if schedule_data:
        for job in schedule_data.get('jobs', []):
            if job.get('type') == 'full':
                schedule_config = job.get('schedule', {})
                if 'daily' in schedule_config:
                    schedule.every().day.at(schedule_config['daily']['time']).do(perform_full_backup, args.user, args.stanza, args.config, bin_dir, data_dir)
                elif 'weekly' in schedule_config:
                    for day in schedule_config['weekly']['days']:
                        schedule.every().wednesday.at(schedule_config['weekly']['time']).do(perform_full_backup, args.user, args.stanza, args.config, bin_dir, data_dir)
            elif job.get('type') == 'incr':
                schedule.every(int(job.get('interval', 1))).minutes.do(perform_incremental_backup, args.user, args.stanza, args.config, bin_dir, data_dir)

        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    main()

