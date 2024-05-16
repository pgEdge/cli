#!/usr/bin/env python3
import subprocess
import os
import fire
import util
import time
import utilx
import json
import sys
from datetime import datetime
from tabulate import tabulate

thisDir = os.path.dirname(os.path.realpath(__file__))

def pgV():
    """Return the first found among supported PostgreSQL versions."""
    pg_versions = ["pg14", "pg15", "pg16"]
    for pg_version in pg_versions:
        if os.path.isdir(pg_version):
            return pg_version
    sys.exit("pg14, 15 or 16 must be installed")

def osSys(p_input, p_display=True):
    """Execute a shell command and optionally display it."""
    if p_display:
        util.message("# " + p_input)
    return os.system(p_input)

def fetch_backup_config():
    """Fetch and return the pgbackrest configuration from system settings."""
    config = {
        "main": {},
        "global": {},
        "stanza": {}
    }

    main_params = ["restore_path", "backup-type", "stanza_count"]
    global_params = [
        "repo1-retention-full", "repo1-retention-full-type", "repo1-path", "repo1-host-user", "repo1-host",
        "repo1-cipher-type", "repo1-cipher-pass", "repo1-s3-bucket", "repo1-s3-key-secret", "repo1-s3-key",
        "repo1-s3-region", "repo1-s3-endpoint", "log-level-console", "repo1-type",
        "process-max", "compress-level"
    ]
    stanza_params = [
        "pg1-path", "pg1-user", "pg1-database", "db-socket-path", "pg1-port", "pg1-host"
    ]

    # Fetch main and global parameters
    for param in main_params:
        config["main"][param] = util.get_value("BACKUP", param)
    for param in global_params:
        config["global"][param] = util.get_value("BACKUP", param)

    # Determine the number of stanzas and fetch their specific parameters
    stanza_count = int(config["main"].get("stanza_count", 1))
    for i in range(stanza_count):
        stanza_name = util.get_value("BACKUP", f"stanza{i}")
        config["stanza"][stanza_name] = {}
        for param in stanza_params:
            indexed_param = f"{param}{i}"
            config["stanza"][stanza_name][param] = util.get_value("BACKUP", indexed_param)

    return config

def show_config():
    """Display the current configuration in a readable format."""
    config = fetch_backup_config()  # Fetches the full configuration from wherever it's stored
    max_key_length = max(max(len(key) for key in section) for section in config.values() if section)

    # Print section with adequate formatting based on the maximum key length
    print("#" * (max_key_length + 40))

    main  = config["main"]
    print(f"[main]")
    for key, value in main.items():
        print(f"{key.ljust(max_key_length + 1)}= {value}")

    glob = config["global"]
    print(f"[global]")
    for key, value in glob.items():
        print(f"{key.ljust(max_key_length + 1)}= {value}")

    stanza_count = int(config["main"].get("stanza_count", 1))
    for i in range(stanza_count):
        stanza_name = util.get_value("BACKUP", f"stanza{i}")
        print(f"[{stanza_name}]")
        for key, value in config["stanza"][stanza_name].items():
            clean_key = key.replace(str(i), '') 
            print(f"{clean_key.ljust(max_key_length + 1)}= {value}")
    
    print("#" * (max_key_length + 40))


def save_config(filename="pgbackrest.conf"):
    """Save the current pgbackrest configuration to a file in standard format."""
    config = fetch_backup_config()
    lines = []

    # Write global settings
    if config["global"]:
        lines.append("[global]")
        for key, value in config["global"].items():
            if key == "compress-level":
                continue  # Handle this key separately in its own section
            if value != " ":
                lines.append(f"{key} = {value}")
        lines.append("")  # Add a newline for separation

        # Handle global:archive-push specifically if needed
        if "compress-level" in config["global"]:
            lines.append("[global:archive-push]")
            lines.append(f"compress-level = {config['global']['compress-level']}")
            lines.append("")  # Add a newline for separation

    # Write stanza sections
    stanza_count = int(config["main"].get("stanza_count", 1))
    for i in range(stanza_count):
        stanza_name = util.get_value("BACKUP", f"stanza{i}")
        if stanza_name in config["stanza"]:
            lines.append(f"[{stanza_name}]")
            for key, value in config["stanza"][stanza_name].items():
                clean_key = key.replace(str(i), '')  # Remove the index from key names
                if value != " ":
                    lines.append(f"{clean_key} = {value}")
            lines.append("")  # Add a newline for separation

    # Write the configuration to file
    with open(f"{thisDir}/{filename}", "w") as f:
        f.write("\n".join(lines))
    util.message(f"Configuration saved to {thisDir}/{filename}.")
    osSys(f"sudo cp {thisDir}/{filename} /etc/pgbackrest/")

    return filename

