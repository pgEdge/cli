#  Copyright 2024-2024 PGEDGE  All rights reserved. #

import os, sys

os.chdir(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

import fire
import util


def osSys(cmd, fatal_exit=True):
    isSilent = os.getenv("isSilent", "False")
    if isSilent == "False":
        s_cmd = util.scrub_passwd(cmd)
        util.message("#")
        util.message("# " + str(s_cmd))

    rc = os.system(cmd)
    if rc != 0 and fatal_exit:
        util.exit_message("FATAL ERROR running setup pgedge", 1)

    return


def check_pre_reqs(User, Passwd, db, port, pg, spock, autostart):

    util.message("#### Checking for Pre-Req's #########################")
    platf = util.get_platform()

    util.message("  Verify Linux")
    if platf != "Linux":
        util.exit_message("OS must be Linux")

    if platf == "Linux":
        util.message("  Verify Linux supported glibc version")
        if util.get_glibc_version() < "2.28":
            util.exit_message("Linux has unsupported (older) version of glibc")

        if autostart:
            util.message("  Verify SELinux is not active")
            if util.is_selinux_active():
               util.exit_message("SELinux must not be active for --autostart True mode")
    
    util.message("  Verify Python 3.9+")
    p3_minor_ver = util.get_python_minor_version()
    if p3_minor_ver < 9:
        util.exit_message("Python version must be greater than 3.9")

    util.message("  Verify non-root user")
    if util.is_admin():
        util.exit_message("You must install as non-root user with passwordless sudo privleges")

    util.message(f"  Verify port {port} availability")
    if util.is_socket_busy(int(port)):
           util.exit_message(f"Port {port} is unavailable")

    util.message(f"  Using port {port}")

    util.message(f"  Verify pg version {pg}")
    if pg == "latest":
        pg = util.DEFAULT_PG
    if str(pg) < "14" or str(pg) > "17":
        util.exit_message(f"pg must be between 14, 15, 16 or 17")

    data_dir = f"data/pg{pg}"
    util.message("  Verify empty data directory '" + data_dir + "'")
    if os.path.exists(data_dir):
        dir = os.listdir(data_dir)
        if len(dir) != 0:
            util.exit_message("The '" + data_dir + "' directory is not empty")

    util.message("  Verify User & Passwd")
    usr_l = User.lower()
    if usr_l == "pgedge":
        util.exit_message("The user defined supersuser may not be called 'pgedge'")

    if usr_l == util.get_user():
        util.exit_message("The user-defined superuser may not be the same as the OS user")

    usr_len = len(usr_l)
    if (usr_len < 1) or (usr_len > 64):
        util.exit_message("The user-defined superuser must be >=1 and <= 64 in length")

    pwd_len = len(Passwd)
    if (pwd_len < 6) or (pwd_len > 128):
        util.exit_message("The password must be >= 6 and <= 128 in length")

    for pwd_char in Passwd:
        pwd_c = pwd_char.strip()
        if pwd_c in (",", "'", '"', "@", ""):
            util.exit_message(
                "The password must not contain {',', \"'\", \", @, or a space"
            )

    if spock != "latest":
       util.message(f"  Verify spock {spock} is valid and unique")
       ns = util.get_num_spocks(spock)
       if ns == 0:
           util.exit_message(f"No available version of spock like '{spock}*'")
       elif ns > 1:
           util.exit_message(f"More than 1 spock version available matching '{spock}*'")



def pgedge(User, Passwd, db, port=5432, pg="16", spock="latest", autostart=False):
    """Install pgEdge node (including Postgres, spock, snowflake-sequences and ...)

       Install pgEdge node (including Postgres, spock, snowflake-sequences and ...)
       Example: setup pgedge "user" "passwd" "test" --pg 16
       :param User: The database user that will own the db
       :param Passwd: The password for the newly created db user 
       :param db: The database name
    """

    print(f"DEBUG {User}, {Passwd}, {db}, {port}, {pg}, {spock}\n")

    check_pre_reqs(User, Passwd, db, port, pg, spock, autostart)


if __name__ == "__main__":
    fire.Fire(
        {
            "pgedge":         pgedge,
        }
    )
