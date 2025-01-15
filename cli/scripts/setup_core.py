
#  Copyright 2024-2024 PGEDGE  All rights reserved. #

import os, sys, time, getpass
import fire, util, db


def osSys(cmd, fatal_exit=True, is_silent=False):
    if not is_silent:
        s_cmd = util.scrub_passwd(cmd)
        util.message("#")
        util.message("# " + str(s_cmd))

    rc = os.system(cmd)
    if rc != 0 and fatal_exit:
        util.exit_message("FATAL ERROR running setup pgedge", 1)

    return


def check_pre_reqs(
    User, Passwd, db, port, pg_major, pg_minor, spock, autostart):

    util.message(
f"""setup_core.check_pre_reqs(User={User}, Passwd={Passwd}, db={db}, port={port},
    pg_major={pg_major}, pg_minor={pg_minor}, spock={spock},
    autostart={autostart}""", 'debug')

    ##util.message("Checking for Pre-Req's", "info")

    platf = util.get_platform()

    if platf == "Linux":
        if util.glibc_ver() < "2.28":
            util.exit_message("Linux has an older version of glibc (< el8)")

        if autostart:
            util.autostart_verify_prereqs()
    
    p3_minor_ver = util.get_python_minor_version()
    if p3_minor_ver < 9:
        util.exit_message("Python version must be greater than 3.9")

    if util.is_admin():
        util.exit_message(
            "You must install as non-root user with passwordless sudo privileges")

    if not verifyPort(port):
        sys.exit(1)

    if util.is_socket_busy(int(port)):
        util.exit_message(f"Port {port} is unavailable")

    if pg_major not in util.VALID_PG:
        util.exit_message(f"pg {pg_major} must be in {util.VALID_PG}")

    if pg_minor > "":
       num_pg_mins = util.num_pg_minors(pg_minor, True)
       if num_pg_mins == 0:
           util.exit_message(f"No available version of pg like '{pg_minor}*'")
       elif num_pg_mins > 1:
           util.exit_message(
               f"{num_pg_mins} versions available matching '{pg_minor}*'")

    data_dir = f"data/pg{pg_major}"
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
            util.exit_message(
                f"No available version of spock like '{spock}*' for pg{pg_major}")
        elif ns > 1:
            util.exit_message(
                f"More than 1 spock version available matching '{spock}*'")
        spock_display = spock
    else:
        sd = util.get_default_spock(pg_major)
        spock_display = f"{sd[0]}.{sd[1]}"

    if pg_minor > " ":
        pg_display = pg_minor
    else:
        pg_display = pg_major

    setup_info = f"""
######### pgEdge Setup Info ###########
#      User: {User}
#  Database: {db}:{port}
#  Postgres: {pg_display}
#     Spock: {spock_display}
# Autostart: {autostart}
#  Platform: {util.get_ctlib_dir()}
#######################################
"""
    util.message(setup_info, "info")


def inputPgVer(p_default):
    util.message(f"setup_core.inputPgVer({p_default})", "debug")
    
    while True:
        try:
            pgver = input(f"  PG Ver({p_default}): ")
        except KeyboardInterrupt:
            util.exit_message("cancelled")
        except Exception:
            return(None)

        if pgver == "":
            pgver = p_default

        if verifyPgVer(pgver):
            return(pgver)


def verifyPgVer(p_pgver):
    util.message(f"setup_core.verifyPgVer({p_pgver})", "debug")

    if (p_pgver >= "14") and (p_pgver <= "17"):
        return(True)

    util.message("Must be 14, 15, 16, or 17", "error")
    return(False)


def inputPort ():
    util.message("setup_core.inputPort()", "debug")
    
    while True:
        try:
            port  = input(f"  Port(5432): ")
        except KeyboardInterrupt:
            util.exit_message("cancelled")
        except Exception:
            return(None)

        if port  == "":
            port = "5432"

        if verifyPort(port):
            return(port)


def verifyPort(p_port):
    util.message(f"setup_core.verifyPort({p_port})", "debug")

    try:
        i_port = int(p_port)
    except Exception:
        util.message("Port must be numeric", "error")
        return(False)

    if (i_port < 0) or (i_port > 65535):
        util.message("Port must be >= 0 and <= 65535", "error")
        return(False)

    return(True)



def inputUser():
    util.message(f"setup_core.inputUser()", "debug")

    while True:
        try:
            user = input("    DB Owner: ")
        except KeyboardInterrupt:
            util.exit_message("cancelled")
        except Exception:
            return(None)

        if verifyUser(user):
            return(user)


def verifyUser(User):
    util.message(f"setup_core.verifyUser({User})", "debug")

    usr_l = User.lower()
    if usr_l == "pgedge":
        util.message("The user defined superuser may not be 'pgedge'", "error")
        return(False)

    if usr_l == util.get_user():
        util.message("The superuser may not be same as OS user", "error")
        return(False)

    usr_len = len(usr_l)
    if (usr_len < 1) or (usr_len > 64):
        util.message("The superuser must be >=1 and <= 64 in length", "error")
        return(False)

    return(True)


def inputPasswd():
    util.message(f"setup_core.inputPasswd()", "debug")
    while True:
        try:
            passwd = getpass.getpass("    Password: ")
            passwd2 = getpass.getpass("     Confirm: ")

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
    util.message(f"setup_core.verifyPasswd({Passwd})", "debug")

    pwd_len = len(Passwd)
    if (pwd_len < 6) or (pwd_len > 128):
        util.message("The password must be >= 6 and <= 128 in length", "error")
        return(False)

    for pwd_char in Passwd:
        pwd_c = pwd_char.strip()
        if pwd_c in (",", "'", '"', "@", ""):
            util.message(
                "The password must not contain " + \
                "{',', \"'\", \", @, or a space", "error")
            return(False)

    return(True)


def inputDbname():
    util.message(f"setup_core.inputDbname()", "debug")
    while True:
        try:
            dbname = input("     DB Name: ")
        except KeyboardInterrupt:
            util.exit_message("cancelled")
        except Exception:
            return(None)

        if verifyDbname(dbname):
            return(dbname)


def verifyDbname(p_db):

    l_db = str(p_db).lower()

    if l_db != p_db:
        util.message(f"pgEdge Dbname's are case insensitive " + \
          "for your own sanity", "warning")

    if util.is_pg_reserved_word(l_db):
        util.message(f"Dbname '{l_db}' is a postgres reserved word", "error")
        return(False)

    if str(l_db[0]).isdigit():
        util.message(f"Dbname '{l_db}' first character may not be digit", "error")
        return(False)

    for c in l_db:
        if c.isdigit() or c.isalpha() or c == "_":
            pass
        else:
            util.message(f"Dbname '{l_db}' characters can only " + \
                "be (a-z), (1-9), or an (_)", "error") 
            return(False)

    return (True)


def parse_pg(pg=""):
    if pg == "":
        return("", "")

    pg = str(pg)

    pg_major = pg
    pg_minor = ""
    if "." in pg:
        pg_minor = str(pg)
        pg_major = str(pg)[:2]
   
    return(pg_major, pg_minor)

