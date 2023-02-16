
import sys, os
import util, meta, fire

try:
  import psycopg
except ImportError as e:
  util.exit_message("Missing 'psycopg' module from pip", 1)


def create(cluster_name, num_nodes, User="lcusr", Passwd="lcpasswd", 
           db="lcdb", port1=6432, pg="15", base_dir="cluster"):
  """Create a local cluster that runs N instances of pgEdge each running PG on a different port."""

  cluster_dir = base_dir + os.sep + cluster_name

  try:
    num_nodes = int(num_nodes)
  except Exception as e:
    util.exit_message("num_nodes parameter is not an integer", 1)

  try:
    port1 = int(port1)
  except Exception as e:
    util.exit_message("port1 parameter is not an integer", 1)

  kount = meta.get_installed_count()
  if kount > 0:
    util.message("WARNING: No other components should be installed when using 'local-cluster create'")

  if num_nodes < 1:
    util.exit_messages("num-nodes must be >= 1", 1)

  usr = util.get_user()

  for n in range(port1, port1 + num_nodes):
    util.message("checking port " + str(n) + " availability")
    if util.is_socket_busy(n):
      util.exit_message("port not avaiable", 1)

  if os.path.exists(cluster_dir):
    util.exit_message("cluster already exists: " + str(cluster_dir), 1)

  util.message("# creating cluster dir: " + cluster_dir)
  os.system("mkdir -p " + cluster_dir)

  pg_v = "pg" + str(pg)

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

    nc = (node_dir + "/nc ")
    parms =  " -U " + str(User) + " -P " + str(Passwd) + " -d " + str(db) + " -p " + str(nd_port)
    rc = util.echo_cmd(nc + "install pgedge" + parms)
    if rc != 0:
      sys.exit(rc)

    pgbench_cmd = '"pgbench --initialize --scale=' + str(num_nodes) + ' ' + str(db) + '"'
    util.echo_cmd(nc + "pgbin " + str(pg) +  " " + pgbench_cmd)

    rep_set = 'pgbench-rep-set'
    dsn = "'host=localhost user=" + usr + "'"

    util.echo_cmd(nc + " spock create-node '" + node_nm + "' --dsn 'host=localhost user=replication' --db " + db)
    util.echo_cmd(nc + " spock create-replication-set " + rep_set + " --db " + db)
    util.echo_cmd(nc + " spock replication-set-add-table " + rep_set + " public.pgbench* --db " + db)

    nd_port = nd_port + 1


def destroy(cluster_name, base_dir="cluster"):
  """Stop each node of a local-cluster and then delete all of it."""

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

  command(cluster_name, "all", "stop", base_dir)

  util.echo_cmd("rm -rf " + cluster_dir, 1)


def command(cluster_name, node, cmd, base_dir="cluster"):
  """Run './nc' commands on one or 'all' nodes."""

  cluster_dir = base_dir + "/" + str(cluster_name)

  if not os.path.exists(cluster_dir):
    util.exit_message("cluster not found: " + cluster_dir, 1)

  if node != "all":
    rc = util.echo_cmd(cluster_dir + "/" + str(node) + "/nc " + str(cmd))
    return(rc)

  rc = 0
  nd=1
  node_dir = cluster_dir + "/n" + str(nd)

  while os.path.exists(node_dir):
    rc = util.echo_cmd(node_dir + "/nc " + str(cmd), 1)
    nd = nd + 1
    node_dir = cluster_dir + "/n" + str(nd)

  return(rc)


if __name__ == '__main__':
  fire.Fire({
    'create':create,
    'destroy':destroy,
    'command':command,
  })

