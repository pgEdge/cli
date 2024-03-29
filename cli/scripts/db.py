#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

import os
import sys
import platform
import subprocess
import json

import util
import fire


def create(db=None, User=None, Passwd=None, pg=None, spock=None):
    """
    Create a pg db with spock installed into it.


     Usage:
         To create a database owned by a specific user
            db create -d <db> -U <usr> -P <passwd>

    """

    util.message(f"db.create(db={db}, User={User}, Passwd={Passwd}, pg={pg}, spock={spock})", "debug")

    # one way or another, the user that creates the db will have a password
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
       major_ver = util.DEFAULT_SPOCK
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


def test_io():
    """ Use the 'fio' Flexible IO Tester on pg data directory """

    if platform.system() != "Linux":
        util.exit_message("Must run on Linux w 'fio' package installed")

    rc = os.system("fio --version >/dev/null 2>&1")
    if rc != 0:
        util.exit_message("Missing 'fio'. In Rocky install via: \n" + \
          "  'dnf --enablerepo=devel install fio' \n" + \
          "or in Ubuntu perhaps via: \n" + \
          "  'apt install fio'")

    fio_cmd = "-rw=write -bs=8Ki -fsync=1 -runtime=2s -size=2GB -directory=/tmp -name=test_io  --output-format=json"

    j_out_file = "/tmp/test_io.json"
    rc =  os.system(f"fio {fio_cmd} > {j_out_file}")

    j_out = util.get_parsed_json(j_out_file)

    print(json.dumps(j_out, indent=2))



def set_readonly(readonly="off", pg=None):
    """Turn PG read-only mode 'on' or 'off'."""

    if readonly not in ("on", "off"):
        util.exit_message("  readonly flag must be 'off' or 'on'")

    pg_v = util.get_pg_v(pg)

    try:
        con = util.get_pg_connection(pg_v, "postgres", util.get_user())
        cur = con.cursor(row_factory=psycopg.rows.dict_row)

        util.change_pgconf_keyval(pg_v, "default_transaction_read_only", readonly, True)

        util.message("reloading postgresql.conf")
        cur.execute("SELECT pg_reload_conf()")
        cur.close()
        con.close()

    except Exception as e:
        util.exit_exception(e)

    sys.exit(0)



if __name__ == "__main__":
    fire.Fire(
        {
            "create": create,
            "guc-set": guc_set,
            "guc-show": guc_show,
            "set-readonly": set_readonly,
            "test-io": test_io
        }
    )