def backup(stanza, type="full", verbose=True):
    """Perform a backup of a database cluster.

    Args:
        stanza (str): The name of the stanza to perform the backup on.
        type (str): The type of backup to perform. Defaults to "full".
                    Allowed types are "full", "diff", and "incr".
    """
    config = fetch_backup_config()
    valid_types = ["full", "diff", "incr"]
    if type not in valid_types:
        utilx.echo_message(f"Error: '{type}' is not a valid backup type.\n allowed types are: {', '.join(valid_types)}.", level = "error")
        return

    command = ["pgbackrest", "--stanza", stanza, "--type", type, "backup"]

    result = utilx.run_command(command, capture_output = not verbose)
    if result["success"] == False:
        utilx.echo_message(f"Error: failed to take {type} backup", level = "error")

def restore(stanza, data_dir=None, backup_label=None, recovery_target_time=None, verbose=True):
    """Restore a database cluster to a specified state."""
    
    config = fetch_backup_config()
    if data_dir == None:
        data_dir = os.path.join(config["main"]["restore_path"], stanza, "data")

    status = utilx.check_directory_status(data_dir)
    if status['exists'] and not status['writable']:
        util.message(status['message'])
        return

    command = ["pgbackrest", "--stanza", stanza, "restore", "--pg1-path", data_dir]

    if status['exists']:
        command.append("--delta")
    
    if backup_label:
        command.append(f"--set={backup_label}")

    if recovery_target_time:
        command.append("--type=time")
        command.append(f"--target={recovery_target_time}")

    result = utilx.run_command(command, capture_output = not verbose)
    if result["success"] == False:
        utilx.echo_message(f"Error: failed to restore backup", level = "error")
    return True

def pitr(stanza, data_dir=None, recovery_target_time=None, verbose=True):
    """Perform point-in-time recovery on a database cluster."""
    if restore(stanza, data_dir=None, backup_label = None, recovery_target_time=recovery_target_time, verbose=verbose) == True:
        _configure_pitr(stanza, data_dir, recovery_target_time)

def _configure_pitr(stanza, pg_data_dir=None, recovery_target_time=None):
    """Configure PostgreSQL for point-in-time recovery."""
    config = fetch_backup_config()
    if pg_data_dir == None:
        pg_data_dir = os.path.join(config["main"]["restore_path"], stanza, "data")

    if recovery_target_time is None:
        recovery_target_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    config_file = os.path.join(pg_data_dir, "postgresql.conf")

    # Configuration changes for PITR
    changes = {
        "port": "5433",
        "log_directory": os.path.join(pg_data_dir, "log"),
        "archive_command": "",
        "archive_mode": "off",
        "hot_standby": "on",
        "recovery_target_time": recovery_target_time,
        "recovery_target_action": "promote"
    }

    for key, value in changes.items():
        change_pgconf_keyval(config_file, key, value)

def change_pgconf_keyval(config_path, key, value):
    """Edit a key-value pair in the PostgreSQL configuration file."""
    key_found = False
    with open(config_path, 'r') as file:
        lines = file.readlines()
    with open(config_path, 'w') as file:
        for line in lines:
            if line.strip().startswith(key):
                file.write(f"{key} = '{value}'\n")
                key_found = True
            else:
                file.write(line)
        if not key_found:
            file.write(f"{key} = '{value}'\n")

def create_replica(stanza, data_dir=None, backup_label=None, verbose=True):
    """Create a replica by restoring from a backup and configure it as a standby server."""
    if restore(stanza, data_dir, backup_label, recovery_target_time=None, verbose=verbose) == True:
        _configure_replica(stanza, data_dir, verbose)

