#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import sys, os, json, subprocess, time
import util, meta, api, fire

nc = "./nodectl "

isAutoStart   = str(os.getenv("isAutoStart",   "False"))
isDebug       = str(os.getenv("pgeDebug",      "0"))
  
## force use of PGPASSWORD from ~/.pgpass
os.environ["PGPASSWORD"] = ""

try:
  import psycopg
except ImportError as e:
  util.exit_message("Missing 'psycopg' module from pip", 1)


def error_exit(p_msg, p_rc=1):
    util.message("ERROR: " + p_msg)
    if isDebug == "0":
      os.system(nc + "remove pgedge")

    sys.exit(p_rc)


def osSys(cmd, sleepy=0, fatal_exit=True):
  isSilent = os.getenv('isSilent', 'False')
  if isSilent == "False":
    s_cmd = util.scrub_passwd(cmd)
    util.message('#')
    util.message('# ' + str(s_cmd))

  rc = os.system(cmd)
  if rc != 0 and fatal_exit:
    error_exit("FATAL ERROR running SPOCK", 1)

  if sleepy > 0:
    time.sleep(sleepy)

  return


def json_dumps(p_input):
  if os.getenv("isJson", "") == "True":
    return(json.dumps(p_input))

  return(json.dumps(p_input, indent=2))


def get_pg_connection(pg_v, db, usr):
  dbp = util.get_column("port", pg_v)

  try:
    con = psycopg.connect(dbname=db, user=usr, host="localhost", port=dbp, autocommit=False)
  except Exception as e:
    util.exit_exception(e)

  return(con)


def run_psyco_sql(pg_v, db, cmd, usr=None):
  if usr == None:
    usr = util.get_user()

  isVerbose = os.getenv('isVerbose', 'False')
  if isVerbose == 'True':
    util.message(cmd, "info")

  con = get_pg_connection(pg_v, db, usr)

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


def get_pg_v(pg):
  pg_v = str(pg)

  if pg_v.isdigit():
    pg_v = "pg" + str(pg_v)

  if pg_v == "None":
    k = 0
    pg_s = meta.get_installed_pg()

    for p in pg_s:
      k = k + 1

    if k == 1:
      pg_v = str(p[0])
    else:
      util.exit_message("must be one PG installed", 1)

  if not os.path.isdir(pg_v):
    util.exit_message(str(pg_v) + " not installed", 1)

  return(pg_v)


def change_pg_pwd(pwd_file, db="*", user="postgres", host="localhost", pg=None ):
  pg_v = get_pg_v(pg)
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


def get_eq(parm, val, sufx):
  colon_equal = str(parm) + " := '" + str(val) + "'" + str(sufx)

  return(colon_equal)


def validate(port=5432, pgV="pg15"):
  """Check pre-reqs for advanced commands."""
  util.message("#### Checking for Pre-Req's #########################")
  platf = util.get_platform()

  util.message("  Verify Linux or macOS")
  if platf != "Linux" and platf != "Darwin":
    error_exit("OS must be Linux or macOS")

  if platf == "Linux":
    util.message("  Verify Linux supported glibc version")
    if util.get_glibc_version() < "2.28":
      error_exit("Linux has unsupported (older) version of glibc")

  util.message("  Verify Python 3.6+")
  p3_minor_ver = util.get_python_minor_version()
  if p3_minor_ver < 6:
    error_exit("Python version must be greater than 3.6")

  util.message("  Verify non-root user")
  if util.is_admin():
    error_exit("You must install as non-root user with passwordless sudo privleges")

  data_dir = "data/" + pgV
  util.message("  Verify empty data directory '" + data_dir + "'")
  if os.path.exists(data_dir):
    dir = os.listdir(data_dir)
    if len(dir) != 0:
      error_exit("The '" + data_dir + "' directory is not empty")


def tune(component="pg15"):
  """Tune pgEdge components."""

  if not os.path.isdir(component):
    util.exit_message(f"{component} is not installed", 1)

  rc = os.system("./nodectl tune " + component)
  return(rc)


