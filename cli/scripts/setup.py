
#  Copyright 2024-2024 PGEDGE  All rights reserved. #

import os, sys, time

os.chdir(os.getenv("MY_HOME"))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

import fire, util, db

# extensions installed 'Disabled' if you pass --extensions [core | all] to setup() (defaults to 'core')
CORE_EXTS="spock40 snowflake lolor vector postgis"

MORE_EXTS="audit cron orafce partman curl citus timescaledb wal2json " + \
       "hypopg hintplan plv8 setuser permissions profiler debugger"

EXTS_15 = "foslots"
CTL="./pgedge"


def osSys(cmd, fatal_exit=True, is_silent=False):
    if not is_silent:
        s_cmd = util.scrub_passwd(cmd)
        util.message("#")
        util.message("# " + str(s_cmd))

    rc = os.system(cmd)
    if rc != 0 and fatal_exit:
        util.exit_message("FATAL ERROR running setup pgedge", 1)

    return


def check_pre_reqs(User, Passwd, db, port, pg_major, pg_minor, spock, autostart, extensions):
    util.message(f"setup.check_pre_reqs(User={User}, db={db}, port={port}, pg_major={pg_major}, " + \
        f"pg_minor={pg_minor}, spock={spock}, autostart={autostart}, extensions={extensions})", "debug")

    util.message("#### Checking for Pre-Req's #########################")

    platf = util.get_platform()

    if platf == "Linux":
        if util.glibc_ver() < "2.28":
            util.exit_message("Linux has unsupported (older) version of glibc")

        if autostart:
            util.autostart_verify_prereqs()
    
    util.message("  Verify Python 3.9+")
    p3_minor_ver = util.get_python_minor_version()
    if p3_minor_ver < 9:
        util.exit_message("Python version must be greater than 3.9")

    util.message("  Verify non-root user")
    if util.is_admin():
        util.exit_message("You must install as non-root user with passwordless sudo privleges")

    if extensions:
        pass
    else:
        util.message(f"  Verify port {port} availability")
        if util.is_socket_busy(int(port)):
            util.exit_message(f"Port {port} is unavailable")
        util.message(f"    - Using port {port}")

    VALID_PG = ["14", "15", "16", "17"]
    if pg_major not in util.VALID_PG:
        util.exit_message(f"pg {pg_major} must be in {util.VALID_PG}")
    if pg_minor:
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

    if extensions is None:
        if (User is None) or (Passwd is None) or (db is None):
            util.exit_message("Must specify User, Passwd & db")

        verifyUserPasswd(User, Passwd)


    if spock:
       util.message(f"  Verify spock '{spock}' is valid and unique")
       ns = util.num_spocks(pg_major, spock, True)
       if ns == 0:
           util.exit_message(f"No available version of spock like '{spock}*' for pg{pg_major}")
       elif ns > 1:
           util.exit_message(f"More than 1 spock version available matching '{spock}*'")


def verifyUserPasswd(User, Passwd):

    util.message("  Verify User & Passwd")
    usr_l = User.lower()
    if usr_l == "pgedge":
        util.exit_message("The user defined superuser may not be called 'pgedge'")

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


def setup_pgedge(User=None, Passwd=None, dbName=None, port=None, 
                 pg_ver=None, spock_ver=None, autostart=False, extensions=None):
    """Install pgEdge node (including postgres, spock, and snowflake-sequences)

       Install pgEdge node (including postgres, spock, and snowflake-sequences)

       Example: ./pgedge setup -U user -P passwd -d test --pg_ver 16
       :param User: The database user that will own the db (required)
       :param Passwd: The password for the newly created db user (required)
       :param dbName: The database name (required)
       :param port: Defaults to 5432 if not specified
       :param pg_ver: Defaults to latest prod version of pg, such as 16.  May be pinned to a specific pg version such as 16.2
       :param spock_ver: Defaults to latest prod version of spock, such as 4.0.  May be pinned to a specific spock version such as 4.0.1
       :param autostart: Defaults to False
       :param extensions: Defaults to 'core' pgEdge extensions. Will install all supported extensions when set to 'all' 
    """

    if os.getenv("isAutoStart", "") == "True":
        autostart = True

    pgeExt = os.getenv("pgeExtensions", None)
    if pgeExt:
        extensions = pgeExt


    util.message(f"setup.pgedge(User={User}, Passwd='***', dbName={dbName}, port={port}, \n" + \
                 f"    pg_ver={pg_ver}, spock_ver={spock_ver}, autostart={autostart}, extensions={extensions})", "debug")

    if not port:
        port = os.getenv("pgePort", "5432")

    df_pg = util.get_default_pg()
    if not pg_ver:
        pg_ver = os.getenv("pgN", df_pg)

    pg_major, pg_minor = parse_pg(pg_ver)

    if autostart is False:
        autos = os.getenv("isAutoStart")
        if autos == "True":
           autostart = True
        else:
           autostart = False 

    check_pre_reqs(User, Passwd, dbName, port, pg_major, pg_minor, spock_ver, autostart, extensions)

    pause = 2
    pg_full = f"pg{pg_major}"

    if pg_minor:
        pg_full = f"pg{pg_major} {pg_minor}"
    osSys(f"{CTL} install {pg_full}")

    if util.is_empty_writable_dir("/data") == 0:
        util.message("## symlink empty local data directory to empty /data ###")
        osSys("rm -rf data; ln -s /data data")

    core_exts_installed = False
    if dbName is None:
        pass
    else:
        pg_maj = f"pg{pg_major}"
        if autostart is True:
            util.autostart_config(pg_maj)
        else:
            osSys(f"{CTL} init {pg_maj}")

        osSys(f"{CTL} config {pg_maj} --port={port}")

        osSys(f"{CTL} start {pg_maj}")
        time.sleep(pause)

        db.create(dbName, User, Passwd, pg_major, spock_ver)
        time.sleep(pause)
        core_exts_installed = True

    if core_exts_installed is False:
        install_disabled_exts(pg_major, CORE_EXTS)

        if pg_major in ["14", "15"]:
            install_disabled_exts(pg_major, EXTS_15)

    if extensions == "all":
        if pg_major not in ["15", "16"]:
            util.message(f"'--extensions all' not supported for pg{pg_major}", "warning")
            return

        install_disabled_exts(pg_major, MORE_EXTS)



def install_disabled_exts(pg_major, exts):
    util.message(f"setup.install_disabled_exts({pg_major}, {exts}", "debug")

    ext_l = exts.split()
    for ext in ext_l:
        full_ext = f"{ext}-pg{pg_major}"
        util.message(f"installing {full_ext}")
        osSys(f"{CTL} install {full_ext} --disabled --silent",
                       fatal_exit=False, is_silent=True)


if __name__ == "__main__":
    fire.Fire(setup_pgedge)
