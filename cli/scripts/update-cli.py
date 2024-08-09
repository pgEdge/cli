
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, sys, datetime

import util, fire

BASE_BACKUP_DIR="/tmp/pgedge-cli-updates"
MY_HOME=os.getenv("MY_HOME")


def get_now():
    return(datetime.datetime.now(datetime.UTC).astimezone().strftime("%Y%m%d_%H%M%S"))


def get_cli_ver(home_dir=os.getenv("MY_HOME", "")):
    util_py = f"{home_dir}/hub/scripts/util.py"
    if not os.path.isfile(f"{util_py}"):
        util.exit_message(f"Cannot locate version file: {util_py}")

    awk3 = "awk '{print $3}'"
    ver_quoted = util.getoutput(f"grep 'MY_VERSION =' {util_py} | {awk3}")

    ver = ver_quoted.replace('"', '')

    return(util.format_ver(ver))


def backup_current():
    ts = get_now()
    ver = get_cli_ver()
    backup_dir = f"{BASE_BACKUP_DIR}/{ts}_{ver}_BACKUP"
    rc = util.echo_cmd(f"mkdir -p {backup_dir}")
    if rc != 0:
        return(False)

    rc1 = util.echo_cmd(f"cp -r {MY_HOME}/hub {backup_dir}")
    rc2 = util.echo_cmd(f"cp {MY_HOME}/pgedge {backup_dir}/.")

    if rc1 + rc2 == 0:
        return(True)

    return(False)


def download_new():
    return("YYYY-MM-DD_HH-MM-SS_xx.yy-z_NEW")


def apply_new(new_dir=None):
    if new_dir:
       if not os.path_isdir(new_dir):
           util.exit_message(f"Invalid new directory: {new_dir}")

    backup_dir = current_backup()
    if backup_dir is None:
        util.exit_message("Failed to take a current cli backup")

    util.message("backup_dir = {backup_dir}")

    if new_dir is None:
        new_dir = new_download()
        if new_dir is None:
            util.exit_message("Failed to download a new dir")

    util.message(f"new_dir = {new_dir}")

    ## copy new_dir over current_dir
    copy_dir_over_current(new_dir)

    return(True)


def list_dir_descending(base_dir, wildcard):
    dir_list = []

    for name in os.listdir(base_dir):
        if wildcard in name:
            dir_list.append(name)

    if len(dir_list) >= 1:
        desc_list = sorted(dir_list, reverse=True)
        for name in desc_list:
            print(name)


def list_downloads():
    list_dir_descending(BASE_BACKUP_DIR, "_DOWNLOAD")
    return


def list_backups():
    list_dir_descending(BASE_BACKUP_DIR, "_BACKUP")

    return


def restore_backup(old_dir):
    ## Create backup directory _BEFORE_RESTORE

    ## copy old_dir over current
    copy_dir_over_current(old_dir)

    return("True || False")


if __name__ == "__main__":
    fire.Fire({
        "backup-current": backup_current,
        "list-backups":   list_backups,
        "download-new":   download_new,
        "list-downloads": list_downloads,
        "apply-new":      apply_new,
        "restore-backup": restore_backup,
    })
