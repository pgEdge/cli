#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, random, json, socket, datetime
import util, fire, meta, subprocess


def create(db=None, User=None, Passwd=None, Id=None, pg=None):
    """
    Create a pg db with spock installed into it.


     Usage:
         To create a superuser than has access to the whole cluster of db's
            db create -d <db> -U <usr> -P <passwd>

         to create an admin user that owns a specifc tennant database
            db create -I <id>  [-P <passwd>]

    """

    if db == None:
        db = os.getenv("pgName", None)

    if User == None:
        User = os.getenv("pgeUser", None)

    ## one way or another, the user that creates the db will have a password
    if Passwd == None:
        Passwd = os.getenv("pgePasswd", None)
        if Passwd == None:
            Passwd = util.get_random_password()

    if pg == None:
        pg_v = util.get_pg_v(pg)
        pg = pg_v[2:]

    nc = "./nodectl "
    ncb = nc + "pgbin " + str(pg) + " "

    privs = ""
    if Id:
        privs = "NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT LOGIN"
        User = "admin_" + str(Id)
        db = "db_" + str(Id)
    elif User and db:
        privs = "SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN"
    else:
        util.exit_message("db_create() must have parms of (-I) or (-U -d)")

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

    util.echo_cmd(nc + "tune pg" + str(pg))

    util.echo_cmd(nc + "install snowflake --no-restart")

    if str(pg) == "17":
        spock_comp = "spock32-pg" + str(pg)
    else:
        util.echo_cmd(nc + "install readonly --no-restart")
        util.echo_cmd(nc + "install foslots  --no-restart")
        spock_comp = "spock31-pg" + str(pg)

    st8 = util.get_comp_state(spock_comp)
    if st8 in ("Installed", "Enabled"):
        cmd = "CREATE EXTENSION spock"
        rc3 = util.echo_cmd(ncb + '"psql -q -c \\"' + cmd + '\\" ' + str(db) + '"')
    else:
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

    if Id:
        print(util.json_dumps(return_json))

    return


def set_guc(guc_name, guc_value, replace=True, pg=None):
    """Set GUC"""
    pg_v = util.get_pg_v(pg)

    util.change_pgconf_keyval(pg_v, guc_name, str(guc_value), replace)
    util.echo_cmd(f"./nc reload {pg_v}")


def show_guc(guc_name, pg=None):
    """Show GUC"""
    pg_v = util.get_pg_v(pg)
    if guc_name == "all" or guc_name == "*":
        guc_name = "%"
    elif "*" in guc_name:
        guc_name = guc_name.replace("*", "%")

    sql = f"SELECT name, setting, pending_restart FROM pg_settings WHERE name LIKE '{guc_name}'"
    util.run_psyco_sql(pg_v, "postgres", sql)
    sys.exit(0)


def dump(object, source_dsn, file="/tmp/db_0.sql", schema_only=False, pg=None):
    """Dump a database, schema, object from the source dsn to a file

    object: database or database.schema.object where schema and object can contain wildcard '*'
    source_dsn: host=x, port=x, username=x (in any order)
    file: location and file name for dump
    schema_only: do not include data in the pg_dump
    """
    pg_v = util.get_pg_v(pg)

    cmd = f'./nodectl pgbin {pg_v} "pg_dump '

    if "=" in source_dsn:
        if "," in source_dsn:
            host = source_dsn.split("host=")[1].split(",")[0]
            port = source_dsn.split("port=")[1].split(",")[0]
            user = source_dsn.split("user=")[1].split(",")[0]
            cmd = f"{cmd} -h {host} -p {port} -U {user} "
        else:
            util.exit_message(
                "source_dsn must be in format: host=x, port=x, username=x, password=x"
            )
    else:
        util.exit_message(
            "source_dsn must be in format: host=x, port=x, username=x, password=x"
        )

    if "." in object:
        db = object.split(".")[0]
        schema = object.split(".")[1]
        table = object.split(".")[2]
        cmd = f"{cmd} --schema='{schema}' --table='{table}' {db}"
    else:
        cmd = f"{cmd} {object} -N spock -N pg_catalog "

    if schema_only == True:
        cmd = f"{cmd} --schema-only"

    cmd = f'{cmd} --clean -f {file} "'
    print(cmd)
    os.system(cmd)


def restore(object, target_dsn, file="/tmp/db_0.sql", pg=None):
    """Restore a database, schema, object from a file to the target_dsn

    object: database.schema.object where schema and object can contain wildcard '*'
    target_dsn: host=x, port=x, username=x, database=x (in any order)
    file: location and file name for dump
    """

    os.system(f"cat {file} | grep -v -E '(spock)' > /tmp/db_1.sql")
    file = "/tmp/db_1.sql"

    pg_v = util.get_pg_v(pg)
    cmd = f'./nodectl pgbin {pg_v} "psql '

    if "=" in target_dsn:
        if "," in target_dsn:
            host = target_dsn.split("host=")[1].split(",")[0]
            port = target_dsn.split("port=")[1].split(",")[0]
            user = target_dsn.split("user=")[1].split(",")[0]
            cmd = f"{cmd} -h {host} -p {port} -U {user} "
        else:
            util.exit_message(
                "target_dsn must be in format: host=x, port=x, username=x, password=x"
            )
    else:
        util.exit_message(
            "target_dsn must be in format: host=x, port=x, username=x, password=x"
        )

    if "." in object:
        db = object.split(".")[0]
    else:
        db = object

    cmd = f'{cmd} {db} -f {file} "'
    print(cmd)
    os.system(cmd)


def migrate(object, source_dsn, target_dsn, schema_only=False, pg=None):
    """Migrate a database, schema, object from a source_dsn to the target_dsn

    object: database.schema.object where schema and object can contain wildcard '*'
    source_dsn: host=x, port=x, username=x, password=x, database=x (in any order)
    target_dsn: host=x, port=x, username=x, password=x, database=x (in any order)
    schema_only: do not include data in the pg_dump
    """
    pass


if __name__ == "__main__":
    fire.Fire(
        {
            "create": create,
            "set-guc": set_guc,
            "show-guc": show_guc,
            "dump": dump,
            "restore": restore,
            "migrate": migrate,
        }
    )
