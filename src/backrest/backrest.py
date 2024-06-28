#!/usr/bin/env python3
import subprocess
import os
import fire
import util
import utilx
import json
import sys
from datetime import datetime
from tabulate import tabulate

def pgV():
    """Return the first found PostgreSQL version (pg14, pg15, or pg16)."""
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

def fetch_config():
    """Fetch and return the configuration from system settings."""
    config = {}
    params = [
        "stanza","restore_path", "backup-type", "repo1-retention-full", 
        "repo1-retention-full-type", "repo1-path", "repo1-host-user", 
        "repo1-host", "repo1-cipher-type", "log-level-console", 
        "repo1-type", "process-max", "compress-level", "pg1-path", 
        "pg1-user", "pg1-database", "db-socket-path", "pg1-port", 
        "pg1-host"
    ]
    for param in params:
        config[param] = util.get_value("BACKUP", param)
    return config

def show_config():
    """Display the current configuration."""
    config = fetch_config()
    max_key_length = max(len(key) for key in config)
    print("#" * (max_key_length + 40))
    for key, value in config.items():
        print(f"{key.ljust(max_key_length + 1)}= {value}")
    print("#" * (max_key_length + 40))

def backup(stanza, type="full", verbose=True):
    """Perform a backup of a database cluster."""
    config = fetch_config()
    valid_types = ["full", "diff", "incr"]

    # Check if backup type is valid
    if type not in valid_types:
        utilx.echo_message(
            f"Error: '{type}' is not valid.\nAllowed types: "
            f"{', '.join(valid_types)}.",
            level="error"
        )
        return

    # Mandatory configuration keys
    mandatory_keys = ['repo1-path', 'pg1-path']

    # Check if mandatory keys are present in config
    for key in mandatory_keys:
        if key not in config or not config[key]:
            utilx.echo_message(
                f"Error: Missing mandatory config value: {key}",
                level="error"
            )
            return

    command = [
        "pgbackrest", 
        "--stanza", stanza, 
        "--type", type,
        "--repo1-type", config['repo1-type'],
        "--pg1-path", config['pg1-path'], 
        "--repo1-path", config['repo1-path'],
        "--db-socket-path", config['db-socket-path'], 
        "backup"
    ]

    # Optional configuration keys
    optional_keys = [
        'repo1-retention-full', 'repo1-retention-full-type', 
        'repo1-cipher-type', 'log-level-console', 'process-max', 'compress-level'
    ]

    # Add optional keys to the command if they are available in config
    for key in optional_keys:
        if key in config and config[key]:
            command.extend([f"--{key.replace('_', '-')}", config[key]])

    result = utilx.run_command(command, capture_output=not verbose)
    if not result["success"]:
        utilx.echo_message(
            f"Error: failed to take {type} backup",
            level="error"
        )

def restore(stanza, data_dir=None, backup_label=None, recovery_target_time=None, verbose=True):
    """Restore a database cluster to a specified state."""
    config = fetch_config()

    # Mandatory configuration keys
    mandatory_keys = ['restore_path', 'pg1-path', 'repo1-type']

    # Check if mandatory keys are present in config
    for key in mandatory_keys:
        if key not in config or not config[key]:
            utilx.echo_message(f"Error: Missing mandatory config value: {key}", level="error")
            return

    if data_dir is None:
        data_dir = os.path.join(config["restore_path"], stanza, "data")

    status = utilx.check_directory_status(data_dir)
    if status['exists'] and not status['writable']:
        util.message(status['message'])
        return

    command = [
        "pgbackrest", "--stanza", stanza, "restore", 
        "--pg1-path", data_dir
    ]

    if status['exists']:
        command.append("--delta")
    if backup_label:
        command.append(f"--set={backup_label}")
    if recovery_target_time:
        command.extend(["--type=time", f"--target={recovery_target_time}"])

    # Optional configuration keys
    optional_keys = [
        'repo1-cipher-type', 
        'log-level-console', 'process-max', 'repo1-type'
    ]

    # Add optional keys to the command if they are available in config
    for key in optional_keys:
        if key in config and config[key]:
            command.extend([f"--{key.replace('_', '-')}", config[key]])

    result = utilx.run_command(command, capture_output=not verbose)
    if not result["success"]:
        utilx.echo_message(f"Error: failed to restore backup", level="error")
        return False

    return True

