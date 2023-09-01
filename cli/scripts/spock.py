#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import sys, os, json, subprocess, time
import util, meta, api, fire

nc = "./nodectl "

isAutoStart   = str(os.getenv("isAutoStart",   "False"))
  
## force use of PGPASSWORD from ~/.pgpass
os.environ["PGPASSWORD"] = ""

try:
  import psycopg
except ImportError as e:
  util.exit_message("Missing 'psycopg' module from pip", 1)


def error_exit(p_msg, p_rc=1):
    util.message("ERROR: " + p_msg)
    if util.debug_lvl() == 0:
      os.system(nc + "remove pgedge")

    sys.exit(p_rc)


def json_dumps(p_input):
  if os.getenv("isJson", "") == "True":
    return(json.dumps(p_input))

  return(json.dumps(p_input, indent=2))


def get_pg_connection(pg_v, db, usr):
  dbp = util.get_column("port", pg_v)

  if util.debug_lvl() > 0:
    util.message(f"get_pg_connection(): dbname={db}, user={usr}, port={dbp}", "debug")

  try:
    con = psycopg.connect(dbname=db, user=usr, host="127.0.0.1", port=dbp, autocommit=False)
  except Exception as e:
    util.exit_exception(e)

  return(con)


def run_psyco_sql(pg_v, db, cmd, usr=None):
  if usr == None:
    usr = util.get_user()

  if util.is_verbose():
    util.message(cmd, "info")

  if util.debug_lvl() > 0:
    util.message(cmd, "debug")

  con = get_pg_connection(pg_v, db, usr)
  if util.debug_lvl() > 0:
    util.message("run_psyco_sql(): " + str(con), "debug")

  try:
    cur = con.cursor(row_factory=psycopg.rows.dict_row)
    cur.execute(cmd)
    con.commit()

    print(json_dumps(cur.fetchall()))

    try:
      cur.close()
      con.close()
    except Exception as e:
      pass

  except Exception as e:
    if "already exists" in str(e):
      util.exit_message("already exists", 0)
    elif "already subscribes" in str(e):
      util.exit_message("already subscribes", 0)
    else:
      util.exit_exception(e)


def change_pg_pwd(pwd_file, db="*", user="postgres", host="localhost", pg=None ):
  pg_v = util.get_pg_v(pg)
  dbp = util.get_column("port", pg_v)

  if os.path.isfile(pwd_file):
    file = open(pwd_file, 'r')
    line = file.readline()
    pg_password = line.rstrip()
    file.close()
    os.system("rm " + pwd_file)
  else:
    util.exit_message("invalid pwd file: " + str(pwd_file), 1) 
  
  rc = util.change_pgpassword(p_passwd=pg_password, p_port=dbp, p_host=host, p_db="*", p_user=user, p_ver=pg_v)
  sys.exit(rc)


def get_eq(parm, val, sufx, set=False):
  if set==False:
    colon_equal = str(parm) + " := '" + str(val) + "'" + str(sufx)
  else:
    colon_equal = str(parm) + " := '{" + str(val) + "}'" + str(sufx)
  return(colon_equal)


