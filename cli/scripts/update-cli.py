
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, sys, time, datetime, tarfile
from urllib import request as urllib2


import util, fire

BASE_BACKUP_DIR="/tmp/pgedge-cli-updates"
MY_HOME=os.getenv("MY_HOME")


def get_now():
    return(datetime.datetime.now(datetime.UTC).astimezone().strftime("%m%d_%H%M%S"))


def get_cli_ver(p_file):

    if not os.path.isfile(f"{p_file}"):
        util.exit_message(f"Cannot locate version file: {p_file}")

    awk3 = "awk '{print $3}'"
    ver_quoted = util.getoutput(f"grep 'VER =' {p_file} | {awk3}")

    ver = ver_quoted.replace('"', '')

    ##return(util.format_ver(ver))
    return(ver)


def replace_files(from_dir, to_dir):
    util.message("DEBUG:  figure it manually first")
    return


def download_file(p_file, p_dir):
    file_path = f"{p_dir}/{p_file}"
    url_path = f"{util.get_value("GLOBAL", "REPO")}/{p_file}"
    util.message(f"\nDownloading {url_path}")

    try:
        fu = urllib2.urlopen(url_path)
        local_file = open(file_path, "wb")
        local_file.write(fu.read())
        local_file.close()
    except Exception as e:
        util.exit_message(f"Unable to download \n {str(e)}")

    return


def unpack_file(p_file, p_dir):

    os.chdir(p_dir)
    util.message(f"\nUnpacking into {p_dir}")

    try:
        # Use 'data' filter if available, but revert to Python 3.11 behavior ('fully_trusted')
        #   if this feature is not available:
        tar = tarfile.open(p_file)
        tar.extraction_filter = getattr(tarfile, 'data_filter',
                                       (lambda member, path: member))
        tar.extractall()
        tar.close()
    except Exception as e:
        print("ERROR: Unable to unpack \n" + str(e))
        sys.exit(1)


def backup_current():
    """Backup current CLI to an archive directory

       Backup current CLI to '/tmp/pgedge_backup_cli' archive directory
    """

    ts = get_now()
    ver = get_cli_ver(f"{MY_HOME}/hub/scripts/install.py")
    backup_dir = f"{BASE_BACKUP_DIR}/{ts}_{ver}_CURRENT_BACKUP"
    rc = os.system(f"mkdir -p {backup_dir}")
    if rc != 0:
        return(None)

    util.message(f"\nBacking up current CLI into {backup_dir}")

    rc1 = os.system(f"cp -r {MY_HOME}/hub {backup_dir}")
    rc2 = os.system(f"cp {MY_HOME}/pgedge {backup_dir}/.")

    if rc1 + rc2 == 0:
        return(backup_dir)

    return(None)


def download_latest():
    """Download latest CLI to an archive directory
    
       Download latest CLI to '/tmp/pgedge_backup_cli' archive directory
    """

    ver_current = get_cli_ver(f"{MY_HOME}/hub/scripts/install.py")
    backup_dir = backup_current()
    if backup_dir is None:
        util.exit_message("Failed to take a current cli backup")
    time.sleep(1)

    now = get_now()
    download_dir = f"{BASE_BACKUP_DIR}/{now}_xxx_LATEST_DOWNLOAD"
    os.system(f"rm -rf {download_dir}")
    os.system(f"mkdir {download_dir}")
    download_file("install.py", download_dir)
    ver_latest = get_cli_ver(f"{download_dir}/install.py")

    new_dir = f"{BASE_BACKUP_DIR}/{now}_{ver_latest}_LATEST_DOWNLOAD"
    os.system(f"mv {download_dir} {new_dir}")

    file = f"pgedge-cli-{ver_latest}.tgz"
    download_file(file, new_dir)
    unpack_file(file, new_dir)

    print("")
    return(new_dir)


def list_archives():
    """List recent archive directories

       List recent archive directories under '/tmp/pgedge_backup_cli'
    """

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


def update_from_archive(archive_dir, force=False):
    """Update CLI from an archive directory

       Backup current CLI, download latest & then update with latest CLI

       Example: ./pgedge update-cli update-from-archive --force True
       :param force: force an update even if new version is same or older (defaults to False)
    """

    replace_files(archive_dir, MY_HOME)

    return("True || False")


def now(force=False):
    """ Backup current CLI, then download & update with latest CLI

        Backup current CLI, download latest & then update with latest CLI

        Example: ./pgedge update-cli now --force True
        :param force: force an update even if new version is same or older (defaults to False)
    """

    return()


if __name__ == "__main__":
    fire.Fire({
        "now":                  now,
        "backup-current":       backup_current,
        "download-latest":      download_latest,
        "update-from-archive":  update_from_archive,
        "list-archives":        list_archives,
    })