def pitr(stanza, data_dir=None, recovery_target_time=None, verbose=True):
    """Perform point-in-time recovery on a database cluster."""
    if restore(stanza, data_dir, None, recovery_target_time, verbose):
        _configure_pitr(stanza, data_dir, recovery_target_time)

def _configure_pitr(stanza, pg_data_dir=None, recovery_target_time=None):
    """Configure PostgreSQL for point-in-time recovery."""
    config = fetch_config()
    if pg_data_dir is None:
        pg_data_dir = os.path.join(config["restore_path"], stanza, "data")
    if recovery_target_time is None:
        recovery_target_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    config_file = os.path.join(pg_data_dir, "postgresql.conf")
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
    """Create a replica by restoring from a backup."""
    if restore(stanza, data_dir, backup_label, verbose=verbose):
        configure_replica_local(stanza, data_dir)

def configure_replica(stanza, pg1_path, pg1_host, pg1_port, pg1_user):
    """Configure a PostgreSQL replica."""
    conf_file = os.path.join(pg1_path, "postgresql.conf")
    standby_signal = os.path.join(pg1_path, "standby.signal")
    primary_conninfo = f"host={pg1_host} port={pg1_port} user={pg1_user}"
    changes = {
        "hot_standby": "on",
        "primary_conninfo": primary_conninfo,
        "port": pg1_port,
        "log_directory": os.path.join(pg1_path, "log"),
        "archive_command": "cd .",
        "archive_mode": "on"
    }
    for key, value in changes.items():
        change_pgconf_keyval(conf_file, key, value)
    open(standby_signal, 'a').close()

def configure_replica_local(stanza):
    """Configure a local PostgreSQL replica."""
    config = fetch_config()
    pg1_path = os.path.join(config["restore_path"], stanza, "data")
    pg1_host = config['repo1-host']
    pg1_port = config['pg1-port']
    pg1_user = config['pg1-user']
    configure_replica(stanza, pg1_path, pg1_host, pg1_port, pg1_user)

def list_backups():
    """List all available backups using pgBackRest."""
    config = fetch_config()

    # Mandatory configuration keys
    mandatory_keys = ['stanza', 'repo1-path']

    # Check if mandatory keys are present in config
    for key in mandatory_keys:
        if key not in config or not config[key]:
            utilx.echo_message(f"Error: Missing mandatory config value: {key}", level="error")
            return

    command = ["pgbackrest", "info", "--output=json", "--stanza", config['stanza']]

    # Optional configuration keys
    optional_keys = [
        'repo1-path', 'repo1-type', 
        'repo1-cipher-type', 'log-level-console'
    ]

    # Add optional keys to the command if they are available in config
    for key in optional_keys:
        if key in config and config[key]:
            command.extend([f"--{key.replace('_', '-')}", config[key]])
    print(command)

    try:
        command_output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, text=True
        )
        backups_info = json.loads(command_output)
        backup_table = []

        for stanza_info in backups_info:
            for backup in stanza_info.get('backup', []):
                backup_details = [
                    stanza_info['name'],
                    backup.get('label', 'N/A'),
                    datetime.utcfromtimestamp(
                        backup['timestamp']['start']
                    ).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.utcfromtimestamp(
                        backup['timestamp']['stop']
                    ).strftime('%Y-%m-%d %H:%M:%S'),
                    backup.get('type', 'N/A'),
                    f"{backup.get('info', {}).get('size', 0) / (1024**3):.2f} GB"
                ]
                backup_table.append(backup_details)

        headers = [
            "Stanza Name", "Label", "Start Time", "End Time", "Type", "Size (GB)"
        ]
        print(tabulate(backup_table, headers=headers, tablefmt="grid"))

    except subprocess.CalledProcessError as e:
        util.message(f"Error executing pgBackRest info command: {e.output}")

