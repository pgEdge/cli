#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

import os, sys
import util, fire


def create(db=None, User=None, Passwd=None, pg=None, spock=None):
    """
    Create a pg db with spock installed into it.


     Usage:
         To create a database owned by a specific user
            db create -d <db> -U <usr> -P <passwd>

    """

    if db is None:
        db = os.getenv("pgName", None)

    if User is None:
        User = os.getenv("pgeUser", None)

    # one way or another, the user that creates the db will have a password
    if Passwd is None:
        Passwd = os.getenv("pgePasswd", None)
        if Passwd is None:
            Passwd = util.get_random_password()

    if pg is None:
        pg_v = util.get_pg_v(pg)
        pg = pg_v[2:]

    nc = "./pgedge "
    ncb = nc + "pgbin " + str(pg) + " "

    privs = ""
    if User and db:
        privs = "SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN"
    else:
        util.exit_message("db.create() must have parms of -User & -db")

    cmd = "CREATE ROLE " + User + " PASSWORD '" + Passwd + "' " + privs
    rc1 = util.echo_cmd(ncb + '"psql -q -c \\"' + cmd + '\\" postgres"')
    cmd = (
        "CREATE ROLE replicator PASSWORD '"
        + Passwd
        + "' "
        + "SUPERUSER LOGIN REPLICATION"
    )
    rc1 = util.echo_cmd(ncb + '"psql -q -c \\"' + cmd + '\\" postgres"')

    cmd = "createdb '" + db + "' --owner='" + User + "'"
    rc2 = util.echo_cmd(ncb + '"' + cmd + '"')

    util.echo_cmd(f"{nc} tune pg{pg}")

    util.echo_cmd(f"{nc} install snowflake-pg{pg} --no-restart")

    if spock is None:
       major_ver = "32"
       ver = ""
    else:
       major_ver = f"{str(spock)[:1]}{str(spock)[2:3:1]}"
       ver = spock

    spock_comp = f"spock{major_ver}-pg{pg}"
    st8 = util.get_comp_state(spock_comp)

    if st8 in ("Installed", "Enabled"):
        cmd = "CREATE EXTENSION spock"
        rc3 = util.echo_cmd(ncb + '"psql -q -c \\"' + cmd + '\\" ' + str(db) + '"')
    else:
        spock_comp = f"spock{major_ver}-pg{pg} {ver}"
        rc3 = util.echo_cmd(nc + "install " + spock_comp + " -d " + str(db))

    cmd = "CREATE EXTENSION snowflake"
    rc4 = util.echo_cmd(ncb + '"psql -q -c \\"' + cmd + '\\" ' + str(db) + '"')

    rm_data = os.getenv("isRM_DATA", "False")
    if rm_data == "True":
        util.message("Removing data directory at your request")
        util.echo_cmd(nc + "stop")
        util.echo_cmd("rm -r data")

    rcs = rc1 + rc2 + rc3 + rc4
    if rcs == 0:
        status = "success"
    else:
        status = "error"

    return_json = {}
    return_json["status"] = status
    return_json["db_name"] = db
    return_json["users"] = []

    user_json = {}
    user_json["user"] = User
    user_json["passwd"] = Passwd
    return_json["users"].append(user_json)

    return


def guc_set(guc_name, guc_value, pg=None):
    """Set GUC"""
    pg_v = util.get_pg_v(pg)

    if pg is None:
        pg_v = util.get_pg_v(pg)
        pg = pg_v[2:]

    nc = "./pgedge "
    ncb = nc + "pgbin " + str(pg) + " "

    cmd = f"ALTER SYSTEM SET {guc_name} = {guc_value}"
    rc1 = util.echo_cmd(ncb + '"psql -q -c \\"' + cmd + '\\" postgres"',False)    
    cmd = f"SELECT pg_reload_conf()"
    rc2 = util.echo_cmd(ncb + '"psql -q -c \\"' + cmd + '\\" postgres"',False)
    rcs = rc1 + rc2
    if rcs == 0:
        util.message(f"Set GUC {guc_name} to {guc_value}","info")
    else:
        util.message("Unable to set GUC","error")


def guc_show(guc_name, pg=None):
    """Show GUC"""
    pg_v = util.get_pg_v(pg)
    if guc_name == "all" or guc_name == "*":
        guc_name = "%"
    elif "*" in guc_name:
        guc_name = guc_name.replace("*", "%")

    sql = f"SELECT name, setting, pending_restart FROM pg_settings WHERE name LIKE '{guc_name}'"
    util.run_psyco_sql(pg_v, "postgres", sql)
    sys.exit(0)


if __name__ == "__main__":
    fire.Fire(
        {
            "create": create,
            "guc-set": guc_set,
            "guc-show": guc_show,
        }
    )
