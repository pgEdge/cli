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

def fetch_backup_config():
    """Fetch backup configuration from util module or other configuration source."""
    config = {
        "BACKUP_TOOL": util.get_value("BACKUP", "BACKUP_TOOL"),
        "STANZA": util.get_value("BACKUP", "STANZA"),
        "DATABASE": util.get_value("BACKUP", "DATABASE"),
        "PG_PATH": util.get_value("BACKUP", "PG_PATH"),
        "PG_SOCKET_PATH": util.get_value("BACKUP", "PG_SOCKET_PATH"),
        "PG_USER": util.get_value("BACKUP", "PG_USER"),
        "REPO_CIPHER_TYPE": util.get_value("BACKUP", "REPO_CIPHER_TYPE"),
        "REPO_PATH": util.get_value("BACKUP", "REPO_PATH"),
        "REPO_RETENTION_FULL_TYPE": util.get_value("BACKUP", "REPO_RETENTION_FULL_TYPE"),
        "REPO_RETENTION_FULL": util.get_value("BACKUP", "REPO_RETENTION_FULL"),
        "PRIMARY_HOST": util.get_value("BACKUP", "PRIMARY_HOST"),
        "PRIMARY_PORT": util.get_value("BACKUP", "PRIMARY_PORT"),
        "PRIMARY_USER": util.get_value("BACKUP", "PRIMARY_USER"),
        "REPLICA_PASSWORD": util.get_value("BACKUP", "REPLICA_PASSWORD"),
        "RECOVERY_TARGET_TIME": util.get_value("BACKUP", "RECOVERY_TARGET_TIME"),
        "PROCESS_MAX": util.get_value("BACKUP", "PROCESS_MAX"),
        "RESTORE_PATH": util.get_value("BACKUP", "RESTORE_PATH"),

        "REPO1_TYPE": util.get_value("BACKUP", "REPO1_TYPE"),

        "REPO_PATH": util.get_value("BACKUP", "REPO_PATH"),
        "PG_PATH": util.get_value("BACKUP", "PG_PATH"),
        "BACKUP_TYPE": util.get_value("BACKUP", "BACKUP_TYPE"),

        "S3_BUCKET": util.get_value("BACKUP", "S3_BUCKET"),
        "S3_REGION": util.get_value("BACKUP", "S3_REGION"),
        "S3_ENDPOINT": util.get_value("BACKUP", "S3_ENDPOINT"),
    }
    return config

def run_command(command_args):
    try:
        subprocess.run(command_args, check=True)
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)


def backup(type="full"):
    """
    Backup a database cluster.

    :param type: Specifies the type of backup to perform. This should be one of the following options:

                 * "full" - Performs a full backup.

                 * "diff" - Performs a differential backup.

                 * "incr" - Performs an incremental backup.

    :type type: str
    :return: None
    """

    config = fetch_backup_config()
    allowed_types = ["full", "diff", "incr"]
    if type not in allowed_types:
        print(f"Error: '{type}' is not a valid backup type. Allowed types are: {', '.join(allowed_types)}.")
        return

    command = [
        config["BACKUP_TOOL"], "--type", type, "backup",
        "--stanza", config["STANZA"],
        "--pg1-path", config["PG_PATH"],
        "--start-fast",
        "--process-max", config["PROCESS_MAX"],
        #"--pg1-host", config["PRIMARY_HOST"],
        "--pg1-port", config["PRIMARY_PORT"],
        "--repo1-retention-full-type", config["REPO_RETENTION_FULL_TYPE"],
        "--repo1-retention-full", config["REPO_RETENTION_FULL"],
    ]

    # Adding repository type specific configurations
    if config["REPO1_TYPE"] == "s3":
        command.extend([
            "--repo1-type", "s3",
            "--repo1-s3-bucket", config["S3_BUCKET"],
            "--repo1-s3-region", config["S3_REGION"],
            "--repo1-s3-endpoint", config["S3_ENDPOINT"],
        ])
    elif config["REPO1_TYPE"] == "posix":
        command.extend(["--repo1-path", config["REPO_PATH"]])

    run_command(command)