def node_add_interface(node_name, interface_name, dsn, db, pg=None):
  """Add a new node interface."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.node_add_interface(" + \
           get_eq("node_name", node_name, ", ") + \
           get_eq("interface_name", interface_name, ", ") + \
           get_eq("dsn", dsn, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def node_drop_interface(node_name, interface_name, db, pg=None):
  """Delete a node interface."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.node_drop_interface(" + \
           get_eq("node_name", node_name, ", ") + \
           get_eq("interface_name", interface_name, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def node_create(node_name, dsn, db, pg=None):
  """Define a node for spock."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.node_create(" + \
           get_eq("node_name", node_name, ", ") + \
           get_eq("dsn",       dsn,       ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def node_drop(node_name, db, pg=None):
  """Remove a spock node."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.node_drop(" + get_eq("node_name", node_name, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def node_alter_location(node_name, location, db, pg=None):
  """Set location details for spock node."""

  pg_v = util.get_pg_v(pg)

  [location_nm, country, state, lattitude, longitude] = util.get_location_dtls(location)

  sql = """
UPDATE spock.node
   SET location_nm = ?, country = ?, state = ?, lattitude = ?, longitude = ?
 WHERE location = ?
"""

  con = get_pg_connection(pg_v, db, util.get_user())

  rc = 0
  try:
    con.transaction()
    cur.execute(sql, [location_nm, country, state, lattitude, longitude])
    con.commit()
  except Exception as e:
    util.print_exception(e)
    con.rollback()
    rc = 1

  sys.exit(rc)


def node_list(db, pg=None):
  """Display node table."""
  pg_v = util.get_pg_v(pg)
  sql = """
SELECT node_id, node_name FROM spock.node ORDER BY node_name
"""
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_create(set_name, db, replicate_insert=True, replicate_update=True, 
                           replicate_delete=True, replicate_truncate=True, pg=None):
  """Define a replication set."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.repset_create(" + \
           get_eq("set_name", set_name, ", ") + \
           get_eq("replicate_insert",   replicate_insert,   ", ") + \
           get_eq("replicate_update",   replicate_update,   ", ") + \
           get_eq("replicate_delete",   replicate_delete,   ", ") + \
           get_eq("replicate_truncate", replicate_truncate, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_alter(set_name, db, replicate_insert=True, replicate_update=True, 
                 replicate_delete=True, replicate_truncate=True, pg=None):
  """Modify a replication set."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.repset_alter(" + \
           get_eq("set_name", set_name, ", ") + \
           get_eq("replicate_insert",   replicate_insert,   ", ") + \
           get_eq("replicate_update",   replicate_update,   ", ") + \
           get_eq("replicate_delete",   replicate_delete,   ", ") + \
           get_eq("replicate_truncate", replicate_truncate, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_alter_seq():
  """Change a replication set sequence."""
  util.exit_message("Not implemented yet.")


def repset_drop(set_name, db, pg=None):
  """Remove a replication set."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.repset_drop(" + get_eq("set_name", set_name, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_add_seq(set_name, db, relation, synchronize_data=False, pg=None):
  """Add a sequence to a replication set."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.repset_add_seq(" + \
           get_eq("set_name", set_name, ", ") + \
           get_eq("relation", relation, ", ") + \
           get_eq("synchronize_data", synchronize_data, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_add_all_seqs(set_name, db, schema_names, synchronize_data=False, pg=None):
  """Add sequences to a replication set."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.repset_add_all_seqs(" + \
           get_eq("set_name", set_name, ", ") + \
           get_eq("schemas", schema_names, ", ") + \
           get_eq("synchronize_data", synchronize_data, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_remove_seq(set_name, relation, db, pg=None):
  """Remove a sequence from a replication set."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.repset_remove_seq(" + \
           get_eq("set_name", set_name, ", ") + \
           get_eq("relation", relation, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_list_tables(schema, db, pg=None):
  """List tables in replication sets."""
  pg_v = util.get_pg_v(pg)

  sql =  "SELECT * FROM spock.tables"
  if (schema != "*"):
      sql = sql + " WHERE nspname='" + schema + "'"
  sql = sql + " ORDER BY set_name, nspname, relname;"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_create(subscription_name, provider_dsn, db, 
               replication_sets=('default','default_insert_only','ddl_sql'),
               synchronize_structure=False, synchronize_data=False, 
               forward_origins='', apply_delay=0, pg=None):
  """Create a subscription."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.sub_create(" + \
           get_eq("subscription_name",     subscription_name,     ", ") + \
           get_eq("provider_dsn",          provider_dsn,          ", ") + \
           get_eq("replication_sets",      ','.join(replication_sets) ,", ", True) + \
           get_eq("synchronize_structure", synchronize_structure, ", ") + \
           get_eq("synchronize_data",      synchronize_data,      ", ") + \
           get_eq("forward_origins",       str(forward_origins), ", ", True) + \
           get_eq("apply_delay",           apply_delay,           ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_drop(subscription_name, db, pg=None):
  """Delete a subscription."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.sub_drop(" + get_eq("subscription_name", subscription_name, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_enable(subscription_name, db, immediate=False, pg=None):
  """Make a subscription live."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.sub_enable(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("immediate",         immediate,         ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_disable(subscription_name, db, immediate=False, pg=None):
  """Put a subscription on hold and disconnect from provider."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.sub_disable(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("immediate",         immediate,         ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_alter_interface(subscription_name, interface_name, db, pg=None):
  """Modify an interface to a subscription."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.sub_disable(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("interface_name", interface_name, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_enable_interface():
  """Make an interface live."""
  util.exit_message("Not implemented yet.")


def sub_disable_interface():
  """Put an interface on the back burner."""
  util.exit_message("Not implemented yet.")


def sub_show_status(subscription_name, db, pg=None):
  """Display the status of the subcription."""

  pg_v = util.get_pg_v(pg)

  sql = "SELECT spock.sub_show_status(" 
  if subscription_name != "*":
    sql = sql + get_eq("subscription_name", subscription_name, "")
  sql = sql + ")"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_show_table(subscription_name, relation, db, pg=None):
  """Show subscription tables."""

  pg_v = util.get_pg_v(pg)

  sql = "SELECT spock.sub_show_table(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           "relation := '" + relation + "'::regclass)"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_sync():
  """Synchronize a subscription."""
  util.exit_message("Not implemented yet.")


def sub_resync_table(subscription_name, relation, db, truncate=False, pg=None):
  """Resynchronize a table."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.sub_resync_table(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("relation", relation, ", ") + \
           get_eq("truncate", truncate, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_add_repset(subscription_name, replication_set, db, pg=None):
  """Add a replication set to a subscription."""

  pg_v = util.get_pg_v(pg)

  sql = "SELECT spock.sub_add_repset(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("replication_set",   replication_set,   ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_remove_repset(subscription_name, replication_set, db, pg=None):
  """Drop a replication set from a subscription."""

  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.sub_remove_repset(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("replication_set",   replication_set,   ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def table_wait_for_sync(subscription_name, relation, db, pg=None):
  """Pause until a table finishes synchronizing."""
  sql = "SELECT spock.table_wait_for_sync(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("relation",   relation,   ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_sync():
  """Pause until a subscription is synchronized."""
  util.exit_message("Not implemented yet.")


def sub_wait_for_sync(subscription_name, db, pg=None):
  """Pause until the subscription is synchronized."""

  pg_v = util.get_pg_v(pg)

  sql = "SELECT spock.sub_wait_for_sync(" + \
           get_eq("subscription_name", subscription_name, ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def set_readonly(readonly="off", pg=None):
  """Turn PG read-only mode 'on' or 'off'."""

  if readonly not in ('on', 'off'):
    util.exit_message("  readonly flag must be 'off' or 'on'")

  pg_v = util.get_pg_v(pg)

  try:
    con = get_pg_connection(pg_v, "postgres",  util.get_user())
    cur = con.cursor(row_factory=psycopg.rows.dict_row)

    util.change_pgconf_keyval(pg_v, "default_transaction_read_only", readonly, True)

    util.message("reloading postgresql.conf")
    cur.execute("SELECT pg_reload_conf()")
    cur.close()
    con.close()

  except Exception as e:
    util.exit_exception(e)

  sys.exit(0)


def get_pii_cols(db,schema=None,pg=None):
  """Retrieve the columns that you have identified as PII"""

  pg_v = util.get_pg_v(pg)

  if schema == None:
    schema="public"
  sql = "SELECT pii_table, pii_column FROM spock.pii WHERE pii_schema='" + schema + "' ORDER BY pii_table;"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def get_table_list(table, db, pg_v):
  w_schema = None
  w_table = None

  l_tbl = table.split(".")
  if len(l_tbl) > 2:
    util.exit_message("Invalid table wildcard", 1)

  if len(l_tbl) == 2:
    w_schema = str(l_tbl[0])
    w_table = str(l_tbl[1])
  elif len(l_tbl) == 1:
    w_table = str(l_tbl[0])

  sql = "SELECT table_schema || '.' || table_name as schema_table \n" + \
        "  FROM information_schema.tables\n" + \
        " WHERE TABLE_TYPE = 'BASE TABLE'" 

  if w_schema:
    sql = sql + "\n   AND table_schema = '" + w_schema + "'"

  sql = sql + "\n   AND table_name LIKE '" + w_table.replace("*", "%") + "'"

  con = get_pg_connection(pg_v, db, util.get_user())

  try:
    cur = con.cursor()
    cur.execute(sql)

    ret = cur.fetchall()

    try:
      cur.close()
      con.close()
    except Exception as e:
      pass

  except Exception as e:
    util.exit_exception(e)

  if len(ret) > 0:
    return(ret)
  util.exit_message(f"Could not find table that matches {table}",1)


def repset_add_table(replication_set, table, db, synchronize_data=False, columns=None, row_filter=None, include_partitions=True, pg=None):
  """Add table(s) to replication set."""

  pg_v = util.get_pg_v(pg)
  tbls = get_table_list(table, db, pg_v)
  con = get_pg_connection(pg_v, db, util.get_user())

  for tbl in tbls:
    tab = str(tbl[0])
    sql="SELECT spock.repset_add_table(" + \
          get_eq("set_name",            replication_set,   ", ") + \
          get_eq("relation",            tab,               ", ") + \
          get_eq("synchronize_data",    synchronize_data,  ", ")
   
    if columns != None and len(tbls) == 1:
      sql = sql + get_eq("columns",','.join(columns), ", ", True)

    if row_filter != None and len(tbls) == 1:
      sql = sql + get_eq("row_filter",row_filter,        ", ")

    sql = sql + get_eq("include_partitions",  include_partitions,") ")
    util.message(f"Adding table {tab} to replication set {replication_set}.")

    try:
      con.transaction()
      cur = con.cursor()
      cur.execute(sql)
      con.commit()
    except Exception as e:
      util.print_exception(e, "warning")
      con.rollback()
    
  sys.exit(0)


def repset_remove_table(replication_set, table, db, pg=None):
  """Remove table from replication set."""
  pg_v = util.get_pg_v(pg)
  sql = "SELECT spock.repset_remove_table(" + \
           get_eq("set_name",   replication_set,   ", ") + \
           get_eq("relation",   table,             ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def health_check(pg=None):
  """Check if PG instance is accepting connections."""
  pg_v = util.get_pg_v(pg)

  if util.is_pg_ready(pg_v):
    util.exit_message("True", 0)

  util.exit_message("false", 0)

 
def metrics_check(db, pg=None):
  """Retrieve advanced DB & OS metrics."""
  try:
    import psutil
  except ImportError as e:
    util.exit_message("Missing or bad psutil module", 1)

  pg_v = util.get_pg_v(pg)
  usr = util.get_user()
  rc = util.is_pg_ready(pg_v)

  load1, load5, load15 = psutil.getloadavg()

  cpu_pct_lst = psutil.cpu_times_percent(interval=.3, percpu=False)
  cpu_pct = round(cpu_pct_lst.user + cpu_pct_lst.system, 1)
  if cpu_pct < 0.05:
    #test again after a little rest
    time.sleep(1)
    cpu_pct_lst = psutil.cpu_times_percent(interval=.3, percpu=False)
    cpu_pct = round(cpu_pct_lst.user + cpu_pct_lst.system, 1)

  disk = psutil.disk_io_counters(perdisk=False)
  disk_read_mb = round((disk.read_bytes / 1024 / 1024), 1)
  disk_write_mb = round((disk.write_bytes / 1024 / 1024), 1)

  disk_mount_pt = ""
  disk_size = ""
  disk_used = ""
  disk_avail = ""
  disk_used_pct = ""

  try:
    dfh = str(subprocess.check_output("df -h | grep '/data$'", shell=True)).split()
    if len(dfh) >= 5:
      disk_mount_pt = "/data"
      disk_size = str(dfh[1])
      disk_used  = str(dfh[2])
      disk_avail = str(dfh[3])
      disk_used_pct = float(util.remove_suffix("%", str(dfh[4])))
  except Exception as e:
    try:
      dfh = str(subprocess.check_output("df -h | grep '/$'", shell=True)).split()
      if len(dfh) >= 5:
        disk_mount_pt = "/"
        disk_size = str(dfh[1])
        disk_used  = str(dfh[2])
        disk_avail = str(dfh[3])
        disk_used_pct = float(util.remove_suffix("%", str(dfh[4])))
    except Exception as e:
      pass

  try:
    con = get_pg_connection(pg_v, db, usr)
    cur = con.cursor()
    cur.execute("SELECT setting FROM pg_settings WHERE name = 'default_transaction_read_only'")
    data = cur.fetchone()
    readonly = str(data[0])
    cur.close()
  except Exception as e:
    util.exit_exception(e)

  mtrc_dict = {"pg_isready": rc, "readonly": readonly, "cpu_pct": cpu_pct, \
               "load_avg": [load1, load5, load15], \
               "disk": {"read_mb": disk_read_mb, "write_mb": disk_write_mb, "size": disk_size,\
                        "used": disk_used, "available": disk_avail, "used_pct": disk_used_pct, \
                        "mount_point": disk_mount_pt} \
              }
  if rc == False:
    return(json_dumps(mtrc_dict))

  try:
    cur = con.cursor()
    cur.execute("SELECT count(*) as resolutions FROM spock.resolutions")
    data = cur.fetchone()
    rsltns = data[0]
    cur.close()
    mtrc_dict.update({"resolutions": rsltns})

    mtrc_dict.update({"slots": []})
    cur = con.cursor()
    sql_slots = "SELECT slot_name, commit_lsn, commit_timestamp, " + \
      "replication_lag, replication_lag_bytes " + \
      "FROM spock.lag_tracker ORDER BY slot_name"
    cur.execute(sql_slots)
    for row in cur:
      mtrc_dict["slots"].append({"slot_name":row[0],"commit_lsn":str(row[1]),"commit_timestamp":str(row[2]),"replication_lag":str(row[3]), "replication_lag_bytes":str(row[4])})
    cur.close()

  except Exception as e:
    pass

  return(json_dumps(mtrc_dict))


def db_create(db=None, User=None, Passwd=None, Id=None, pg=None):
  """
  Create a pg db with spock installed into it.


   Usage:
       To create a superuser than has access to the whole cluster of db's
          spock db-createdb -d <db> -U <usr> -P <passwd>

       to create an admin user that owns a specifc tennant database
          spock db-createdb -I <id>  [-P <passwd>]
      
  """

  if db == None:
    db = os.getenv('pgName', None)

  if User == None:
    User = os.getenv('pgeUser', None)

  ## one way or another, the user that creates the db will have a password
  if Passwd == None:
    Passwd = os.getenv('pgePasswd', None)
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
  rc1 = util.echo_cmd(ncb +  '"psql -q -c \\"' + cmd + '\\" postgres"')

  cmd = "createdb '" + db + "' --owner='" + User + "'"
  rc2 = util.echo_cmd(ncb  + '"' + cmd + '"')

  spock_comp = "spock31-pg" + str(pg)
  st8 = util.get_comp_state(spock_comp)
  if st8 in ("Installed", "Enabled"):
    cmd = "CREATE EXTENSION spock"
    rc3 = util.echo_cmd(ncb +  '"psql -q -c \\"' + cmd + '\\" ' + str(db) + '"')
  else:
    rc3 = util.echo_cmd(nc + "install " + spock_comp + " -d " + str(db))

  ##print(f" rcs = {rc1}, {rc2}, {rc3}")
  rcs = rc1 + rc2 + rc3
  if rcs == 0:
    status = "success"
  else:
    status = "error"

  return_json = {}
  return_json["status"] = status
  return_json["db_name"] = db 
  return_json["users"] = []

  user_json={}
  user_json["user"] = User
  user_json["passwd"] = Passwd
  return_json["users"].append(user_json)

  print(json_dumps(return_json))
  return


if __name__ == '__main__':
  fire.Fire({
      'node-create':         node_create,
      'node-drop':           node_drop,
      'node-alter-location': node_alter_location,
      'node-list':           node_list,
      'node-add-interface':  node_add_interface,
      'node-drop-interface': node_drop_interface,
      'repset-create':       repset_create,
      'repset-alter':        repset_alter,
      'repset-drop':         repset_drop,
      'repset-add-table':    repset_add_table,
      'repset-remove-table': repset_remove_table,
      'repset-add-seq':      repset_add_seq,
      'repset-remove-seq':   repset_remove_seq,
      'repset-alter-seq':    repset_alter_seq,
      'repset-list-tables':  repset_list_tables,
      'sub-create':          sub_create,
      'sub-drop':            sub_drop,
      'sub-alter-interface': sub_alter_interface,
      'sub-enable':          sub_enable,
      'sub-disable':         sub_disable,
      'sub-add-repset':      sub_add_repset,
      'sub-remove-repset':   sub_remove_repset,
      'sub-show-status':     sub_show_status,
      'sub-show-table':      sub_show_table,
      'sub-sync':            sub_sync,
      'sub-resync-table':    sub_resync_table,
      'sub-wait-for-sync':   sub_wait_for_sync,
      'table-wait-for-sync': table_wait_for_sync,
      'health-check':        health_check,
      'metrics-check':       metrics_check,
      'set-readonly':        set_readonly,
      'db-create':           db_create
  })


#pglogical.replication_set_add_all_tables
#spock.repset_add_all_tables
 
#pglogical.replication_set_add_all_sequences
#spock.repset_add_all_seqs

#pglogical.synchronize_sequence
#spock.seq_synch
