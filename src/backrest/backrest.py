#!/usr/bin/env python3

# Copyright 2022-2024 PGEDGE All rights reserved.

import subprocess
import json
from tabulate import tabulate
from datetime import datetime
import fire
import sys
import os

base_dir = "cluster"

def pgedge_create_replica(stanza, restore_path, backup_id, primary_host='127.0.0.1', primary_port='5432', primary_user='postgres', replica_password=None, recovery_target_time=None):
    """ 
    pgedge: Create read-only replica, with an option for PITR
    Usage: pgedge backrest create-replica --stanza=stanza --restore-path=<path> --set=<id> [--primary-host=<ip>] [--primary-port=<port>] [primary--user=<user>] [--replica-password=<password>] [--recovery-target-time=<time>]
    
    :param stanza: The pgBackRest stanza name.
    :param restore_path: Path where PostgreSQL should be restored to create the replica.
    :param backup_id: Label of the pgBackRest backup to use for restoration.
    :param primary_host: IP address of the primary PostgreSQL server. Default is '127.0.0.1'.
    :param primary_port: Port of the primary PostgreSQL server. Default is '5432'.
    :param primary_user: User for the replication connection. Default is 'postgres'.
    :param replica_password: Password for the replication user. Optional.
    :param recovery_target_time: The target time for the PITR, in a format recognized by PostgreSQL (e.g., 'YYYY-MM-DD HH:MI:SS'). Optional.
    """
    restore_command = ["pgbackrest", "--stanza", stanza, "restore", "--delta",
                        "--set", backup_id, "--pg1-path", restore_path]

    # If a recovery target time is specified, add PITR options
    if recovery_target_time:
        restore_command += ["--type", "time", "--target", recovery_target_time]

    # Step 1: Restore the backup, with optional PITR
    try:
        subprocess.run(restore_command, check=True)
        print(f"Backup {backup_id} successfully restored to {restore_path}.")
        if recovery_target_time:
            print(f"Point-In-Time Recovery to {recovery_target_time} applied.")
    except subprocess.CalledProcessError as e:
        print(f"Error restoring backup {backup_id}: {e}")
        return

    # Step 2: Modify postgresql.conf to configure as replica for PostgreSQL 16
    postgresql_conf_path = os.path.join(restore_path, "postgresql.conf")
    # Construct primary_conninfo with provided details
    primary_conninfo = f"host={primary_host} port={primary_port} user={primary_user}"
    if replica_password:
        primary_conninfo += f" password={replica_password}"
    
    try:
        with open(postgresql_conf_path, "a") as conf_file:
            conf_file.write("\n# Replica settings for PostgreSQL\n")
            conf_file.write("\nport=5433\n")
            conf_file.write(f"primary_conninfo = '{primary_conninfo}'\n")
            # Create standby.signal file
            standby_signal_path = os.path.join(restore_path, "standby.signal")
            with open(standby_signal_path, 'w') as signal_file:
                signal_file.write("")  # Just need to create the file
        print("Configurations modified to configure as replica. standby.signal file created.")
        print("Make sure your pg_hba.conf is configured to allow connection from this IP")
    except Exception as e:
        print(f"Error modifying replica configuration: {e}")

def pgedge_service_status():
    """
    pgedge: Check service status.
    Usage: pgedge backrest service-status
    """
    try:
        # Run a command to check the status of the backrest service
        subprocess.run(["systemctl", "status", "backrest.service"], check=True)
    except subprocess.CalledProcessError as e:
        # If the command fails, print the error message
        print("Error checking service status:", e)

def pgedge_service_log():
    """
    pgedge: Get remote service log.
    Usage: pgedge backrest service-log
    """
    try:
        # Run a command to retrieve the log of the backrest service
        subprocess.run(["journalctl", "-u", "backrest.service"], check=True)
    except subprocess.CalledProcessError as e:
        # If the command fails, print the error message
        print("Error retrieving service log:", e)

def pgedge_list_backups():
    """
    pgedge: List dynamic stanza name, start time, end time, WAL start, and WAL end using pgbackrest info command.
    Usage: pgedge backrest list-backups
    """
    try:
        # Run pgbackrest info command and capture its output as JSON
        output = subprocess.check_output(["pgbackrest", "info", "--output=json"], stderr=subprocess.STDOUT, universal_newlines=True)
        json_output = json.loads(output)
        stanza_info = json_output[0]  # Assuming there's at least one stanza
        stanza_name = stanza_info['name']  # Dynamically get the stanza name
        backups_info = stanza_info['backup']  # Extract the list of backups

        # Extract necessary information for each backup
        backup_table = []
        for backup in backups_info:
            try:
                start_time_unix = backup['timestamp']['start']
                end_time_unix = backup['timestamp']['stop']
                wal_start = backup['lsn']['start']
                wal_end = backup['lsn']['stop']
                backup_type = backup['type']
                backup_label = backup['label']
                backup_size = backup['info']['size']
                # Assuming the backup UUID is part of the label. Extracting it from there.
                # In this example, backup_label is used as is, assuming it includes the UUID.

                # Convert start and end time from UNIX timestamp to actual date and time
                # Modifying the date format to MM-DD-YYYY HH:MM:SS
                start_time = datetime.utcfromtimestamp(start_time_unix).strftime('%d-%m-%Y %H:%M:%S')
                end_time = datetime.utcfromtimestamp(end_time_unix).strftime('%d-%m-%Y %H:%M:%S')
            except KeyError as e:
                # If a KeyError occurs, set the corresponding value to "null"
                print(f"Warning: Missing field - {e}")
                start_time = end_time = wal_start = wal_end = backup_type = backup_label = backup_size = "null"

            backup_table.append([stanza_name, backup_label, start_time, end_time, wal_start, wal_end, backup_type, backup_size])

        # Print the table
        headers = ["Stanza Name", "Label","Start Time", "End Time", "WAL Start", "WAL End", "Backup Type", "Size"]
        print(tabulate(backup_table, headers=headers, tablefmt="grid"))
    except subprocess.CalledProcessError as e:
        # If the command fails, print the error message
        print("Error executing pgbackrest info command:", e.output)
    except KeyError as ke:
        # If there's a KeyError, print the error message and provide information about the JSON structure
        print("Error accessing JSON data:", ke)
        print("Ensure that the JSON structure matches the expected format.")