def check_restore_path(restore_path):
    """Check if the restore path exists and if it is writable."""
    directory_existed = os.path.exists(restore_path)

    if not directory_existed:
        print(f"INFO: Restore path '{restore_path}' does not exist. Will attempt to create.", file=sys.stderr)
        try:
            os.makedirs(restore_path)  # Attempt to create the directory
            return True, False  # Directory was successfully created, did not exist before
        except PermissionError:
            print(f"Error: No permission to create the restore path '{restore_path}'.", file=sys.stderr)
            return False, False  # Permission error to create directory
    elif not os.access(restore_path, os.W_OK):
        print(f"Error: No write permission on the restore path '{restore_path}'.", file=sys.stderr)
        return False, directory_existed  # Directory exists but no write permission
    else:
        return True, directory_existed  # Directory exists and is writable

def format_recovery_target_time(recovery_target_time=None):
    if recovery_target_time is None:
        print("Missing or Invalid recovery_target_time format. Please provide the time in 'YYYY-MM-DD HH:MM:SS' format.")
        sys.exit(1)  # Exit the script if the input format is invalid
    try:
        # Parse the input time string to a datetime objecti
        recovery_time_obj = datetime.strptime(recovery_target_time, "%Y-%m-%d %H:%M:%S")
        # Format the datetime object to the required format
        formatted_time = recovery_time_obj.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_time
    except ValueError:
        # Handle invalid input format
        print("Invalid recovery_target_time format. Please provide the time in 'YYYY-MM-DD HH:MM:SS' format.")
        sys.exit(1)  # Exit the script if the input format is invalid

def restore(backup_label=None, recovery_target_time=None):
    """
    Restore a database cluster.

    :param backup_label: The backup label to use for creating the replica. If not specified, the latest backup will be used.
    :type backup_label: str, optional

    :param recovery_target_time: The target time for point-in-time recovery (PITR). This allows the replica to be restored to a specific point in time, rather than the state at the time of the backup.
    :type recovery_target_time: str, optional.

    :return: None
    """
    pass

    config = fetch_backup_config()
    print ("Checking restore path directory and permissions")
    path_check, directory_existed = check_restore_path(config["RESTORE_PATH"])
    if not path_check:
        print ("Failed")
        return

    rpath = config["RESTORE_PATH"]
    data_dir = rpath + "/data/"

    # Construct the restore command
    command = [
        config["BACKUP_TOOL"],
        "restore",
        "--stanza", config["STANZA"],
        "--pg1-path", data_dir
    ]

    # Append --delta if the directory existed and is writable
    if directory_existed:
        command.append("--delta")

    # Extend command based on `backup_label` and `recovery_target_time`
    if config["BACKUP_TOOL"] == "pgbackrest":
        if backup_label:
            command.append("--set={}".format(backup_label))
        if recovery_target_time:
            formatted_time = format_recovery_target_time(recovery_target_time)
            print(formatted_time)
            command.append(f"--type=time")
            command.append(f"--target={formatted_time}")

    run_command(command)
    print("Restoration completed successfully.")

def _configure_pitr(stanza, recovery_target_time=None):
    config = fetch_backup_config()
    conf_file = os.path.join(config["RESTORE_PATH"], "data/postgresql.conf")
    logDir= config["RESTORE_PATH"] + "/log/"
    change_pgconf_keyval(conf_file, "port", "5433")
    change_pgconf_keyval(conf_file, "log_directory", logDir)
    change_pgconf_keyval(conf_file, "archive_command", "")
    change_pgconf_keyval(conf_file, "archive_mode", "off")
    change_pgconf_keyval(conf_file, "hot_standby", "on")
    change_pgconf_keyval(conf_file, "recovery_target_action", "promote",)

