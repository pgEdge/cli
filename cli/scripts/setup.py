
#  Copyright 2024-2024 PGEDGE  All rights reserved. #

import os, sys, time

os.chdir(os.getenv("MY_HOME"))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

import fire, util, db, setup_core

CTL="./pgedge"


def setup_pgedge(User=None, Passwd=None, dbName=None, port=None, pg_ver=None, spock_ver=None, autostart=False, interactive=False, yes=False):
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
       :param interactive: Defaults to False
       :param yes: Accept input parms without prompting to confirm (always set to True when interactive is false)
    """

    pgN = os.getenv("pgN", "")
    if (pgN > "" ) and (pg_ver is None):
        util.message("parm '--pg' is deprecated.  use '--pg_ver' instead", "warning")
        pg_ver = pgN


    if os.getenv("isAutoStart", "") == "True":
        autostart = True

    pgePasswd = os.getenv("pgePasswd", "")
    if (pgePasswd > "" ) and (Passwd is None):
        util.message("over-riding Passwd with $pgePasswd", "debug")
        Passwd = pgePasswd

    util.message(f"""
setup.pgedge(User={User}, Passwd={Passwd}, dbName={dbName}, port={port}, pg_ver={pg_ver},
  spock_ver={spock_ver}, autostart={autostart}, interactive={interactive}, yes={yes})
""", "debug")

    if interactive is False:
        # don't prompt to continue unless in interactive mode
        yes = True

    if not port:
        port = os.getenv("pgePort", "5432")

    if autostart is False:
        autos = os.getenv("isAutoStart")
        if autos == "True":
           autostart = True
        else:
           autostart = False 

    if User is None and interactive:
        User = setup_core.inputUser()

    if Passwd is None and interactive:
        Passwd = setup_core.inputPasswd()
        # pg installer will need the passwd securely sent to it
        os.environ["pgePasswd"] = Passwd

    if dbName is None and interactive:
        dbName = setup_core.inputDbname()

    if pg_ver is None:
       df_pg = util.get_default_pg()
       if interactive:
          pg_ver = setup_core.inputPgVer(df_pg)
       else:
          pg_ver = df_pg

    pg_major, pg_minor = setup_core.parse_pg(pg_ver)

    setup_core.check_pre_reqs(
        User, Passwd, dbName, port, pg_major, pg_minor, spock_ver, autostart)

    if interactive and yes is False:
        y_or_n = input("Do you want to continue? [Y/n] ")
        y_or_n = y_or_n.lower()
        if y_or_n in ['y', 'yes', '' ]:
            pass
        else:
            util.exit_message("Goodbye!", 0)

    setup_core.osSys(f"{CTL} install pg{pg_major} {pg_minor}")

    if util.is_empty_writable_dir("/data") == 0:
        util.message("## symlink empty local data directory to empty /data ###")
        setup_core.osSys("rm -rf data; ln -s /data data")

    if dbName is None:
        pass
    else:
        pg_maj = f"pg{pg_major}"
        if autostart is True:
            util.autostart_config(pg_maj)
        else:
            setup_core.osSys(f"{CTL} init {pg_maj}")

        setup_core.osSys(f"{CTL} config {pg_maj} --port={port}")

        setup_core.osSys(f"{CTL} start {pg_maj}")

        time.sleep(2)
        db.create(dbName, User, Passwd, pg_major, spock_ver)
        time.sleep(2)


if __name__ == "__main__":
    fire.Fire(setup_pgedge)