def pgbackrest_annotate():
    """
    Add or modify backup annotation.
    pgedge backrest  annotate
    """
    call_pgbackrest("annotate")

def pgbackrest_archive_get():
    """
    Get a WAL segment from the archive.
    pgedge backrest  archive-get
    """
    call_pgbackrest("archive-get")

def pgbackrest_archive_push():
    """
    Push a WAL segment to the archive.
    pgedge backrest  archive-push
    """
    call_pgbackrest("archive-push")

def pgbackrest_backup():
    """
    Backup a database cluster.
    pgedge backrest  backup
    """
    call_pgbackrest("backup")

def pgbackrest_check():
    """
    Check the configuration.
    pgedge backrest  check
    """
    call_pgbackrest("check")

def pgbackrest_expire():
    """
    Expire backups that exceed retention.
    pgedge backrest  expire
    """
    call_pgbackrest("expire")

def pgbackrest_info():
    """
    Retrieve information about backups.
    pgedge backrest  info
    """
    call_pgbackrest("info")

def pgbackrest_repo_get():
    """
    Get a file from a repository.
    pgedge backrest  repo-get
    """
    call_pgbackrest("repo-get")

def pgbackrest_repo_ls():
    """
    List files in a repository.
    pgedge backrest  repo-ls
    """
    call_pgbackrest("repo-ls")

def pgbackrest_server():
    """
    pgBackRest server.
    pgedge backrest  server
    """
    call_pgbackrest("server")

def pgbackrest_server_ping():
    """
    Ping pgBackRest server.
    pgedge backrest  server-ping
    """
    call_pgbackrest("server-ping")

def pgbackrest_stanza_create():
    """
    Create the required stanza data.
    pgedge backrest  stanza-create
    """
    call_pgbackrest("stanza-create")

def pgbackrest_stanza_delete():
    """
    Delete a stanza.
    pgedge backrest  stanza-delete
    """
    call_pgbackrest("stanza-delete")

def pgbackrest_stanza_upgrade():
    """
    Upgrade a stanza.
    pgedge backrest  stanza-upgrade
    """
    call_pgbackrest("stanza-upgrade")

def pgbackrest_start():
    """
    Allow pgBackRest processes to run.
    pgedge backrest  start
    """
    call_pgbackrest("start")

def pgbackrest_stop():
    """
    Stop pgBackRest processes from running.
    pgedge backrest  stop
    """
    call_pgbackrest("stop")

def pgbackrest_verify():
    """
    Verify contents of the repository.
    pgedge backrest  verify
    """
    call_pgbackrest("verify")

def pgbackrest_version():
    """
    Get version.
    pgedge backrest  version
    """
    call_pgbackrest("version")

def call_pgbackrest(command):
    """
    Call pgbackrest with provided command.
    """
    try:
        # Form the command to execute pgbackrest with provided command
        full_command = ["pgbackrest", command]
        # Execute the command
        subprocess.run(full_command, check=True)
    except subprocess.CalledProcessError as e:
        # If the command fails, print the error message
        print(f"Error executing pgbackrest command '{command}':", e.output)

if __name__ == "__main__":
    # Create a Fire instance with the dictionary of commands
    fire_dict = {
        "create-replica": pgedge_create_replica,
        "service-log": pgedge_service_log,
        "service-status": pgedge_service_status,
        "list-backups": pgedge_list_backups,
        "annotate": pgbackrest_annotate,
        "archive-get": pgbackrest_archive_get,
        "archive-push": pgbackrest_archive_push,
        "backup": pgbackrest_backup,
        "check": pgbackrest_check,
        "expire": pgbackrest_expire,
        "info": pgbackrest_info,
        "repo-get": pgbackrest_repo_get,
        "repo-ls": pgbackrest_repo_ls,
        "server": pgbackrest_server,
        "server-ping": pgbackrest_server_ping,
        "stanza-create": pgbackrest_stanza_create,
        "stanza-delete": pgbackrest_stanza_delete,
        "stanza-upgrade": pgbackrest_stanza_upgrade,
        "start": pgbackrest_start,
        "stop": pgbackrest_stop,
        "verify": pgbackrest_verify,
        "version": pgbackrest_version
    }

    fire.Fire(fire_dict)

