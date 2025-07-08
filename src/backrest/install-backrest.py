#!/usr/bin/env python3
#     Copyright (c)  2022-2025 PGEDGE  #

import os
import sys
import util

thisDir = os.path.dirname(os.path.realpath(__file__))
osUsr = util.get_user()
usrUsr = osUsr + ":" + osUsr

os.chdir(f"{thisDir}")

def exit_rm_backrest(msg):
    util.message(f"{msg}", "error")
    osSys(f"{thisDir}/pgedge remove backrest")
    sys.exit(1)


def pgV():
    pg_versions = ["pg14", "pg15", "pg16", "pg17"]
    os.chdir(f"{thisDir}/../")
    for pg_version in pg_versions:
        if os.path.isdir(pg_version):
            return pg_version

    exit_rm_backrest("pg14, 15, 16 or 17 must be installed")

def osSys(p_input, p_display=False):
    if p_display:
        util.message("# " + p_input)
    rc = os.system(p_input)
    return rc

def configure_backup_settings():
    """Configure and return the pgBackRest settings."""
    stanza = "pg16"
    repo1_path = "/var/lib/pgbackrest/"
    config = {
        "stanza": stanza,
        "restore_path": "xx",
        "backup-type": "full",
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
        "process-max": "3",
        "log-level-console": "info",
        "pg1-path": "xx",
        "pg1-user": "xx",
        "pg1-port": "5432",
        "db-socket-path": "/tmp",
        "global:archive-push": {
            "compress-level": "3"
        }
    }

    # Set the configuration values
    for key, value in config.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                util.set_value("BACKUP", sub_key, sub_value)
        else:
            util.set_value("BACKUP", key, value)

    return config

def setup_pgbackrest_links():
    """
    Set up symbolic link for pgbackrest and create necessary directories.
    """
    osSys("sudo rm -f /usr/bin/pgbackrest")
    osSys(f"sudo ln -s {thisDir}/bin/pgbackrest /usr/bin/pgbackrest")
    osSys("sudo chmod 755 /usr/bin/pgbackrest")

    osSys("sudo mkdir -p -m 770 /var/log/pgbackrest")
    osSys(f"sudo chown {usrUsr} -R /var/log/pgbackrest")
    
    osSys("sudo mkdir -p -m 770 /var/lib/pgbackrest")
    osSys(f"sudo chown {usrUsr} -R /var/lib/pgbackrest")

def print_header(header):
    bold_start = "\033[1m"
    bold_end = "\033[0m"
    print(bold_start + "##### " + header + " #####"+ bold_end)

def main():
    if os.path.isdir(f"/var/lib/pgbackrest/"):
        util.message("/var/lib/pgbackrest directory already exists")
    
    print_header("Configuring pgbackrest")
    configure_backup_settings()
    setup_pgbackrest_links()
    osSys("pgbackrest version")

if __name__ == "__main__":
    main()