def change_pgconf_keyval(config_path, key, value):
    key_found = False
    new_lines = []
    with open(config_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            # Check if the line starts with the key
            if line.strip().startswith(key):
                new_lines.append(f"{key} = '{value}'\n")
                key_found = True
            else:
                new_lines.append(line)
    if not key_found:
        new_lines.append(f"{key} = '{value}'\n")

    with open(config_path, 'w') as file:
        file.writelines(new_lines)

def _configure_replica():
    config = fetch_backup_config()
    stanza = config["STANZA"]
    conf_file = os.path.join(config["RESTORE_PATH"] + "/data/", "postgresql.conf")
    standby_signal_path = os.path.join(config["RESTORE_PATH"] + "/data/", "standby.signal")
    logDir= config["RESTORE_PATH"] + "/log/"
    # Connection info for the primary server
    primary_conninfo = f"host={config['PRIMARY_HOST']} port={config['PRIMARY_PORT']} user={config['PRIMARY_USER']} password={config['REPLICA_PASSWORD']}"

    change_pgconf_keyval(conf_file, "primary_conninfo", primary_conninfo)
    change_pgconf_keyval(conf_file, "hot_standby", "on")
    change_pgconf_keyval(conf_file, "port", "5433")
    change_pgconf_keyval(conf_file, "log_directory", logDir)
    change_pgconf_keyval(conf_file, "archive_command", "")
    change_pgconf_keyval(conf_file, "archive_mode", "off")

    with open(standby_signal_path, "w") as _:
        pass

    print("Configurations modified to configure as replica. Ensure the PostgreSQL instance is restarted to apply these changes.")


def pitr(backup_label=None, recovery_target_time=None):
    """
    Perfomr point-in-time recovery.

    :param backup_label: The backup label to use for creating the replica. If not specified, the latest backup will be used.
    :type backup_label: str, optional

    :param recovery_target_time: The target time for point-in-time recovery (PITR). This allows the replica to be restored to a specific point in time, rather than the state at the time of the backup.
    :type recovery_target_time: str, optional.

    :return: None
    """
    pass

    rtt = format_recovery_target_time(recovery_target_time)
    config = fetch_backup_config()
    restore(backup_label, recovery_target_time)
    _configure_pitr(config["STANZA"], recovery_target_time)

def create_replica(backup_label=None, recovery_target_time=None, do_backup=False):
    """
    Create a replica by restoring from a backup and configure it.

    :param backup_label: The backup label to use for creating the replica. If not specified, the latest backup will be used.
    :type backup_label: str, optional

    :param recovery_target_time: The target time for point-in-time recovery (PITR). This allows the replica to be restored to a specific point in time, rather than the state at the time of the backup.
    :type recovery_target_time: str, optional

    :param do_backup: Whether to initiate a new backup before creating the replica. This can be used to ensure that the replica is as up-to-date as possible by creating a fresh backup from the primary before beginning the restoration process.
    :type do_backup: bool, optional

    :return: None
    """
    pass

    # If do_backup is True, initiate a backup before proceeding
    if do_backup:
      backup("full")

    restore(backup_label, recovery_target_time)

    # Configure the PostgreSQL instance as a replica
    _configure_replica()

def list_backups():
    """
    List backups using the configured backup tool.
    """
    config = fetch_backup_config()
    if config["BACKUP_TOOL"] == "pgbackrest":
        try:
            # Execute the pgbackrest info command with JSON output format
            command_output = subprocess.check_output([config["BACKUP_TOOL"], "info", "--output=json"],
                                                     stderr=subprocess.STDOUT, universal_newlines=True)
            backups_info = json.loads(command_output)

            # Prepare table data from backups info
            backup_table = []
            for stanza_info in backups_info:
                for backup in stanza_info.get('backup', []):
                    backup_details = [
                        stanza_info['name'],  # Stanza Name
                        backup.get('label', 'N/A'),  # Backup Label
                        datetime.utcfromtimestamp(backup['timestamp']['start']).strftime('%Y-%m-%d %H:%M:%S'),  # Start Time
                        datetime.utcfromtimestamp(backup['timestamp']['stop']).strftime('%Y-%m-%d %H:%M:%S'),  # End Time
                        backup.get('lsn', {}).get('start', 'N/A'),  # WAL Start
                        backup.get('lsn', {}).get('stop', 'N/A'),  # WAL End
                        backup.get('type', 'N/A'),  # Backup Type
                        f"{backup.get('info', {}).get('size', 0) / (1024**3):.2f} GB"  # Backup Size in GB
                    ]
                    backup_table.append(backup_details)

            # Print the backup table
            headers = ["Stanza Name", "Label", "Start Time", "End Time", "WAL Start", "WAL End", "Backup Type", "Size (GB)"]
            print(tabulate(backup_table, headers=headers, tablefmt="grid"))

        except subprocess.CalledProcessError as e:
            print(f"Error executing {config['BACKUP_TOOL']} info command:", e.output)
        except KeyError as ke:
            print(f"Error processing JSON data from {config['BACKUP_TOOL']}:", ke)
    else:
        print(f"The backup tool '{config['BACKUP_TOOL']}' does not support listing backups through this script.")


def print_config():
    """
    List configuration parameter configured backup tool.
    """
    config = fetch_backup_config()
    bold_start = "\033[1m"
    bold_end = "\033[0m"
    max_key_length = max(len(key) for key in config.keys())
    max_value_length = max(len(value) for value in config.values())
    line_length = max_key_length + max_value_length + 4  # Including spaces around colon

    # Print the top border
    print(bold_start + "#" * (line_length + 4) + bold_end)  # Adjusting for padding

    for key, value in config.items():
        # Right-align the key, align colons vertically, and ensure values are left-aligned
        if key == "REPLICA_PASSWORD":
            val = "******"
            print(bold_start + f"# {key.rjust(max_key_length)}" + bold_end + f": {val.ljust(max_value_length)}")
        else:
          print(bold_start + f"# {key.rjust(max_key_length)}" + bold_end + f": {value.ljust(max_value_length)}")

    # Print the bottom border
    print(bold_start + "#" * (line_length + 4) + bold_end)  # Adjusting for padding

def run_external_command(*args):
    """
    Run pgbackrest with the given arguments.

    Example:  ./pgedge backrest command info
    """
    # Prepend 'pgbackrest' to the command arguments
    command = ["pgbackrest"] + list(args)
    try:
        # Execute the command and capture the output
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # If the command was successful, print the stdout
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        # If an error occurred, print the stderr
        print(f"Error executing command: {e.stderr}")

def create_stanza():
    """
    Create the required stanza data.
    """
    config = fetch_backup_config()
    try:
        command = [
            "pgbackrest",
            "--stanza=" + util.get_value("BACKUP", "STANZA"),
            "--pg1-path=" + util.get_value("BACKUP", "PG_PATH"),
            #"--pg1-host=" + util.get_value("BACKUP", "PRIMARY_HOST"),
            "--pg1-port=" + util.get_value("BACKUP", "PRIMARY_PORT"),
            "--pg1-user=" + util.get_value("BACKUP", "PRIMARY_USER"),
            "--pg1-socket-path=" + util.get_value("BACKUP", "PG_SOCKET_PATH"),
            "--repo1-cipher-type=" + util.get_value("BACKUP", "REPO_CIPHER_TYPE"),
            "--repo1-path=" + util.get_value("BACKUP", "REPO_PATH"),
            "--log-level-console=info",
            "--log-level-file=info",
            "stanza-create"
        ]
        # Adding repository type specific configurations
        if config["REPO1_TYPE"] == "s3":
            command.extend([
                "--repo1-type", "s3",
                "--repo1-s3-bucket", config["S3_BUCKET"],
                "--repo1-s3-region", config["S3_REGION"],
                "--repo1-s3-endpoint", config["S3_ENDPOINT"],
            ])
        elif config["REPO1_TYPE"] == "posix":
            command.extend(["--repo1-path", config["REPO_PATH"]])
        subprocess.run(command, check=True)
        print("Stanza created successfully.")
    except subprocess.CalledProcessError as e:
        print("Error creating stanza:", e)

if __name__ == "__main__":
    fire.Fire({
        "backup": backup,
        "restore": restore,
        "pitr": pitr,
        "create-stanza": create_stanza,
        "create-replica": create_replica,
        "list-backups": list_backups,
        "config": print_config,
        "command": run_external_command,
    })

