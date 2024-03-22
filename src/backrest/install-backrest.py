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

thisDir = os.path.dirname(os.path.realpath(__file__))
osUsr = util.get_user()
usrUsr = osUsr + ":" + osUsr

def exit_rm_backrest(msg):
    util.message(f"{msg}", "error")
    osSys("./pgedge remove backrest")
    sys.exit(1)

pgV = ""
if os.path.isdir("pg14"):
    pgV = "pg14"
elif os.path.isdir("pg15"):
    pgV = "pg15"
elif os.path.isdir("pg16"):
    pgV = "pg16"
if pgV == "":
    exit_rm_backrest("pg14, 15 or 16 must be installed")

os.chdir(thisDir)

def osSys(p_input, p_display=True):
    if p_display:
        util.message("# " + p_input)
    rc = os.system(p_input)
    return rc

def configure_backup_settings(stanza_name):
    """
    Configures backup settings based on environment variables and system properties.
    """
    pg_data_path = os.getenv('PSX', '/usr/local/pgsql') + "/data/" + stanza_name
    pg_restore_path = os.getenv('PSX', '/usr/local/pgsql') + "/restore/" + stanza_name

    current_user = getpass.getuser()

    # Backup configuration settings
    backup_config = {
        "BACKUP_PATH": "/path/to/backup",
        "DATABASE": "postgres",
        "PG_PATH": pg_data_path,
        "PG_USER": current_user,
        "PG_SOCKET_PATH": "/tmp",
        "REPO_CIPHER_TYPE": "aes-256-cbc",
        "REPO_CIPHER_PASSWORD": "",
        "REPO_PATH": "/var/lib/pgbackrest",
        "REPO_RETENTION_FULL_TYPE": "count",
        "REPO_RETENTION_FULL": "7",
        "BACKUP_TOOL": "pgbackrest",
        "STANZA": stanza_name,
        "PRIMARY_HOST": "127.0.0.1",
        "PRIMARY_PORT": "5432",
        "PRIMARY_USER": current_user,
        "REPLICA_PASSWORD": "123",
        "RECOVERY_TARGET_TIME": "",
        "RESTORE_PATH": pg_restore_path,
        "REPO1_TYPE": "local",
        "BACKUP_TYPE": "full",
        "S3_BUCKET": "",
        "S3_REGION": "",
        "S3_ENDPOINT": ""
    }

    for key, value in backup_config.items():
        util.set_value("BACKUP", key, value)

    print("Backup configuration has been set successfully.")

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
    usrUsr = config["PG_USER"]
    dataDir = config["PG_PATH"]

    osSys(f"sudo chown {usrUsr} /var/log/pgbackrest")
    osSys("sudo mkdir -p /etc/pgbackrest /etc/pgbackrest/conf.d")
    osSys("sudo cp pgbackrest.conf /etc/pgbackrest/")
    osSys("sudo chmod 640 /etc/pgbackrest/pgbackrest.conf")
    osSys(f"sudo chown {usrUsr} /etc/pgbackrest/pgbackrest.conf")

    osSys("sudo mkdir -p /var/lib/pgbackrest")
    osSys("sudo chmod 750 /var/lib/pgbackrest")
    osSys(f"sudo chown {usrUsr} /var/lib/pgbackrest")
    conf_file = thisDir + "/pgbackrest.conf"
    util.replace("pgXX", pgV, conf_file, True)
    util.replace("pg1-path=xx", "pg1-path=" + dataDir, conf_file, True)
    util.replace("pg1-user=xx", "pg1-user=" + usrUsr, conf_file, True)
    util.replace("pg1-database=xx", "pg1-database=" + "postgres", conf_file, True)
    osSys("cp " + conf_file + "  /etc/pgbackrest/.")

def generate_cipher_pass():
    """
    Generate and replace cipher pass in pgbackrest.conf.
    """
    conf_file = os.path.join(thisDir, "pgbackrest.conf")
    cmd = "dd if=/dev/urandom bs=256 count=1 2> /dev/null | LC_ALL=C tr -dc 'A-Za-z0-9' | head -c32"
    bCipher = subprocess.check_output(cmd, shell=True)
    sCipher = bCipher.decode("ascii")
    util.replace("repo1-cipher-pass=xx", f"repo1-cipher-pass={sCipher}", conf_file, True)
    util.set_value("BACKUP", "REPO_CIPHER_PASSWORD", sCipher)

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
  util.update_pg_hba_conf(pgV, new_rules)

def modify_postgresql_conf(stanza):
    """
    Modify 'postgresql.conf' to integrate with pgBackRest.
    """
    aCmd = f"pgbackrest --stanza={stanza} archive-push %p"
    util.change_pgconf_keyval(stanza, "archive_command", aCmd, p_replace=True)
    util.change_pgconf_keyval(stanza, "archive_mode", "on", p_replace=True)

def create_stanza():
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
        subprocess.run(command, check=True)
        print("Stanza created successfully.")
    except subprocess.CalledProcessError as e:
        print("Error creating stanza:", e)

def define_cron_job():

    # Define your command
    backup_command = "pgedge backup"
    incr_backup_command = "pgedge backup --incr"

    # Access the current user's crontab
    cron = CronTab(user=util.get_user())

    # Create a new job for the full backup at 01:00 every day
    full_job = cron.new(command=backup_command, comment='Full backup job')
    full_job.setall('0 1 * * *')

    # Create a new job for the incremental backup every hour
    incr_job = cron.new(command=incr_backup_command, comment='Incremental backup job')
    incr_job.setall('0 * * * *')

    # Write the jobs to the crontab
    cron.write()


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

def print_header(header):
    bold_start = "\033[1m"
    bold_end = "\033[0m"
    print(bold_start + "##### " + header + " #####"+ bold_end)

def main():
    if os.path.isdir("/var/lib/pgbackrest"):
        exit_rm_backrest("ERROR: '/var/lib/pgbackrest' directory already exists")

    print_header("Configuring pgbackrest")
    configure_backup_settings(pgV)
    generate_cipher_pass()
    setup_pgbackrest_links()
    setup_pgbackrest_conf()
    usrUsr = f"{util.get_user()}:{util.get_user()}"
    osSys("rm -r lib", False)
    osSys("rm -r share", False)
    print_config()

    print_header("Configuring pgbackrest's setting in postgresql.conf")
    modify_postgresql_conf(pgV)
    modify_hba_conf()

    print_header("Restarting PostgreSQL instance " + pgV)
    osSys(f"../pgedge restart {pgV}")
    time.sleep(3)

    print_header("Creating stanza for pgbackrest" + pgV)
    create_stanza()

    print_header("Configuraing cron jobs for pgbackrest")
    define_cron_job()

    print("pgbackrest installed successfully")

if __name__ == "__main__":
    main()

