#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, random, time, json, socket
import util, fire, meta, pgbench 



base_dir = "cluster"


def create_json(cluster_name, db, num_nodes, usr, pg, port1):
  cluster_dir = base_dir + os.sep + cluster_name
  text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")
  cluster_json = {}
  cluster_json["cluster"] = cluster_name
  cluster_json["dbname"] = db
  cluster_json["conntype"] = "local"
  cluster_json["user"] = usr
  cluster_json["pg"] = pg
  cluster_json["count"] = num_nodes
  cluster_json["cert"] = ""
  cluster_json["nodes"] = []
  for n in range(1, num_nodes+1):
    node_json={}
    node_json["nodename"]="n"+str(n)
    node_json["ip"]="localhost"
    node_json["port"]=port1
    node_json["path"]=cluster_name + os.sep + "n" + str(n)
    cluster_json["nodes"].append(node_json)
    port1=port1+1
  try:
    text_file.write(json.dumps(cluster_json, indent=2))
    text_file.close()
  except: 
     util.exit_message("Unable to create JSON file", 1)


def load_json(cluster_name):
  cluster_dir = base_dir + os.sep + cluster_name

  try:
    with open(cluster_dir + os.sep  + cluster_name + ".json") as f:
      parsed_json = json.load(f)
  except Exception as e:
    util.exit_message("Unable to load JSON file", 1)
  db=parsed_json["dbname"]
  pg=parsed_json["pg"]
  count=parsed_json["count"]
  user=parsed_json["user"]
  cert=parsed_json["cert"]
  return db, pg, count, user, cert, parsed_json["nodes"]


def runNC(node, nc_cmd, db, user, cert):
  import paramiko

  if not (os.path.exists(cert)):
    util.exit_message("Unable to locate cert file", 1)

  ## Set up ssh connection
  pk = paramiko.RSAKey.from_private_key_file(cert)
  client = paramiko.SSHClient()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

  nc_message=[]
  for n in node:
    cmd=n["path"] + "nc " + nc_cmd
    # Execute Command
    try:
      client.connect(hostname=n["ip"], username=user, pkey=pk, timeout=3)
      stdin, stdout, stderr = client.exec_command(cmd)
      output =  stdout.read()
      ##print(output.decode('utf-8'), end="\n")
      client.close()
      nc_message.append(n["nodename"] + ": \n"  + output.decode('utf-8'))
    except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
        paramiko.SSHException, socket.error) as e:
        nc_message.append(n["nodename"] + ": \n SSH is not working correctly " + repr(e))

  return nc_message


def diff_tables(cluster_name, node1, node2, table_name):
  """Compare table on different cluster nodes"""

  if not os.path.isdir("pgdiff"):
    util.message("Installing the required 'pgdiff' component.")
    os.system("./nodectl install pgdiff")

  check_cluster_exists(cluster_name)

  if node1 == node2:
    util.exit_message("node1 must be different than node2")

  check_node_exists(cluster_name, node1)
  check_node_exists(cluster_name, node2)
    

def remove(rm_data=False):
  """Remove pgEdge components"""
  pass


def create_local(cluster_name, num_nodes, User="lcusr", Passwd="lcpasswd", 
           db="lcdb", port1=6432, pg="15", app=None):
  """Create local cluster of N pgEdge nodes on different ports."""

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
    util.message("WARNING: No other components should be installed when using 'cluster local'")

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
    os.system("cp nodectl " + node_dir + "/.")
    os.system("cp nc      " + node_dir + "/.")

    nc = (node_dir + "/nodectl ")
    parms =  " -U " + str(User) + " -P " + str(Passwd) + " -d " + str(db) + " -p " + str(nd_port)
    rc = util.echo_cmd(nc + "install pgedge" + parms)
    if rc != 0:
      sys.exit(rc)

    if app == "pgbench":
      pgbench.setup_node(node_nm, nc, num_nodes, db, pg, usr)

    nd_port = nd_port + 1

  create_json(cluster_name, db, num_nodes, usr, pg, port1)


def validate(cluster_name):
  """Validate a cluster configuration"""
  db, pg, count, user, cert, nodes = load_json(cluster_name)
  message = runNC(nodes, "info", db, user, cert)
  if len(message) == len(nodes):
    for n in message:
      if "NodeCtl" not in n:
          util.exit_message("Validation of the cluster failed for " + n[:2], 1)
  else:
    util.exit_message("Validation of the cluster failed", 1)
  return cluster_name + " Cluster Validated Sucessfully!"


def init(cluster_name):
  """Initialize cluster for Spock"""
  util.exit_message("Coming Soon!")


def destroy(cluster_name):
  """Stop and then nuke a cluster"""

  if not os.path.exists(base_dir):
    util.exit_message("no cluster directory: " + str(base_dir), 1)

  if cluster_name == "all":
    kount = 0
    for it in os.scandir(base_dir):
      if it.is_dir():
        kount = kount + 1
        lc_destroy1(it.name)
    
    if kount == 0:
      util.exit_message("no cluster(s) to delete", 1)

  else:
    lc_destroy1(cluster_name)


def lc_destroy1(cluster_name):
  cluster_dir = base_dir + "/" + str(cluster_name)

  command(cluster_name, "all", "stop")

  util.echo_cmd("rm -rf " + cluster_dir, 1)


def check_node_exists(cluster_name, node_name):
  node_dir = base_dir + "/" + str(cluster_name) + "/" + str(node_name)

  if not os.path.exists(node_dir):
    util.exit_message("node not found: " + node_dir, 1)


def check_cluster_exists(cluster_name):
  cluster_dir = base_dir + "/" + str(cluster_name)

  if not os.path.exists(cluster_dir):
    util.exit_message("cluster not found: " + cluster_dir, 1)


def command(cluster_name, node, cmd):
  """Run './nodectl' commands on one or 'all' nodes."""

  check_cluster_exists(cluster_name)

  cluster_dir = base_dir + "/" + str(cluster_name)

  if node != "all":
    rc = util.echo_cmd(cluster_dir + "/" + str(node) + "/nodectl " + str(cmd))
    return(rc)

  rc = 0
  nd=1
  node_dir = cluster_dir + "/n" + str(nd)

  while os.path.exists(node_dir):
    rc = util.echo_cmd(node_dir + "/nodectl " + str(cmd), 1)
    nd = nd + 1
    node_dir = cluster_dir + "/n" + str(nd)

  return(rc)


def app_install(cluster_name, app_name):
  """Install test application [ pgbench | spockbench | bmsql ]"""   

  if app_name ==  "pgbench":
    pgbench.setup_cluster(cluster_name)
  else:
    util.exit_message("Invalid application name.")


def app_remove(cluster_name, app_name):
  """Remove test application from cluster"""

  util.exit_message("Coming Soon", 1)
 

if __name__ == '__main__':
  fire.Fire({
    'create-local':   create_local,
    'destroy':        destroy,
    'validate':       validate,
    'init':           init,
    'command':        command,
    'diff-tables':    diff_tables,
    'app-install':    app_install,
    'app-remove':     app_remove
  })
