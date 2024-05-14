#!/usr/bin/env python3
#     Copyright (c)  2022-2024 PGEDGE  #

import os
import subprocess
import time
import sys
import getpass
from crontab import CronTab
import subprocess
import util
import utilx

thisDir = os.path.dirname(os.path.realpath(__file__))
osUsr = util.get_user()
usrUsr = osUsr + ":" + osUsr

os.chdir(f"{thisDir}")

def exit_rm_backrest(msg):
    util.message(f"{msg}", "error")
    osSys(f"{thisDir}/pgedge remove backrest")
    sys.exit(1)


def pgV():
    pg_versions = ["pg14", "pg15", "pg16"]
    os.chdir(f"{thisDir}/../")
    for pg_version in pg_versions:
        if os.path.isdir(pg_version):
            return pg_version

    exit_rm_backrest("pg14, 15 or 16 must be installed")

def osSys(p_input, p_display=False):
    if p_display:
        util.message("# " + p_input)
    rc = os.system(p_input)
    return rc

def configure_backup_settings():
    stanza = "pg16"
    repo1_path = f"/var/lib/pgbackrest/"
    config = {
        "main": {
            "restore_path": "xx",
            "backup-type" : "full",
            "stanza_count" : "1"
        },
        "global": {
            "repo1-path": repo1_path,
            "repo1-host-user": "xx",
            "repo1-host": "xx",
            "repo1-type": "posix",
            "repo1-cipher-pass": "xx",
            "repo1-cipher-type": "aes-256-cbc",
            "repo1-s3-bucket": "xx",
            "repo1-s3-region": "eu-west-2",
            "repo1-s3-key": "xx",
            "repo1-s3-key-secret": "xx",
            "repo1-s3-endpoint": "s3.amazonaws.com",
            "repo1-retention-full": "7",
            "repo1-retention-full-type": "count",
            "process-max" : "3",
            "log-level-console": "info"
        },
        "stanza": {
            "stanza0" : "xx",
            "pg1-path0" : "xx",
            "pg1-user0" : "xx",
            "pg1-port0" : "5432",
            "pg1-host0" : "127.0.0.1",
            "db-socket-path0" : "/tmp",
            "global:archive-push0": {
                "compress-level": "3"
            }
        }
    }
    for section, parameters in config.items():
        if isinstance(parameters, dict):
            for key, sub_params in parameters.items():
                if isinstance(sub_params, dict):
                    for sub_key, value in sub_params.items():
                        util.set_value(f"BACKUP", sub_key, value)
                else:
                    util.set_value("BACKUP", key, sub_params)

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
    osSys(f"sudo cp {thisDir}/{filename} /etc/pgbackrest/")
    return filename

def setup_pgbackrest_links():
    """
    Set up symbolic link for pgbackrest and create necessary directories.
    """
    osSys("sudo rm -f /usr/bin/pgbackrest")
    osSys(f"sudo ln -s {thisDir}/bin/pgbackrest /usr/bin/pgbackrest")
    osSys("sudo chmod 755 /usr/bin/pgbackrest")

    osSys("sudo mkdir -p -m 770 /var/log/pgbackrest")

def setup_pgbackrest_conf():
    """
    Create pgbackrest configuration file and directories.
    """
    config = fetch_backup_config()
    usrUsr = osUsr
    parentDir = os.path.dirname(thisDir)
    
    dataDir = f"{parentDir}/data/{pgV()}"
    restoreDir = f"{parentDir}/restore"

    save_config()
    osSys(f"sudo chown {usrUsr} /var/log/pgbackrest")
    osSys("sudo mkdir -p /etc/pgbackrest /etc/pgbackrest/conf.d")
    osSys("sudo chmod 640 /etc/pgbackrest/pgbackrest.conf")
    osSys(f"sudo chown {usrUsr} /etc/pgbackrest/pgbackrest.conf")

    osSys("sudo mkdir -p /var/lib/pgbackrest")
    osSys("sudo chmod 750 /var/lib/pgbackrest")
    osSys(f"sudo chown -R {usrUsr}:{usrUsr} /var/lib/pgbackrest")

    conf_file = thisDir + "/pgbackrest.conf"
    util.replace("pgXX", pgV(), conf_file, True)
    util.replace("pg1-path=xx", "pg1-path=" + dataDir, conf_file, True)
    util.replace("pg1-user=xx", "pg1-user=" + usrUsr, conf_file, True)
    util.replace("pg1-database=xx", "pg1-database=" + "postgres", conf_file, True)
    
    util.set_value("BACKUP", "restore_path", restoreDir)
    
    util.set_value("BACKUP", "repo1-host", " ")
    util.set_value("BACKUP", "repo1-host-user", usrUsr)
    
    util.set_value("BACKUP", "stanza0", pgV())
    util.set_value("BACKUP", "pg1-path0", dataDir)
    util.set_value("BACKUP", "pg1-user0", usrUsr)
    util.set_value("BACKUP", "pg1-database0", "postgres")