def _configure_replica(stanza, pg_data_dir=None, verbose=True):
    """Configure PostgreSQL to run as a replica (standby server)."""
    config = fetch_backup_config()

    if pg_data_dir == None:
        pg_data_dir = os.path.join(config["main"]["restore_path"], stanza, "data")
    
    conf_file = os.path.join(pg_data_dir, "postgresql.conf")
    standby_signal = os.path.join(pg_data_dir, "standby.signal")

    # Connection info for the primary server should be configured prior to calling this function
    primary_conninfo = f"host={config['global']['repo1-host']} port={config['stanza'][stanza]['pg1-port']} user={config['stanza'][stanza]['pg1-user']}"
   
    # Configure postgresql.conf for replica
    changes = {
        "hot_standby": "on",
        "primary_conninfo": primary_conninfo,
        "port": f"{config['stanza'][stanza]['pg1-port']}",
        "log_directory": os.path.join(pg_data_dir, "log"),
        "archive_command": "cd .",
        "archive_mode": "on"
    }

    for key, value in changes.items():
        change_pgconf_keyval(conf_file, key, value)
    
    # Create an empty standby.signal file to trigger standby mode
    open(standby_signal, 'a').close()

def list_backups():
    """List all available backups using pgBackRest."""
    config = fetch_backup_config()
    try:
        command = ["pgbackrest", "info", "--output=json"]
        command_output = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        backups_info = json.loads(command_output)

        backup_table = []
        for stanza_info in backups_info:
            for backup in stanza_info.get('backup', []):
                backup_details = [
                    stanza_info['name'],
                    backup.get('label', 'N/A'),
                    datetime.utcfromtimestamp(backup['timestamp']['start']).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.utcfromtimestamp(backup['timestamp']['stop']).strftime('%Y-%m-%d %H:%M:%S'),
                    backup.get('type', 'N/A'),
                    f"{backup.get('info', {}).get('size', 0) / (1024**3):.2f} GB"
                ]
                backup_table.append(backup_details)

        headers = ["Stanza Name", "Label", "Start Time", "End Time", "Type", "Size (GB)"]
        print(tabulate(backup_table, headers=headers, tablefmt="grid"))

    except subprocess.CalledProcessError as e:
        util.message(f"Error executing pgBackRest info command: {e.output}")

def modify_hba_conf():
  new_rules = [
      {
          "type": "host",
          "database": "replication",
          "user": "all",
          "address": "127.0.0.1/0",
          "method": "trust"
      }
  ]
  util.update_pg_hba_conf(pgV(), new_rules)

def modify_postgresql_conf(stanza):
    """
    Modify 'postgresql.conf' to integrate with pgbackrest.
    """
    aCmd = f"pgbackrest --stanza={stanza} archive-push %p"
    util.change_pgconf_keyval(pgV(), "archive_command", aCmd, p_replace=True)
    util.change_pgconf_keyval(pgV(), "archive_mode", "on", p_replace=True)

def run_external_command(*args):
    """Execute an external pgBackRest command."""

    command = args
    result = utilx.run_command(command)
    if result["success"]:
        util.message("Command executed successfully.")
    else:
        utilx.ereport('Error', 'Command execution failed', detail=result["error"])

def validate_stanza_config(stanza_name, config):
    """
    Validate that all required parameters for a stanza are set.
    """
    required_params = ["pg1-path", "pg1-user", "pg1-database", "db-socket-path", "pg1-port", "pg1-host"]
    missing_params = [param for param in required_params if not config["stanza"].get(stanza_name, {}).get(param)]
    if missing_params:
        raise ValueError(f"Missing configuration parameters for stanza {stanza_name}: {', '.join(missing_params)}")
    return True

def create_stanza(stanza, verbose=True):
    """
    Create the required stanza for pgBackRest and configure PostgreSQL settings after ensuring all values are properly set.
    """
    # Fetch the current configuration
    config = fetch_backup_config()

    if validate_stanza_config(stanza, config):
        command = ["pgbackrest", "--stanza", stanza, "stanza-create"]
        result = utilx.run_command(command, capture_output = not verbose)
        if result["success"] == False:
            utilx.echo_message('Error', f'Failed to create or configure stanza', level = "error")
        modify_postgresql_conf(stanza)
        modify_hba_conf()
        command = ["./pgedge", "restart", pgV()]
        result = utilx.run_command(command, capture_output = not verbose)
        if result["success"] == False:
            utilx.echo_message(f"Error: failed to restart postgresql cluster", level = "error")

if __name__ == "__main__":
    fire.Fire({
        "backup": backup,
        "restore": restore,
        "pitr": pitr,
        "create-stanza": create_stanza,
        "create-replica": create_replica,
        "list-backups": list_backups,
        "show-config": show_config,
        "save-config": save_config,
        "command": run_external_command,
    })