def node_add_interface(node_name, interface_name, dsn, db, pg=None):
  """Add a new node interface."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.node_add_interface(" + \
           get_eq("node_name", node_name, ", ") + \
           get_eq("interface_name", interface_name, ", ") + \
           get_eq("dsn", dsn, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def node_drop_interface(node_name, interface_name, db, pg=None):
  """Delete a node interface."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.node_drop_interface(" + \
           get_eq("node_name", node_name, ", ") + \
           get_eq("interface_name", interface_name, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def node_create(node_name, dsn, db, pg=None):
  """Define a node for spock."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.node_create(" + \
           get_eq("node_name", node_name, ", ") + \
           get_eq("dsn",       dsn,       ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def node_drop(node_name, db, pg=None):
  """Remove a spock node."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.node_drop(" + get_eq("node_name", node_name, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def node_alter_location(node_name, location, db, pg=None):
  """Set location details for spock node."""

  pg_v = get_pg_v(pg)

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
  pg_v = get_pg_v(pg)
  sql = """
SELECT node_id, node_name FROM spock.node ORDER BY node_name
"""
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_create(set_name, db, replicate_insert=True, replicate_update=True, 
                           replicate_delete=True, replicate_truncate=True, pg=None):
  """Define a replication set."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.repset_create(" + \
           get_eq("set_name", set_name, ", ") + \
           get_eq("replicate_insert",   replicate_insert,   ", ") + \
           get_eq("replicate_update",   replicate_update,   ", ") + \
           get_eq("replicate_delete",   replicate_delete,   ", ") + \
           get_eq("replicate_truncate", replicate_truncate, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_alter(set_name, replicate_insert=NULL, replicate_update=NULL, 
                 replicate_delete=NULL, replicate_truncate=NULL, db, pg=None):
  """Modify a replication set."""
  pg_v = get_pg_v(pg)
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
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.repset_drop(" + get_eq("set_name", set_name, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_add_seq(set_name, relation, synchronize_data=false, db, pg=None):
  """Add a sequence to a replication set."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.repset_add_seq(" + \
           get_eq("set_name", set_name, ", ") + \
           get_eq("relation", relation, ", ") + \
           get_eq("synchronize_data", synchronize_data, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_add_all_seqs(set_name, schema_names, synchronize_data=false, db, pg=None):
  """Add sequences to a replication set."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.repset_add_all_seqs(" + \
           get_eq("set_name", set_name, ", ") + \
           get_eq("schemas", schema_names, ", ") + \
           get_eq("synchronize_data", synchronize_data, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_remove_seq(set_name, relation, db, pg=None):
  """Remove a sequence from a replication set."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.repset_remove_seq(" + \
           get_eq("set_name", set_name, ", ") + \
           get_eq("relation", relation, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def repset_list_tables(schema, db, pg=None):
  """List tables in replication sets."""
  pg_v = get_pg_v(pg)

  sql =  "SELECT * FROM spock.tables"
  if (schema != "*"):
      sql = sql + " WHERE nspname='" + schema + "'"
  sql = sql + " ORDER BY set_name, nspname, relname;"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_create(subscription_name, provider_dsn, db, 
               replication_sets="{default,default_insert_only,ddl_sql}",
               synchronize_structure=False, synchronize_data=False, 
               forward_origins='{}', apply_delay=0, pg=None):
  """Create a subscription."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.sub_create(" + \
           get_eq("subscription_name",     subscription_name,     ", ") + \
           get_eq("provider_dsn",          provider_dsn,          ", ") + \
           get_eq("replication_sets",      replication_sets,      ", ") + \
           get_eq("synchronize_structure", synchronize_structure, ", ") + \
           get_eq("synchronize_data",      synchronize_data,      ", ") + \
           get_eq("forward_origins",       forward_origins,       ", ") + \
           get_eq("apply_delay",           apply_delay,           ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_drop(subscription_name, db, pg=None):
  """Delete a subscription."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.sub_drop(" + get_eq("subscription_name", subscription_name, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_enable(subscription_name, db, immediate=False, pg=None):
  """Make a subscription live."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.sub_enable(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("immediate",         immediate,         ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_disable(subscription_name, db, immediate=False, pg=None):
  """Put a subscription on hold and disconnect from provider."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.sub_disable(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("immediate",         immediate,         ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_alter_interface(subscription_name, interface_name, db, pg=None):
  """Modify an interface to a subscription."""
  pg_v = get_pg_v(pg)
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

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.sub_show_status(" 
  if subscription_name != "*":
    sql = sql + get_eq("subscription_name", subscription_name, "")
  sql = sql + ")"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_show_table(subscription_name, relation, db, pg=None):
  """Show subscription tables."""

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.sub_show_table(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           "relation := '" + relation + "'::regclass)"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_synch():
  """Synchronize a subscription."""
  util.exit_message("Not implemented yet.")


def sub_resync_table(subscription_name, relation, truncate=true, db, pg=None):
  """Resynchronize a table."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.sub_resync_table(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("relation", relation, ", ") + \
           get_eq("truncate", truncate, ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_add_repset(subscription_name, replication_set, db, pg=None):
  """Add a replication set to a subscription."""

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.sub_add_repset(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("replication_set",   replication_set,   ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_remove_repset(subscription_name, replication_set, db, pg=None):
  """Drop a replication set from a subscription."""

  pg_v = get_pg_v(pg)
  sql = "SELECT spock.sub_remove_repset(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("replication_set",   replication_set,   ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def table_wait_for_sync(subscription_name, relation regclass, db, pg=None):
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

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.sub_wait_for_sync(" + \
           get_eq("subscription_name", subscription_name, ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def set_readonly(readonly="off", pg=None):
  """Turn PG read-only mode 'on' or 'off'."""

  if readonly not in ('on', 'off'):
    util.exit_message("  readonly flag must be 'off' or 'on'")

  pg_v = get_pg_v(pg)

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

  pg_v = get_pg_v(pg)

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

  return([table])


def repset_add_table(replication_set, table, db, cols=None, pg=None):
  """Add table(s) to replication set."""

  pg_v = get_pg_v(pg)

  tbls = get_table_list(table, db, pg_v)

  con = get_pg_connection(pg_v, db, util.get_user())

  for tbl in tbls:
    tab = str(tbl[0])

    sql="SELECT spock.repset_add_table('" + replication_set + "','" + tab + "'"
    if cols:
      sql = sql + " ,'" + cols +"')"
    else:
      sql = sql + ")"

    util.message(f"Adding table {tab} to replication set {replication_set}.")

    try:
      con.transaction()
      cur = con.cursor()
      cur.execute(sql)
      con.commit()
    except Exception as e:
      util.print_exception(e)
      con.rollback()
    
  sys.exit(0)


def repset_remove_table(replication_set, table, db, pg=None):
  """Remove table from replication set."""
  pg_v = get_pg_v(pg)
  sql = "SELECT spock.repset_remove_table(" + \
           get_eq("replication_set",   replication_set,   ", ") + \
           get_eq("relation",          table,             ")")
  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def health_check(pg=None):
  """Check if PG instance is accepting connections."""
  pg_v = get_pg_v(pg)

  if is_pg_ready(pg_v):
    util.exit_message("True", 0)

  util.exit_message("false", 0)

 
def is_pg_ready(pg_v):
  rc = os.system(os.getcwd() + "/" + pg_v + "/bin/pg_isready -d postgres > /dev/null 2>&1")
  if rc == 0:
    return(True)

  return(False)


def metrics_check(db, pg=None):
  """Retrieve advanced DB & OS metrics."""
  try:
    import psutil
  except ImportError as e:
    util.exit_message("Missing or bad psutil module", 1)

  pg_v = get_pg_v(pg)
  usr = util.get_user()
  rc = is_pg_ready(pg_v)

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
    sql_slots = \
      "SELECT slot_name, to_char(pg_wal_lsn_diff(pg_current_wal_insert_lsn(), confirmed_flush_lsn), \n" + \
      "       '999G999G999G999G999') as confirmed_flush_replication_lag, reply_time, \n" + \
      "       now() - reply_time AS reply_replication_lag \n" + \
      "  FROM pg_replication_slots R \n" + \
      "LEFT OUTER JOIN pg_stat_replication S ON R.slot_name = S.application_name \n" + \
      "ORDER BY 1"
    cur.execute(sql_slots)
    for row in cur:
      mtrc_dict["slots"].append({"slotName":row[0],"flushReplicationLag":row[1],"replyTime":str(row[2]),"replicationLag":str(row[3])})
    cur.close()

  except Exception as e:
    pass

  return(json_dumps(mtrc_dict))


def install(User=None, Password=None, database=None, location=None, port=5432,
            pgV="pg15", autostart=True, with_patroni=False, with_cat=False, with_bouncer=False, 
            with_backrest=False, with_postgrest=False):
  """Install pgEdge components."""

  pgeUser = os.getenv('pgeUser', None)
  pgePasswd = os.getenv('pgePasswd', None)
  pgName = os.getenv('pgName', None)

  if (User or pgeUser) and (Password or pgePasswd) and (database or pgName):
    pass
  else:
    error_exit("The User, Password & database (-U -P -d) must all be specified")


  if not User and pgeUser:
    User = pgeUser
  else:
    User = str(User)

  if not Password and pgePasswd:
    Password = pgePasswd
  else:
    Password = str(Password)

  if not database and pgName:
    database = pgName

  if location:
    os.environ["pgeLocation"] =  str(location)

  try:
    pgePort = int(os.getenv('pgePort', '5432'))
  except Exception as e:
    error_exit("Port " + os.getenv('pgePort') + " is not an integer")
  if not port and pgePort != 5432:
    port = pgePort

  if util.get_platform() == "Darwin":
    ## not supporting autostart mode on osx yet
    autostart = False

  database = str(database)
  try:
    port = int(port)
  except Exception as e:
    error_exit("The port must be an integer")

  pgV = str(pgV)
  #print(f"pgN = {pgV[2:]} pg = {pgV[:2]}")
  if pgV[:2] != "pg":
    error_exit("pgV parm must start with 'pg'")
  try:
    pgN = int(pgV[2:])
  except Exception as e:
    error_exit("pgV parm must end with a two digit integer")

  if User:
    util.message("  Verify -U user & -P password...")

    usr_l = User.lower()
    if usr_l == "pgedge":
      error_exit("The user defined supersuser may not be called 'pgedge'")

    if usr_l == util.get_user():
      error_exit("The user-defined superuser may not be the same as the OS user")

    usr_len = len(usr_l)
    if (usr_len < 2) or (usr_len > 64):
      error_exit("The user-defined superuser must be >=1 and <= 64 in length")

    if str(usr_l[0]).isnumeric():
      error_exit("The user may not start with a numeric character")

  if Password:
    pwd_len = len(Password)
    if (pwd_len < 6) or (pwd_len > 128):
      error_exit("The password must be >= 6 and <= 128 in length")

    for pwd_char in Password:
      pwd_c = pwd_char.strip()
      if pwd_c in (",", "'", '"', "@", ""):
        error_exit("The password must not contain ',', \"'\", \", @, or a space")

  if util.is_socket_busy(port):
    error_exit("Port " + str(port) + " is busy")

  osSys(nc + "install " + pgV)

  if util.is_empty_writable_dir("/data") == 0:
    util.message("## symlink empty local data directory to empty /data ###")
    osSys("rm -rf data; ln -s /data data")

  if autostart:
    util.message("\n## init & config autostart  ###############")
    osSys(nc + "init " + pgV + " --svcuser=" + util.get_user())
    osSys(nc + "config " + pgV + " --autostart=on")
  else:
    osSys(nc + "init " + pgV)

  osSys(nc + "config " + pgV + " --port=" + str(port))

  osSys(nc + "start " + pgV)
  time.sleep(3)

  if User and Password:
    ncb = nc + 'pgbin ' + str(pgN) + ' '
    cmd = "CREATE ROLE " + User + " PASSWORD '" + Password + "' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN"
    osSys(ncb +  '"psql -c \\"' + cmd + '\\" postgres" > /dev/null')

    cmd = "createdb '" + database + "' --owner='" + User + "'"
    osSys(ncb  + '"' + cmd + '"')

  osSys(nc + "tune " + pgV, 3)

  osSys(nc + "install spock -d " + database, 2)
  ##osSys(nc + "install readonly", 2)

  if util.get_platform() == "Linux":
    util.change_pgconf_keyval(pgV, "cron.database_name", database, True)
    osSys(nc + "install cron -d " + database, 2)

  if os.getenv("withPOSTGREST", "False") == "True":
    with_postgrest = True
  if with_postgrest == True:
    osSys(nc + "install postgrest", fatal_exit=False)

  if os.getenv("withPATRONI", "False") == "True":
    with_patroni = True
  if with_patroni == True:
    osSys(nc + "install patroni", fatal_exit=False)

  if os.getenv("withCAT", "False") == "True":
    with_cat = True
  if with_cat  == True:
    osSys(nc + "install cat")

  if os.getenv("withBOUNCER", "False") == "True":
    with_bouncer = True
  if with_bouncer  == True:
    osSys(nc + "install bouncer", fatal_exit=False)

  if os.getenv("withBACKREST", "False") == "True":
    with_backrest = True
  if with_backrest == True:
    osSys(nc + "install backrest", fatal_exit=False)


if __name__ == '__main__':
  fire.Fire({
      'tune':                tune,
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
      'sub-sync':            sub_synch,
      'sub-resynch-table':   sub_resynch_table,
      'sub-wait-for-sync':   sub_wait_for_sync,
      'table-wait-for-sync': table_wait_for_sync,
      'health-check':        health_check,
      'metrics-check':       metrics_check,
      'set-readonly':        set_readonly,
  })


#pglogical.replication_set_add_all_tables
#spock.repset_add_all_tables
 
#pglogical.replication_set_add_all_sequences
#spock.repset_add_all_seqs

#pglogical.synchronize_sequence
#spock.seq_synch
