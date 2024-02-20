#!/usr/bin/env python3

# Copyright 2022-2024 PGEDGE All rights reserved.

import subprocess
import json
from tabulate import tabulate
from datetime import datetime
import fire
import sys

base_dir = "cluster"

def pgedge_create_stanza():
    """
    pgedge: Add or modify backup annotation.
    Usage: pgedge backrest create-stanza
    """
    # Add logic here to create a stanza
    pass

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
    pgedge: List stanza name, start time, end time, WAL start, and WAL end using pgbackrest info command.
    Usage: pgedge backrest list-backups
    """
    try:
        # Run pgbackrest info command and capture its output as JSON
        output = subprocess.check_output(["pgbackrest", "info", "--output=json"], stderr=subprocess.STDOUT, universal_newlines=True)
        backups_info = json.loads(output)[0]['backup']  # Extract the list of backups

        # Extract necessary information for each backup
        backup_table = []
        for backup in backups_info:
            try:
                stanza_name = "pg16"  # Assuming the stanza name is always "pg16" based on the provided JSON
                start_time_unix = backup['timestamp']['start']
                end_time_unix = backup['timestamp']['stop']
                wal_start = backup['lsn']['start']
                wal_end = backup['lsn']['stop']
                backup_type = backup['type']
                backup_label = backup['label']
                backup_size = backup['info']['size']

                # Convert start and end time from UNIX timestamp to actual date and time
                start_time = datetime.utcfromtimestamp(start_time_unix).strftime('%Y-%m-%d %H:%M:%S')
                end_time = datetime.utcfromtimestamp(end_time_unix).strftime('%Y-%m-%d %H:%M:%S')
            except KeyError as e:
                # If a KeyError occurs, set the corresponding value to "null"
                print(f"Warning: Missing field - {e}")
                stanza_name = start_time = end_time = wal_start = wal_end = backup_type = backup_label = backup_size = "null"

            backup_table.append([stanza_name, start_time, end_time, wal_start, wal_end, backup_type, backup_label, backup_size])

        # Print the table
        headers = ["Stanza Name", "Start Time", "End Time", "WAL Start", "WAL End", "Backup Type", "Label", "Size"]
        print(tabulate(backup_table, headers=headers, tablefmt="grid"))
    except subprocess.CalledProcessError as e:
        # If the command fails, print the error message
        print("Error executing pgbackrest info command:", e.output)
    except KeyError as ke:
        # If there's a KeyError, print the error message and provide information about the JSON structure
        print("Error accessing JSON data:", ke)
        print("Ensure that the JSON structure matches the expected format.")



def pgedge_pitr(pitr_json_file):
    """ 
    pgedge: Restore a backup using pgbackrest restore command
    Usage: pgedge backrest pitr <pitr_json_file>
    """
    if not os.path.exists(pitr_json_file):
        raise FileNotFoundError(f"PITR JSON file '{pitr_json_file}' not found.")

    try:
        # Run pgbackrest restore command
        subprocess.run(["pgbackrest", "restore"], check=True)
    except subprocess.CalledProcessError as e:
        # If the command fails, print the error message
        print("Error executing pgbackrest restore command:", e.output)

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
        "create-stanza": pgedge_create_stanza,
        "service-log": pgedge_service_log,
        "service-status": pgedge_service_status,
        "list-backups": pgedge_list_backups,
        "pitr": pgedge_pitr,
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

