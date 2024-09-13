
#  Copyright 2024-2024 PGEDGE  All rights reserved. #

import os, sys, time, getpass

os.chdir(os.getenv("MY_HOME"))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

import fire, util, db

CORE_EXTS="spock40 snowflake lolor vector postgis"

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


def check_pre_reqs(User, Passwd, db, port, pg_major, pg_minor, spock, autostart):
    util.message(f"setup.check_pre_reqs(User={User}, db={db}, port={port}, pg_major={pg_major}, " + \
        f"pg_minor={pg_minor}, spock={spock}, autostart={autostart}", "debug")

    util.message("#### Checking for Pre-Req's #########################")

    platf = util.get_platform()

    if platf == "Linux":
        if util.glibc_ver() < "2.28":
            util.exit_message("Linux has an older version of glibc (< el8)")

        if autostart:
            util.autostart_verify_prereqs()
    
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
    util.message(f"    - Using port {port}")

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

    if (User is None) or (Passwd is None) or (db is None):
        util.exit_message("Must specify User, Passwd & db")

    kount = 0

    if verifyUser(User):
        kount = kount + 1
    if verifyPasswd(Passwd):
        kount = kount + 1
    if verifyDbname(db):
        kount = kount + 1

    if kount < 3:
        sys.exit(1)

    if spock:
       util.message(f"  Verify spock '{spock}' is valid and unique")
       ns = util.num_spocks(pg_major, spock, True)
       if ns == 0:
           util.exit_message(f"No available version of spock like '{spock}*' for pg{pg_major}")
       elif ns > 1:
           util.exit_message(f"More than 1 spock version available matching '{spock}*'")


def inputPgVer(p_default):
    util.message(f"setup.inputPgVer({p_default})", "debug")
    
    while True:
        try:
            pgver = input(f"  PG Version({p_default}): ")
        except KeyboardInterrupt:
            util.exit_message("cancelled")
        except Exception:
            return(None)

        if pgver == "":
            pgver = p_default

        if verifyPgVer(pgver):
            return(pgver)


def verifyPgVer(p_pgver):
    util.message(f"setup.verifyPgVer({p_pgver}", "debug")

    if (p_pgver >= "14") and (p_pgver <= "17"):
        return(True)

    util.message("Must be 14, 15, 16, or 17", "error")
    return(False)



def inputUser():
    util.message(f"setup.inputUser()", "debug")

    while True:
        try:
            user = input("        DB Owner: ")
        except KeyboardInterrupt:
            util.exit_message("cancelled")
        except Exception:
            return(None)

        if verifyUser(user):
            return(user)


def verifyUser(User):
    util.message(f"setup.verifyUser({User})", "debug")

    usr_l = User.lower()
    if usr_l == "pgedge":
        util.message("The user defined superuser may not be called 'pgedge'", "error")
        return(False)

    if usr_l == util.get_user():
        util.message("The user-defined superuser may not be the same as the OS user", "error")
        return(False)

    usr_len = len(usr_l)
    if (usr_len < 1) or (usr_len > 64):
        util.message("The user-defined superuser must be >=1 and <= 64 in length", "error")
        return(False)

    return(True)


def inputPasswd():
    util.message(f"setup.inputPasswd()", "debug")
    while True:
        try:
            passwd = getpass.getpass("        Password: ")
            passwd2 = getpass.getpass("Confirm Password: ")

            if passwd != passwd2:
                util.message("passwords do not match", "error")
                continue

        except KeyboardInterrupt:
            util.exit_message("cancelled")

        except Exception:
            return(None)

        if verifyPasswd(passwd):
            return(passwd)


def verifyPasswd(Passwd):
    util.message(f"setup.verifyPasswd({Passwd})", "debug")

    pwd_len = len(Passwd)
    if (pwd_len < 6) or (pwd_len > 128):
        util.message("The password must be >= 6 and <= 128 in length", "error")
        return(False)

    for pwd_char in Passwd:
        pwd_c = pwd_char.strip()
        if pwd_c in (",", "'", '"', "@", ""):
            util.message(
                "The password must not contain {',', \"'\", \", @, or a space", "error")
            return(False)

    return(True)


def inputDbname():
    util.message(f"setup.inputDbname()", "debug")
    while True:
        try:
            dbname = input("         DB Name: ")
        except KeyboardInterrupt:
            util.exit_message("cancelled")
        except Exception:
            return(None)

        if verifyDbname(dbname):
            return(dbname)


def verifyDbname(p_db):

    l_db = str(p_db).lower()

    if l_db != p_db:
        util.message(f"pgEdge Dbname's are case insensitive for your own sanity", "warning")

    if util.is_pg_reserved_word(l_db):
        util.message(f"Dbname '{l_db}' is a postgres reserved word", "error")
        return(False)

    if str(l_db[0]).isdigit():
        util.message(f"Dbname '{l_db}' first character may not be a digit", "error")
        return(False)

    for c in l_db:
        if c.isdigit() or c.isalpha() or c == "_":
            pass
        else:
            util.message(f"Dbname '{l_db}' characters can only be (a-z), (1-9), or an (_)", "error") 
            return(False)

    return (True)


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
       :param pg_ver: Defaults to latest prod version of pg, such as 16.  May be pinned to a specific pg version such as 16.4
       :param spock_ver: Defaults to latest prod version of spock, such as 4.0.  May be pinned to a specific spock version such as 4.0.1
       :param autostart: Defaults to False
    """

    if os.getenv("isAutoStart", "") == "True":
        autostart = True

    pgeExt = os.getenv("pgeExtensions", None)
    if pgeExt:
        extensions = pgeExt


    util.message(f"setup.pgedge(User={User}, Passwd='***', dbName={dbName}, port={port}, \n" + \
                 f"    pg_ver={pg_ver}, spock_ver={spock_ver}, autostart={autostart})", "debug")

    if not port:
        port = os.getenv("pgePort", "5432")

    if autostart is False:
        autos = os.getenv("isAutoStart")
        if autos == "True":
           autostart = True
        else:
           autostart = False 

    interactive = False
    if User is None:
        interactive = True
        User = inputUser()

    if Passwd is None:
        interactive = True
        Passwd = inputPasswd()

    if dbName is None:
        interactive = True
        dbName = inputDbname()

    df_pg = util.get_default_pg()
    df_pg = os.getenv("pgN", df_pg)
    if (pg_ver is None) and (interactive is True):
        pg_ver = inputPgVer(p_default=df_pg)
    else:
        pg_ver = df_pg

    pg_major, pg_minor = parse_pg(pg_ver)

    check_pre_reqs(User, Passwd, dbName, port, pg_major, pg_minor, spock_ver, autostart)

    pause = 2
    pg_full = f"pg{pg_major}"

    if pg_minor:
        pg_full = f"pg{pg_major} {pg_minor}"
    osSys(f"{CTL} install {pg_full}")

    if util.is_empty_writable_dir("/data") == 0:
        util.message("## symlink empty local data directory to empty /data ###")
        osSys("rm -rf data; ln -s /data data")

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


if __name__ == "__main__":
    fire.Fire(setup_pgedge)
