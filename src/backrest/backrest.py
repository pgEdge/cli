#!/usr/bin/env python3
#     Copyright (c)  2022-2024 PGEDGE  #
import subprocess
import os
import fire
import util
import json
from datetime import datetime
from tabulate import tabulate


def fetch_backup_config():
    """Fetch backup configuration from util module or other configuration source."""
    config = {
        "BACKUP_TOOL": util.get_value("BACKUP", "BACKUP_TOOL"),
        "STANZA": util.get_value("BACKUP", "STANZA"),
        "DATABASE": util.get_value("BACKUP", "DATABASE"),
        "PG_PATH": util.get_value("BACKUP", "PG_PATH"),
        "SOCKET_PATH": util.get_value("BACKUP", "SOCKET_PATH"),
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


def backup(backup_type="full"):
    """Perform a backup using the specified backup tool and backup type, storing the backup at the specified backup path."""
    config = fetch_backup_config()
    allowed_types = ["full", "diff", "incr"]
    if backup_type not in allowed_types:
        print(f"Error: '{backup_type}' is not a valid backup type. Allowed types are: {', '.join(allowed_types)}.")
        return

    command = [
        config["BACKUP_TOOL"], "--type", backup_type, "backup",
        "--stanza", config["STANZA"],
        "--pg1-path", config["PG_PATH"],
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

def restore(backup_id=None, recovery_target_time=None):
    """
    Restore a PostgreSQL database from a backup.

    Args:
        backup_id (str, optional): Specific backup ID to restore from. If not provided,
                                   the latest backup will be used.
        recovery_target_time (str, optional): Specific point in time to restore to,
                                               useful for point-in-time recovery (PITR).
                                               Must be a string in a format recognized by PostgreSQL.
    """ 
    config = fetch_backup_config()
    path_check, directory_existed = check_restore_path(config["RESTORE_PATH"])
    if not path_check:  # No permission or failed to create directory
        return  # Exit function without attempting to restore
    
    # Construct the restore command
    command = [
        config["BACKUP_TOOL"],
        "restore",
        "--stanza", config["STANZA"],
        "--pg1-path", config["RESTORE_PATH"]
    ]
    
    # Append --delta if the directory existed and is writable
    if directory_existed:
        command.append("--delta")
    
    # Extend command based on `backup_id` and `recovery_target_time`
    if config["BACKUP_TOOL"] == "pgbackrest":
        if backup_id:
            command.append("--set={}".format(backup_id))
        if recovery_target_time:
            command.extend(["--type=time", "--target={}".format(recovery_target_time)])
    
    run_command(command)
    print("Restoration completed successfully.")

def modify_postgresql_conf(stanza):
     """
     Modify 'postgresql.conf' to integrate with pgBackRest.
     """
     aCmd = f"pgbackrest --stanza={stanza} archive-push %p"
     util.change_pgconf_keyval(stanza, "archive_command", aCmd, p_replace=True)
     util.change_pgconf_keyval(stanza, "archive_mode", "on", p_replace=True)

def _configure_replica(operation_type='replica'):
    config = fetch_backup_config()
    postgresql_conf_path = os.path.join(config["RESTORE_PATH"], "postgresql.conf")
    standby_signal_path = os.path.join(config["RESTORE_PATH"], "standby.signal")

    # Connection info for the primary server
    primary_conninfo = f"host={config['PRIMARY_HOST']} port={config['PRIMARY_PORT']} user={config['PRIMARY_USER']} password={config['REPLICA_PASSWORD']}"

    with open(postgresql_conf_path, "a") as conf_file:
        conf_file.write("\n# Replica settings\n")
        conf_file.write(f"primary_conninfo = '{primary_conninfo}'\n")
        conf_file.write("hot_standby = on\n")  # Ensure hot standby is enabled for read-only queries on the replica
        conf_file.write("port = 5433\n") 

    # Create an empty standby.signal file to signal the instance to start in standby mode
    # This is crucial for PostgreSQL versions 12 and above
    with open(standby_signal_path, "w") as _:
        pass

    print("Configurations modified to configure as replica. Ensure the PostgreSQL instance is restarted to apply these changes.")


def create_replica(backup_id=None, recovery_target_time=None, do_backup=False):
    """
    Create a replica by restoring from a backup and configure it. If specified, perform PITR.
    Optionally, initiate a backup before creating the replica.

    Args:
        backup_id (str, optional): The ID of the backup to use for creating the replica.
                                   If not provided, the latest backup will be used unless do_backup is True.
        recovery_target_time (str, optional): The target time for PITR.
        do_backup (bool, optional): Whether to initiate a new backup before creating the replica.
                                    Defaults to False.
    """
    config = fetch_backup_config()
    
    # If do_backup is True, initiate a backup before proceeding
    if do_backup:
      backup("full")

    restore(backup_id, recovery_target_time)

    # Configure the PostgreSQL instance as a replica
    _configure_replica(operation_type="pitr" if recovery_target_time else "replica")

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
        if key == bold_start + "REPLICA_PASSWORD" + bold_end:
            val = "******"
            print(f"# {key.rjust(max_key_length)} : {val.ljust(max_value_length)}")
        else:  
          print(bold_start + f"# {key.rjust(max_key_length)}" + bold_end + f": {value.ljust(max_value_length)}")
        
    # Print the bottom border
    print(bold_start + "#" * (line_length + 4) + bold_end)  # Adjusting for padding

def run_external_command(*args):
    """
    Run pgbackrest) with the given arguments.
    Automatically prepends 'pgbackrest' to the arguments.
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

if __name__ == "__main__":
    fire.Fire({
        "backup": backup,
        "restore": restore,
        "create_replica": create_replica,
        "list": list_backups,
        "config": print_config,
        "command": run_external_command,
    })

