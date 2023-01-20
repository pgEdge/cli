
import sys, os, json
import util, meta

try:
  import fire
except ImportError as e:
  util.exit_message("Missing 'fire' module from pip", 1)

try:
  import psycopg2
  from psycopg2.extras import RealDictCursor
except ImportError as e:
  util.exit_message("Missing 'psycopg2' module from pip", 1)
   

def echo_cmd(cmd, sleep_secs=0):
  isSilent = os.getenv('isSilent', 'False')
  if isSilent == "False":
    s_cmd = util.scrub_passwd(cmd)
    util.message("# " + str(s_cmd))

  rc = os.system(str(cmd))
  if rc == 0:
    if sleep_secs > 0:
      os.system("sleep " + str(sleep_secs))
    return(0)

  return(1)


def run_psyco_sql(pg_v, db, cmd, usr=None):
  if usr == None:
    usr = util.get_user()

  dbp = util.get_column("port", pg_v)

  isVerbose = os.getenv('isVerbose', 'False')
  if isVerbose == 'True':
    util.message(cmd, "info")

  try:
    ##con = psycopg2.connect(dbname=db, user=usr, host="localhost", port=dbp)
    con = psycopg2.connect(dbname=db, port=dbp)
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute(cmd)
    con.commit()

    print(json.dumps(cur.fetchall(), indent=2))

    try:
      cur.close()
      con.close()
    except Exception as e:
      pass

  except Exception as e:
    lines = str(e).splitlines()
    util.exit_message(str(lines[0]), 1)


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


def create_extension(db, pg=None):
  pg_v = get_pg_v(pg)

  sql = "CREATE EXTENSION SPOCK"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def create_node(node_name, dsn, db, pg=None):
  pg_v = get_pg_v(pg)

  sql = "SELECT spock.create_node(" + \
           get_eq("node_name", node_name, ", ") + \
           get_eq("dsn",       dsn,       ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def create_replication_set(set_name, db, replicate_insert=True, replicate_update=True, 
                           replicate_delete=True, replicate_truncate=True, pg=None):
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
  pg_v = get_pg_v(pg)

  sql = "SELECT spock.show_subscription_status(" 
  if subscription_name != "*":
    get_eq("subscription_name", subscription_name, "")
  sql = sql + ")"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def show_subscription_table(subscription_name, relation, db, pg=None):
  pg_v = get_pg_v(pg)

  sql = "SELECT spock.show_subscription_status(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           "relation := '" + relation + "'::regclass)"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def alter_subscription_add_replication_set(subscription_name, replication_set, db, pg=None):
  pg_v = get_pg_v(pg)

  sql = "SELECT spock.alter_subscription_add_replication_set(" + \
           get_eq("subscription_name", subscription_name, ", ") + \
           get_eq("replication_set",   replication_set,   ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def wait_for_subscription_sync_complete(subscription_name, db, pg=None):
  pg_v = get_pg_v(pg)

  sql = "SELECT spock.wait_for_subscription_sync_complete(" + \
           get_eq("subscription_name", subscription_name, ")")

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def get_pii_cols(db,schema=None,pg=None):
  pg_v = get_pg_v(pg)

  if schema == None:
    schema="public"
  sql = "SELECT pii_table, pii_column FROM spock.pii WHERE pii_schema='" + schema + "' ORDER BY pii_table;"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)

def get_replication_tables(db, schema=None,pg=None):
  pg_v = get_pg_v(pg)

  if schema == None:
    schema="public"
  sql = "SELECT col.table_name, ARRAY_AGG(col.column_name) FROM information_schema.columns col LEFT OUTER JOIN spock.pii on col.table_name=pii.pii_table and col.column_name=pii.pii_column WHERE pii.pii_column IS NULL and table_schema='" + schema + "' GROUP BY 1 ORDER BY 1;"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def replication_set_add_table(replication_set, table, db, cols=None, pg=None):
  pg_v = get_pg_v(pg)

  if cols == None:
    sql="SELECT spock.replication_set_add_table('" + replication_set + "','" + table + "')"
  else:
    sql="SELECT spock.replication_set_add_table('" + replication_set + "','" + table + "','" + cols +"')"

  run_psyco_sql(pg_v, db, sql)
  sys.exit(0)


