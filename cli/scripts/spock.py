import sys, os, json, subprocess, time
import util, meta, api, fire

nc = "./nodectl "

isAutoStart   = str(os.getenv("isAutoStart",   "False"))
isDebug       = str(os.getenv("pgeDebug",      "0"))

try:
  import psycopg
except ImportError as e:
  util.exit_message("Missing 'psycopg' module from pip", 1)


def error_exit(p_msg, p_rc=1):
    util.message("ERROR: " + p_msg)
    if isDebug == "0":
      os.system(nc + "remove pgedge")

    sys.exit(p_rc)


def osSys(cmd, fatal_exit=True):
  isSilent = os.getenv('isSilent', 'False')
  if isSilent == "False":
    s_cmd = util.scrub_passwd(cmd)
    util.message('#')
    util.message('# ' + str(s_cmd))

  rc = os.system(cmd)
  if rc != 0 and fatal_exit:
    error_exit("FATAL ERROR running install-pgedge", 1)

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

  util.message("  Ensure recent pip3")
  rc = os.system("pip3 --version >/dev/null 2>&1")
  if rc == 0:
    os.system("pip3 install --upgrade pip --user")
  else:
    url="https://bootstrap.pypa.io/get-pip.py"
    if p3_minor_ver == 6:
      url="https://bootstrap.pypa.io/pip/3.6/get-pip.py"
    util.message("\n# Trying to install 'pip3'")
    osSys("rm -f get-pip.py", False)
    osSys("curl -O " + url, False)
    osSys("python3 get-pip.py --user", False)
    osSys("rm -f get-pip.py", False)

  util.message("  Verify non-root user")
  if util.is_admin():
    error_exit("You must install as non-root user with passwordless sudo privleges")

  data_dir = "data/" + pgV
  util.message("  Verify empty data directory '" + data_dir + "'")
  if os.path.exists(data_dir):
    dir = os.listdir(data_dir)
    if len(dir) != 0:
      error_exit("The '" + data_dir + "' directory is not empty")

  util.message("  Ensure PSYCOPG-BINARY pip3 module")
  try:
    import psycopg
  except ImportError as e:
    osSys("pip3 install psycopg-binary --user --upgrade", False)
    osSys("pip3 install psycopg        --user --upgrade", False)

  util.message("  Check for PSUTIL module")
  try:
    import psutil
  except ImportError as e:
    util.message("  You need a native PSUTIL module to run 'metrics-check' or 'top'")



def tune(component="pg15"):
  """Tune pgEdge components."""

  if not os.path.isdir(component):
    util.exit_message(f"{component} is not installed", 1)

  rc = os.system("./nodectl tune " + component)
  return(rc)


def node_add_interface():
  """Add a new node interafce."""
  util.exit_message("Not implemented yet.")


def node_drop_interface():
  """Delete a node interface."""
  util.exit_message("Not implemented yet.")


def node_create(node_name, dsn, db, pg=None):
  """Define a node for spock."""

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.node_create(" + \
           get_eq("node_name", node_name, ", ") + \
           get_eq("dsn",       dsn,       ")")

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


def repset_alter():
  """Modify a replication set."""
  util.exit_message("Not implemented yet.")


def repset_alter_seq():
  """Change a replication set sequence."""
  util.exit_message("Not implemented yet.")


def repset_drop():
  """Remove a replication set."""
  util.exit_message("Not implemented yet.")


def repset_add_seq():
  """Add a sequence to a replication set."""
  util.exit_message("Not implemented yet.")
  #pglogical.replication_set_add_sequence


def repset_add_all_seqs():
  """Add sequences to a replication set."""
  util.exit_message("Not implemented yet.")
  #pglogical.replication_set_add_all_sequences


def repset_remove_seq():
  """Remove a sequence from a replication set."""
  util.exit_message("Not implemented yet.")
  #pglogical.replication_set_remove_sequence


