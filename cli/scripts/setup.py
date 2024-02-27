#  Copyright 2024-2024 PGEDGE  All rights reserved. #

import os, sys, time

os.chdir(os.getenv("MY_HOME"))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

import fire, util, db


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


def check_pre_reqs(User, Passwd, db, port, pg_major, pg_minor, spock, autostart):
    util.message(f"setup.check_pre_reqs({User}, {db}, {port}, {pg_major}, {pg_minor}, {spock})", "debug")

    util.message("#### Checking for Pre-Req's #########################")

    platf = util.get_platform()

    # util.message("  Verify Linux")
    # if platf != "Linux":
    #    util.exit_message("OS must be Linux")

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

    util.message(f"  Verify pg major version {pg_major}")
    valid_pg = ["14", "15", "16", "17"]
    if pg_major not in valid_pg:
        util.exit_message(f"pg {pg_major} must be in {valid_pg}")
    if pg_minor:
       util.message(f"  Verify pg minor version {pg_minor}")
       num_pg_mins = util.num_pg_minors(pg_minor, True)
       if num_pg_mins == 0:
           util.exit_message(f"No available version of pg like '{pg_minor}*'")
       elif num_pg_mins > 1:
           util.exit_message(f"{num_pg_mins} versions available matching '{pg_minor}*'")

    data_dir = f"data/pg{pg_major}"
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

    if spock:
       util.message(f"  Verify spock '{spock}' is valid and unique")
       ns = util.num_spocks(pg_major, spock, True)
       if ns == 0:
           util.exit_message(f"No available version of spock like '{spock}*'")
       elif ns > 1:
           util.exit_message(f"More than 1 spock version available matching '{spock}*'")


def parse_pg(pg):
   if pg is None:
     return(None, None)

   pg = str(pg)

   pg_major = pg
   pg_minor = None
   if "." in pg:
     pg_minor = str(pg)
     pg_major = str(pg)[:2]
   
   return(pg_major, pg_minor)


def setup_pgedge(User=None, Passwd=None, dbName=None, port=None, pg_ver=None, spock_ver=None, autostart=False):
    """Install pgEdge node (including postgres, spock, and snowflake-sequences)

       Install pgEdge node (including postgres, spock, and snowflake-sequences)

       Example: ./pgedge setup -U user -P passwd -d test --pg_ver 16
       :param User: The database user that will own the db (required)
       :param Passwd: The password for the newly created db user (required)
       :param dbName: The database name (required)
       :param port: Defaults to 5432 if not specified
       :param pg_ver: Defaults to latest prod version of pg, such as 16.  May be pinned to a specific pg version such as 16.1
       :param spock_ver: Defaults to latest prod version of spock, such as 3.2.  May be pinned to a specific spock version such as 3.2.4
       :param autostart: Defaults to False
    """

    util.message(f"setup.pgedge({User}, {dbName}, {port}, {pg_ver}, {spock_ver}, {autostart}", "debug")

    if not User:
        User = os.getenv("pgeUser", None)

    if not Passwd:
        Passwd = os.getenv("pgePasswd", None)

    if not dbName:
        dbName = os.getenv("pgName", None)

    if (User is None) or (Passwd is None) or (dbName is None):
        util.exit_message("Must specify User, Passwd & dbName")

    if not port:
        port = os.getenv("pgePort", "5432")

    if not pg_ver:
        pg_ver = os.getenv("pgN", util.DEFAULT_PG)

    pg_major, pg_minor = parse_pg(pg_ver)

    if not autostart:
        autos = os.getenv("isAutoStart")
        if autos == "True":
           autostart = True
        else:
           autostart = False 

    check_pre_reqs(User, Passwd, dbName, port, pg_major, pg_minor, spock_ver, autostart)

    pause = 4
    pg_full = f"pg{pg_major}"
    ctl = "./pgedge"

    if pg_minor:
        pg_full = f"pg{pg_major} {pg_minor}"
    osSys(f"{ctl} install {pg_full}")

    if util.is_empty_writable_dir("/data") == 0:
        util.message("## symlink empty local data directory to empty /data ###")
        osSys("rm -rf data; ln -s /data data")

    if autostart:
        util.message("\n## init & config autostart  ###############")
        osSys(f"{ctl} init pg{pg_major} --svcuser={util.get_user()}")
        osSys(f"{ctl} config pg{pg_major} --autostart=on")
    else:
        osSys(f"{ctl} init pg{pg_major}")

    osSys(f"{ctl} config pg{pg_major} --port={port}")

    osSys(f"{ctl} start pg{pg_major}")
    time.sleep(pause)

    db.create(dbName, User, Passwd, pg_major, spock_ver)
    time.sleep(pause)


if __name__ == "__main__":
    fire.Fire(setup_pgedge)
