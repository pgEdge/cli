
import sys, os, json, subprocess, time
import util, meta, api, fire

try:
  import psycopg
except ImportError as e:
  util.exit_message("Missing 'psycopg' module from pip", 1)


def json_dumps(p_input):
  if os.getenv("isJson", "") == "True":
    return(json.dumps(p_input))

  return(json.dumps(p_input, indent=2))


def get_pg_connection(pg_v, db, usr):
  dbp = util.get_column("port", pg_v)

  try:
    con = psycopg.connect(dbname=db, user=usr, host="localhost", port=dbp)
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


def create_node(node_name, dsn, db, pg=None):
  """Create a spock node."""

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.create_node(" + \
           get_eq("node_name", node_name, ", ") + \
           get_eq("dsn",       dsn,       ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def create_replication_set(set_name, db, replicate_insert=True, replicate_update=True, 
                           replicate_delete=True, replicate_truncate=True, pg=None):
  """Define a replication set."""

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.create_replication_set(" + \
           get_eq("set_name", set_name, ", ") + \
           get_eq("replicate_insert",   replicate_insert,   ", ") + \
           get_eq("replicate_update",   replicate_update,   ", ") + \
           get_eq("replicate_delete",   replicate_delete,   ", ") + \
           get_eq("replicate_truncate", replicate_truncate, ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def create_subscription(subscription_name, provider_dsn, db, replication_sets="{default,default_insert_only,ddl_sql}",
                        synchronize_structure=False, synchronize_data=False, 
                        forward_origins='{}', apply_delay=0, pg=None):
  """Create a subscription."""

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.create_subscription(" + \
           get_eq("subscription_name",     subscription_name,     ", ") + \
           get_eq("provider_dsn",          provider_dsn,          ", ") + \
           get_eq("replication_sets",      replication_sets,      ", ") + \
           get_eq("synchronize_structure", synchronize_structure, ", ") + \
           get_eq("synchronize_data",      synchronize_data,      ", ") + \
           get_eq("forward_origins",       forward_origins,       ", ") + \
           get_eq("apply_delay",           apply_delay,           ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def show_subscription_status(subscription_name, db, pg=None):
  """Display the status of the subcription."""

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.show_subscription_status(" 
  if subscription_name != "*":
    get_eq("subscription_name", subscription_name, "")
  sql = sql + ")"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def show_subscription_table(subscription_name, relation, db, pg=None):
  """ ???????? """

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.show_subscription_status(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           "relation := '" + relation + "'::regclass)"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def alter_subscription_add_replication_set(subscription_name, replication_set, db, pg=None):
  """Modify a subscription and add a replication set to it."""

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.alter_subscription_add_replication_set(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("replication_set",   replication_set,   ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def wait_for_subscription_sync_complete(subscription_name, db, pg=None):
  """Pause until the subscription is synchronized."""

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.wait_for_subscription_sync_complete(" + \
           get_eq("subscription_name", subscription_name, ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def get_pii_cols(db,schema=None,pg=None):
  """Retrieve the columns that you have identified as PII 
     (these will be excluded from replicating to other servers)."""

  pg_v = get_pg_v(pg)

  if schema == None:
    schema="public"
  sql = "SELECT pii_table, pii_column FROM spock.pii WHERE pii_schema='" + schema + "' ORDER BY pii_table;"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)

def get_replication_tables(db, schema=None,pg=None):
  """Show the replication tables."""
  pg_v = get_pg_v(pg)

  if schema == None:
    schema="public"
  sql = "SELECT col.table_name, ARRAY_AGG(col.column_name) FROM information_schema.columns col LEFT OUTER JOIN spock.pii on col.table_name=pii.pii_table and col.column_name=pii.pii_column WHERE pii.pii_column IS NULL and table_schema='" + schema + "' GROUP BY 1 ORDER BY 1;"

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


def replication_set_add_table(replication_set, table, db, cols=None, pg=None):
  """Add a table to a replication set."""

  pg_v = get_pg_v(pg)

  tbls = get_table_list(table, db, pg_v)
  
  for tbl in tbls:
    if cols == None:
      sql="SELECT spock.replication_set_add_table('" + replication_set + "','" + str(tbl[0]) + "')"
    else:
      sql="SELECT spock.replication_set_add_table('" + replication_set + "','" + str(tbl[0]) + "','" + cols +"')"

    run_psyco_sql(pg_v, db, sql)

  sys.exit(0)

def health_check(pg=None):
  """Check if the PG instance is accepting connections."""
  pg_v = get_pg_v(pg)

  if is_pg_ready(pg_v):
    util.exit_message("True", 0)

  util.exit_message("false", 0)

 
def is_pg_ready(pg_v):
  rc = os.system(os.getcwd() + "/" + pg_v + "/bin/pg_isready > /dev/null 2>&1")
  if rc == 0:
    return(True)

  return(False)


def metrics_check(db, pg=None):
  """Retrieve OS & DB metrics."""
  try:
    import psutil
  except ImportError as e:
    util.exit_message("Missing 'psutil' module from pip", 1)

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

  mtrc_dict = {"pg_isready": rc, "cpu_pct": cpu_pct, "load_avg": [load1, load5, load15], \
               "disk": {"read_mb": disk_read_mb, "write_mb": disk_write_mb, "size": disk_size,\
                        "used": disk_used, "available": disk_avail, "used_pct": disk_used_pct, \
                        "mount_point": disk_mount_pt} \
              }
  if rc == False:
    return(json_dumps(mtrc_dict))

  try:
    con = get_pg_connection(pg_v, db, usr)
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


if __name__ == '__main__':
  fire.Fire({
      'create-node': create_node,
      'create-replication-set': create_replication_set,
      'replication-set-add-table':replication_set_add_table,
      'get-replication-tables': get_replication_tables,
      'create-subscription': create_subscription,
      'show-subscription-status': show_subscription_status,
      'show-subscription-table': show_subscription_table,
      'alter-subscription-add-replication-set': alter_subscription_add_replication_set,
      'wait-for-subscription-sync-complete': wait_for_subscription_sync_complete,
      'get-pii-columns': get_pii_cols,
      'health-check':health_check,
      'metrics-check':metrics_check,
  })

