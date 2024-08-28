
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, sys, time, datetime, tarfile, subprocess
from urllib import request as urllib2

BASE_BACKUP_DIR="/tmp/pgedge-cli-updates"
MY_HOME=os.getcwd()


def exit_message(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def check_cmd(p_cmd, noisy=True):
    if noisy:
        print(f"$ {p_cmd}")

    rc = os.system(p_cmd)
    if rc == 0:
        return
    exit_message(f"Failed '{p_cmd}'")


def get_now():
    return(datetime.datetime.now().astimezone().strftime("%m%d_%H%M%S"))


def get_output(p_cmd):
    try:
        out_b = subprocess.check_output(p_cmd, shell=True)
    except Exception as e:
        exit_message(f"Unable to run {p_cmd} \n {e}")

    out_s = out_b.strip().decode("ascii") 
    return (out_s)


def get_cli_ver(p_file):
    if not os.path.isfile(f"{p_file}"):
        exit_message(f"Cannot locate version file: {p_file}")

    awk3 = "awk '{print $3}'"
    cmd = f"grep 'VER =' {p_file} | {awk3}"
    ver_quoted = get_output(cmd)

    ver = ver_quoted.replace('"', '')
    return(ver)


def download_file(p_file, p_dir):
    file_path = f"{p_dir}/{p_file}"

    repo = get_output(f"{MY_HOME}/pgedge get GLOBAL REPO")

    url_path = f"{repo}/{p_file}"
    if not DRYRUN:
        print(f"# Downloading {url_path}")

    try:
        fu = urllib2.urlopen(url_path)
        local_file = open(file_path, "wb")
        local_file.write(fu.read())
        local_file.close()
    except Exception as e:
        exit_message(f"Unable to download \n {e}")

    return


def unpack_file(p_file, p_dir):
    os.chdir(p_dir)
    print(f"# Unpacking into {p_dir}")

    try:
        # Use 'data' filter if available, but revert to Python 3.11 behavior ('fully_trusted')
        #   if this feature is not available:
        tar = tarfile.open(p_file)
        tar.extraction_filter = getattr(tarfile, 'data_filter',
                                       (lambda member, path: member))
        tar.extractall()
        tar.close()
    except Exception as e:
        exit_message(f"Unable to unpack\n {str(e)}")


def backup_current():

    if not DRYRUN:
        print(f"\n### Validating CLI current dir '{MY_HOME}'")
    ts = get_now()
    ver = get_cli_ver(f"{MY_HOME}/hub/scripts/install.py")
    print(f"\n## Current CLI = {ver}")

    backup_dir = f"{BASE_BACKUP_DIR}/{ts}_{ver}_CURRENT_BACKUP"
    if not DRYRUN:
        print(f"\n### Backing up current CLI to {backup_dir}")
    check_cmd(f"mkdir -p {backup_dir}", False)

    check_cmd(f"cp -r {MY_HOME}/hub {backup_dir}", False)
    check_cmd(f"cp {MY_HOME}/pgedge {backup_dir}/.", False)
    check_cmd(f"cp {MY_HOME}/data/conf/db_local.db {backup_dir}/.", False)
    check_cmd(f"cp {MY_HOME}/data/conf/versions.sql {backup_dir}/.", False)

    return(backup_dir)


def download_latest():
    print("\n### Download latest CLI to archive directory")

    now = get_now()
    download_dir = f"{BASE_BACKUP_DIR}/{now}_xxx_LATEST_DOWNLOAD"
    check_cmd(f"rm -rf {download_dir}", False)
    check_cmd(f"mkdir {download_dir}", False)

    download_file("install.py", download_dir)
    ver_latest = get_cli_ver(f"{download_dir}/install.py")

    print(f"\n### Latest CLI = {ver_latest}\n")

    if DRYRUN:
        return("")

    new_dir = f"{BASE_BACKUP_DIR}/{now}_{ver_latest}_LATEST_DOWNLOAD"
    check_cmd(f"mv {download_dir} {new_dir}", False)

    file = f"pgedge-cli-{ver_latest}.tgz"
    download_file(file, new_dir)
    unpack_file(file, new_dir)

    return(new_dir)


def update_from_archive(archive_dir):
    print("\n### Updating CLI modules from archive")

    os.chdir(MY_HOME)
    check_cmd(f"cp -r {archive_dir}/pgedge/hub .", False)
    check_cmd(f"cp {archive_dir}/pgedge/pgedge .", False)

    print("\n### Updating meta data from remote")
    check_cmd("./pgedge update")

    print("\n### Ensure latest ctlibs")
    check_cmd("./pgedge remove ctlibs")
    check_cmd("./pgedge install ctlibs")


########## MAINLINE ###############################

if len(sys.argv) > 2:
    exit_message("Too many parms, only optional parm is '--dryrun'")

DRYRUN = False
if len(sys.argv) == 2:
    if sys.argv[1] == "--dryrun":
        DRYRUN = True
    else:
        exit_message(f"Invalid parm {sys.argv[1]}, only optional parm is '--dryrun'")


curr_backup = backup_current()

time.sleep(1)
latest_archive = download_latest()

if DRYRUN:
    sys.exit(0)

install_py = "hub/scripts/install.py"
curr_ver = get_cli_ver(f"{curr_backup}/{install_py}")
latest_ver = get_cli_ver(f"{latest_archive}/pgedge/{install_py}")

sleep_secs = 3
print(f"\n### Updating to {latest_ver} from {curr_ver} in {sleep_secs} seconds")
time.sleep(sleep_secs)

update_from_archive(latest_archive)

sys.exit(0)