def modify_hba_conf():
    """Modify pg_hba.conf for replication."""
    new_rules = [{
        "type": "host",
        "database": "replication",
        "user": "all",
        "address": "127.0.0.1/0",
        "method": "trust"
    }]
    util.update_pg_hba_conf(pgV(), new_rules)

def modify_postgresql_conf(stanza, pg1_path, repo1_path, repo1_type):
    """Modify 'postgresql.conf' to integrate with pgbackrest."""
    aCmd = (
        f"pgbackrest --stanza={stanza} --pg1-path={pg1_path} "
        f"--repo1-type={repo1_type} --repo1-path={repo1_path} "
        f"--repo1-cipher-type=aes-256-cbc archive-push %p"
    )
    util.change_pgconf_keyval(pgV(), "archive_command", aCmd, p_replace=True)
    util.change_pgconf_keyval(pgV(), "archive_mode", "on", p_replace=True)

def run_external_command(command, **kwargs):
    """Execute an external pgBackRest command."""
    full_command = ["pgbackrest", command]
    for key, value in kwargs.items():
        if key and value:
            if not key.startswith('--'):
                key = key.replace('_', '-')
                full_command.append(f"--{key}")
            else:
                full_command.append(key)
            full_command.append(str(value))
        else:
            print(f"Invalid key-value pair ignored: key={key}, value={value}")
    print(f"Full command to be executed: {' '.join(full_command)}")
    try:
        result = subprocess.run(full_command, check=True, text=True, capture_output=True)
        print("Command executed successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e.stderr}")
    except Exception as e:
        print(f"Exception occurred during command execution: {str(e)}")

def create_stanza(stanza, verbose=True):
    """Create the required stanza for pgBackRest."""
    config = fetch_config()

    # Mandatory configuration keys
    mandatory_keys = ['pg1-path', 'repo1-path', 'repo1-type']

    # Check if mandatory keys are present in config
    for key in mandatory_keys:
        if key not in config or not config[key]:
            utilx.echo_message(f"Error: Missing mandatory config value: {key}", level="error")
            return

    command = [
        "pgbackrest", 
        "--stanza", stanza, 
        "--pg1-path", config['pg1-path'], 
        "--repo1-path", config['repo1-path'],
        "--repo1-type", config['repo1-type'], 
        "--db-socket-path", config['db-socket-path'], 
        "stanza-create"
    ]

    # Optional configuration keys
    optional_keys = [
        'repo1-cipher-type', 
        'log-level-console'
    ]

    # Add optional keys to the command if they are available in config
    for key in optional_keys:
        if key in config and config[key]:
            command.extend([f"--{key.replace('_', '-')}", config[key]])

    result = utilx.run_command(command, capture_output=not verbose)
    if not result["success"]:
        utilx.echo_message(
            'Error', 'Failed to create or configure stanza', level="error"
        )
        return

    modify_postgresql_conf(
        stanza, config['pg1-path'], config['repo1-path'], config['repo1-type']
    )
    modify_hba_conf()

    command = ["./pgedge", "restart", pgV()]
    result = utilx.run_command(command, capture_output=not verbose)
    if not result["success"]:
        utilx.echo_message(
            f"Error: failed to restart postgresql cluster", level="error"
        )

if __name__ == "__main__":
    fire.Fire({
        "backup": backup,
        "restore": restore,
        "pitr": pitr,
        "create-stanza": create_stanza,
        "create-replica": create_replica,
        "configure_replica": configure_replica,
        "list-backups": list_backups,
        "show-config": show_config,
        "set_hbaconf": modify_hba_conf,
        "set_postgresqlconf": modify_postgresql_conf,
        "command": run_external_command,
    })