def local_cluster_create(cluster_name, num_nodes=3, port1=6432, pg="15", base_dir="cluster"):
  cluster_dir = base_dir + os.sep + cluster_name

  kount = meta.get_installed_count()
  if kount > 0:
    util.exit_message("No other components can be installed when using local_cluster_create()", 1)

  if num_nodes < 1:
    util.exit_messages("num-nodes must be >= 1", 1)

  for n in range(port1, port1 + num_nodes):
    util.message("checking port " + str(n) + " availability")
    if util.is_socket_busy(n):
      util.exit_message("port not avaiable", 1)

  if os.path.exists(cluster_dir):
    util.exit_message("cluster already exists: " + str(cluster_dir), 1)

  util.message("# creating cluster dir: " + cluster_dir)
  os.system("mkdir -p " + cluster_dir)

  pg_v = "pg" + str(pg)

  repl_passwd="abc123"
  nd_port = port1
  for n in range(1, num_nodes+1):
    node_nm = "n" + str(n)
    node_dir = cluster_dir + os.sep + node_nm

    util.message("\n\n" + \
      "###############################################################\n" + \
      "# creating node dir: " + node_dir)
    os.system("mkdir " + node_dir)

    os.system("cp -r conf " + node_dir + "/.")
    os.system("cp -r hub  " + node_dir + "/.")
    os.system("cp nc "      + node_dir + "/.")

    db='postgres'

    nc = (node_dir + "/nc ")
    echo_cmd(nc + "install " + pg_v)
    echo_cmd(nc + "init " + pg_v + " --port " + str(nd_port))
    echo_cmd(nc + "start " + pg_v)
    echo_cmd(nc + "install spock -d " + db)

    pgbench_cmd = '"pgbench --initialize --scale=' + str(num_nodes) + ' postgres"'
    echo_cmd(nc + "pgbin " + str(pg) +  " " + pgbench_cmd)

    #replusr_cmd = '"createuser with superuser replication password ' + repl_passwd"'
    #echo_cmd(nc + "pgbin " + str(pg) +  " " + replusr_cmd)

    rep_set='pgbench-rep-set'

    echo_cmd(nc + " spock create-node '" + node_nm + "' --dsn 'host=localhost user=replication' --db " + db)
    echo_cmd(nc + " spock create-replication-set " + rep_set + " --db " + db)
    echo_cmd(nc + " spock replication-set-add-table " + rep_set + " pgbench_accounts --db " + db)
    echo_cmd(nc + " spock replication-set-add-table " + rep_set + " pgbench_branches --db " + db)
    echo_cmd(nc + " spock replication-set-add-table " + rep_set + " pgbench_tellers  --db " + db)

    nd_port = nd_port + 1


def local_cluster_destroy(cluster_name, base_dir="cluster"):
  if not os.path.exists(base_dir):
    util.exit_message("no cluster directory: " + str(base_dir), 1)

  if cluster_name == "all":
    kount = 0
    for it in os.scandir(base_dir):
      if it.is_dir():
        kount = kount + 1
        lc_destroy1(it.name, base_dir)
    
    if kount == 0:
      util.exit_message("no cluster(s) to delete", 1)

  else:
    lc_destroy1(cluster_name, base_dir)


def lc_destroy1(cluster_name, base_dir):
  cluster_dir = base_dir + "/" + str(cluster_name)
  if not os.path.exists(cluster_dir):
    util.exit_message("cluster not found: " + cluster_dir, 1)

  local_cluster_cmd(cluster_name, "all", "stop", base_dir)

  echo_cmd("rm -rf " + cluster_dir, 1)


def local_cluster_cmd(cluster_name, node, cmd, base_dir="cluster"):
  cluster_dir = base_dir + "/" + str(cluster_name)

  if node != "all":
    rc = echo_cmd(cluster_dir + "/" + str(node) + "/nc " + str(cmd))
    return(rc)

  rc = 0
  nd=1
  node_dir = cluster_dir + "/n" + str(nd)

  while os.path.exists(node_dir):
    rc = echo_cmd(node_dir + "/nc " + str(cmd), 1)
    nd = nd + 1
    node_dir = cluster_dir + "/n" + str(nd)

  return(rc)


def health_check(pg=None):
  pg_v = get_pg_v(pg)

  rc = os.system(os.getcwd() + "/" + pg_v + "/bin/pg_isready > /dev/null 2>&1")
  if rc == 0:
    util.exit_message("true", 0)

  util.exit_message("false", 0)


if __name__ == '__main__':
  fire.Fire({
      'health-check':health_check,
      'create-extension': create_extension,
      'create-node': create_node,
      'create-replication-set': create_replication_set,
      'create-subscription': create_subscription,
      'show-subscription-status': show_subscription_status,
      'show-subscription-table': show_subscription_table,
      'alter-subscription-add-replication-set': alter_subscription_add_replication_set,
      'wait-for-subscription-sync-complete': wait_for_subscription_sync_complete,
      'change-pg-pwd': change_pg_pwd,
      'get-pii-columns': get_pii_cols,
      'get-replication-tables': get_replication_tables,
      'replication-set-add-table':replication_set_add_table,
      'local-cluster-create':local_cluster_create,
      'local-cluster-destroy':local_cluster_destroy,
      'local-cluster-cmd':local_cluster_cmd,
  })