def sub_create(subscription_name, provider_dsn, db, replication_sets="{default,default_insert_only,ddl_sql}",
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


def sub_drop():
  """Delete a subscription."""
  util.exit_message("Not implemented yet.")


def sub_enable():
  """Make a subscription live."""
  util.exit_message("Not implemented yet.")


def sub_disable():
  """Put a subscription on hold."""
  util.exit_message("Not implemented yet.")


def sub_alter_interface():
  """Modify an interface to a subscription."""
  util.exit_message("Not implemented yet.")


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
    get_eq("subscription_name", subscription_name, "")
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


def sub_resynch_table():
  """Resynchronize a table."""
  util.exit_message("Not implemented yet.")


def sub_add_repset(subscription_name, replication_set, db, pg=None):
  """Add a replication set to a subscription."""

  pg_v = get_pg_v(pg)

  sql = "SELECT spock.sub_add_repset(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("replication_set",   replication_set,   ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def sub_remove_repset():
  """Drop a replication set from a subscription."""
  util.exit_message("Not implemented yet.")


def table_wait_for_sync():
  """Pause until a table finishes synchronizing."""
  util.exit_message("Not implemented yet.")


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
  """Add a table to a replication set."""

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


def repset_remove_table():
  """Coming Soon!"""
  util.exit_message("Not implemented yet.")


def health_check(pg=None):
  """Check if PG instance is accepting connections."""
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
  """Retrieve advanced DB & OS metrics."""
  try:
    import psutil
  except ImportError as e:
    util.exit_message("Missing native 'pyton3[9]-psutil' module", 1)

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


def install(User=None, Password=None, database=None, country=None, port=5432,
            pgV="pg15", autostart=True, with_bouncer=False, 
            with_backrest=False, with_postgrest=False):
  """Install pgEdge components."""

  pgeUser = os.getenv('pgeUser', None)
  if not User and pgeUser:
    User = pgeUser
  else:
    User = str(User)

  pgePasswd = os.getenv('pgePasswd', None)
  if not Password and pgePasswd:
    Password = pgePasswd
  else:
    Password = str(Password)

  pgName = os.getenv('pgName', None)
  if not database and pgName:
    database = pgName

  if country:
    os.environ["pgeCountry"] =  str(country)

  try:
    pgePort = int(os.getenv('pgePort', '5432'))
  except Exception as e:
    error_exit("Port " + os.getenv('pgePort') + " is not an integer")
  if not port and pgePort != 5432:
    port = pgePort

  if util.get_platform() == "Darwin":
    ## not supporting autostart mode on osx yet
    autostart = False

  ##print(f"User={User}, Password={Password}, database={database}, country={country}, port={port}")
  ##print(f"autostart={autostart}, with_bouncer={with_bouncer}")

  database = str(database)
  country = str(country)
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

  if User == None and Password == None:
    pass
  elif User and Password:
    pass
  else:
    error_exit("The User and Password must be specified as a pair")

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

  osSys(nc + "tune " + pgV)
  time.sleep(3)

  osSys(nc + "install spock -d " + database)
  time.sleep(2)

  if os.getenv("withPOSTGREST", "False") == "True":
    with_postgrest = True
  if with_postgrest == True:
    osSys(nc + "install postgrest")

  if os.getenv("withBOUNCER", "False") == "True":
    with_bouncer = True
  if with_bouncer  == True:
    osSys(nc + "install bouncer")

  if os.getenv("withBACKREST", "False") == "True":
    with_backrest = True
  if with_backrest == True:
    osSys(nc + "install backrest")


if __name__ == '__main__':
  fire.Fire({
      'install':             install,
      'validate':            validate,
      'tune':                tune,
      'node-create':         node_create,
      'node-add-interface':  node_add_interface,
      'node-drop-interface': node_drop_interface,
      'repset-create':       repset_create,
      'repset-alter':        repset_alter,
      'repset-drop':         repset_drop,
      'repset-add-table':    repset_add_table,
      'repset-add-seq':      repset_add_seq,
      'repset-remove-seq':   repset_remove_seq,
      'repset-alter-seq':    repset_alter_seq,
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
  })


#pglogical.replication_set_add_all_tables
#spock.repset_add_all_tables
 
#pglogical.replication_set_add_sequence
#spock.repset_add_seq

#pglogical.replication_set_add_all_sequences
#spock.repset_add_all_seqs

#pglogical.replication_set_remove_sequence
#spock.repset_remove_seq
 
#pglogical.synchronize_sequence
#spock.seq_synch
