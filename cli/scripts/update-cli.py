
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, sys, datetime, tarfile
from urllib import request as urllib2


import util, fire

BASE_BACKUP_DIR="/tmp/pgedge-cli-updates"
MY_HOME=os.getenv("MY_HOME")


def get_now():
    return(datetime.datetime.now(datetime.UTC).astimezone().strftime("%Y%m%d_%H%M%S"))


def get_cli_ver(p_file):

    if not os.path.isfile(f"{p_file}"):
        util.exit_message(f"Cannot locate version file: {p_file}")

    awk3 = "awk '{print $3}'"
    ver_quoted = util.getoutput(f"grep 'VER =' {p_file} | {awk3}")

    ver = ver_quoted.replace('"', '')

    return(util.format_ver(ver))


def replace_files(from_dir, to_dir):
    util.message("DEBUG:  figure it manually first")
    return


def download_file(p_file, p_dir):
    file_path = f"{p_dir}/{p_file}"
    url_path = f"{util.get_value("GLOBAL", "REPO")}/{p_file}"
    util.message(f"Downloading {url_path} to '{file_path}'")

    try:
        fu = urllib2.urlopen(url_path)
        local_file = open(file_path, "wb")
        local_file.write(fu.read())
        local_file.close()
    except Exception as e:
        util.exit_message(f"Unable to download \n {str(e)}")

    return


def unpack_file(p_file, p_dir):
    file_path = f"{p_dir}/{p_file}"
    util.message(f"Unpacking {file_path} ...")

    try:
        # Use 'data' filter if available, but revert to Python 3.11 behavior ('fully_trusted')
        #   if this feature is not available:
        tar = tarfile.open(file_path)
        tar.extraction_filter = getattr(tarfile, 'data_filter',
                                       (lambda member, path: member))
        tar.extractall()
        tar.close()
    except Exception as e:
        print("ERROR: Unable to unpack \n" + str(e))
        sys.exit(1)


def backup_current():
    ts = get_now()
    ver = get_cli_ver(f"{MY_HOME}/hub/scripts/install.py")
    backup_dir = f"{BASE_BACKUP_DIR}/{ts}_{ver}_BACKUP"
    rc = os.system(f"mkdir -p {backup_dir}")
    if rc != 0:
        return(None)

    rc1 = os.system(f"cp -r {MY_HOME}/hub {backup_dir}")
    rc2 = os.system(f"cp {MY_HOME}/pgedge {backup_dir}/.")

    if rc1 + rc2 == 0:
        return(backup_dir)

    return(None)


def apply_latest():

    ver_current = get_cli_ver(f"{MY_HOME}/hub/scripts/install.py")
    backup_dir = backup_current()
    if backup_dir is None:
        util.exit_message("Failed to take a current cli backup")

    download_dir = f"{BASE_BACKUP_DIR}/{get_now()}_{get_cli_ver()}_DOWNLOAD"
    os.system(f"rm -rf {download_dir}")
    os.system(f"mkdir {download_dir}")
    download_file("install.py", download_dir)
    ver_latest = get_cli_ver(f"{download_dir}/install.py")

    file = f"hub-{verlatest}"
    download_file(file, download_dir)
    unpack_file(file, download_dir)
    replace_files(download_dir, MY_HOME)

    return


def list_archives():
    dir_list = []

    if not os.path.isdir(BASE_BACKUP_DIR):
        os.system(f"mkdir -p {BASE_BACKUP_DIR}")

    for name in os.listdir(BASE_BACKUP_DIR):
        if ("_BACKUP" in name) or ("_DOWNLOAD" in name):
            dir_list.append(name)

    if len(dir_list) >= 1:
        desc_list = sorted(dir_list, reverse=True)
        for name in desc_list:
            print(name)


def restore_archive(old_dir):
    ## Create backup directory _BEFORE_RESTORE

    ## copy old_dir over current
    copy_dir_over_current(old_dir)

    return("True || False")


if __name__ == "__main__":
    fire.Fire({
        "apply-latest":    apply_latest,
        "backup-current":  backup_current,
        "list-archives":   list_archives,
        "restore-archive":  restore_archive,
    })
