
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import util, fire

BACKUP_DIR="/tmp/pgedge-cli-updates"

def current_backup():
    return("YYYY-MM-DD_HH-MM-SS_xx.yy-z_BACKUP")

def new_download():
    return("YYYY-MM-DD_HH-MM-SS_xx.yy-z_NEW")

def new_apply(new_dir=None):

    if new_dir:
       # if [ ! -d $new_dir ]; then
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


def new_list():
    # show(*_NEW directories)
    return("True || False")

def old_list():
    # show(*_OLD directories)
    return("True || False")
    return(True)

def old_restore(old_dir):
    ## Create backup directory _BEFORE_RESTORE

    ## copy old_dir over current
    copy_dir_over_current(old_dir)

    return("True || False")


if __name__ == "__main__":
    fire.Fire({
        "current-backup": current_backup,
        "new-download":   new_download,
        "new-list":       new_list,
        "new-apply":      new_apply,
        "old-list":       old_list,
        "old-restore":    old_restore,
    })