def generate_cipher_pass():
    """
    Generate and replace cipher pass in pgbackrest.conf.
    """
    conf_file = os.path.join(thisDir, "pgbackrest.conf")
    cmd = "dd if=/dev/urandom bs=256 count=1 2> /dev/null | LC_ALL=C tr -dc 'A-Za-z0-9' | head -c32"
    bCipher = subprocess.check_output(cmd, shell=True)
    sCipher = bCipher.decode("ascii")
    util.replace("repo1-cipher-pass=xx", f"repo1-cipher-pass={sCipher}", conf_file, True)
    util.set_value("BACKUP", "repo1-cipher-pass", sCipher)

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

def create_or_update_job(crontab_lines, job_comment, detailed_comment, new_job):
    job_identifier = f"# {job_comment}"
    detailed_comment_line = f"# {detailed_comment}\n"
    job_exists = False

    for i, line in enumerate(crontab_lines):
        if job_identifier in line:
            crontab_lines[i] = job_identifier + "\n"
            if i + 1 < len(crontab_lines):
                crontab_lines[i + 1] = detailed_comment_line
                crontab_lines[i + 2] = new_job
            job_exists = True
            break

    if not job_exists:
        crontab_lines.extend([job_identifier + "\n", detailed_comment_line, new_job])

def define_cron_job():
    stanza = util.get_value("BACKUP", "stanza")
    full_backup_command = f"pgbackrest --stanza={stanza} --type=full backup"
    incr_backup_command = f"pgbackrest --stanza={stanza} --type=incr backup"
    expire_backup_command = f"pgbackrest --stanza={stanza} expire"

    run_as_user = 'root'

    # Crontab entries with detailed comments
    full_backup_cron = f"0 1 * * * {run_as_user} {full_backup_command}\n"
    incr_backup_cron = f"0 * * * * {run_as_user} {incr_backup_command}\n"
    expire_backup_cron = f"30 1 * * * {run_as_user} {expire_backup_command}\n"

    # Detailed comments for each job
    full_backup_comment = "Performs a full backup daily at 1 AM."
    incr_backup_comment = "Performs an incremental backup every hour."
    expire_backup_comment = "Manages backup retention, expiring old backups at 1:30 AM daily."

    system_crontab_path = "/etc/crontab"
    backrest_crontab_path = "backrest.crontab"

    with open(system_crontab_path, 'r') as file:
        existing_crontab = file.readlines()

    create_or_update_job(existing_crontab, "FullBackup", full_backup_comment, full_backup_cron)
    create_or_update_job(existing_crontab, "IncrementalBackup", incr_backup_comment, incr_backup_cron)
    create_or_update_job(existing_crontab, "ExpireBackup", expire_backup_comment, expire_backup_cron)

    with open(backrest_crontab_path, 'w') as file:
        file.writelines(existing_crontab)

    osSys(f"sudo cat {backrest_crontab_path} | sudo tee {system_crontab_path} > /dev/null", False)

def fetch_backup_config():
    """Fetch and return the pgBackRest configuration from system settings."""
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

def print_header(header):
    bold_start = "\033[1m"
    bold_end = "\033[0m"
    print(bold_start + "##### " + header + " #####"+ bold_end)

def main():
    stanza = pgV()
    if os.path.isdir(f"/var/lib/pgbackrest/{stanza}/"):
        utilx.ereport("WARNING", "/var/lib/pgbackrest directory already exists")
    
    print_header("Configuring pgbackrest")
    configure_backup_settings()
    generate_cipher_pass()
    setup_pgbackrest_links()
    setup_pgbackrest_conf()
    usrUsr = f"{util.get_user()}:{util.get_user()}"
    osSys("pgbackrest version")

if __name__ == "__main__":
    main()

