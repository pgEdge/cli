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
    node_json["nodename"] = "n"+str(n)
    node_json["ip"] = "127.0.0.1"
    node_json["port"] = port1
    node_json["path"] = os.getcwd() + os.sep + "cluster" + os.sep + cluster_name + os.sep + "n" + str(n)
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


def remove(rm_data=False):
  pass


def create_cloud(cluster_name, locations, User, Passwd, db, cloud="aws", size="Medium", pg="16", app=None, port=5432):
  """Coming Soon!  Provision a secure global cluster in the Cloud using your own account."""

  util.exit_message("Coming Soon!!", 0)


def create_remote(cluster_name, num_nodes, pg=None, app=None, port1=6432, 
                 User="lcusr", Passwd="lcpasswd", db="lcdb"):
  """Comiing Soon! Create a remote SSH cluster from a cluster json definition file."""


def create_local(cluster_name, num_nodes, pg=None, app=None, port1=6432, 
                 User="lcusr", Passwd="lcpasswd", db="lcdb"):
  """Create a localhost test cluster of N pgEdge nodes on different ports."""

  util.message("# Verifying passwordless ssh...")
  if util.is_password_less_ssh():
    util.message("  passwordless ssh working")
  else:
    util.exit_message("  passwordless ssh not configured properly", 1)

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
      util.exit_message("port not available", 1)

  if os.path.exists(cluster_dir):
    util.exit_message("cluster already exists: " + str(cluster_dir), 1)

  util.message("# creating cluster dir: " + cluster_dir)
  os.system("mkdir -p " + cluster_dir)

  if pg == None:
    pg = os.getenv("pgN", None)
    if pg == None:
      pg = "15"

  create_json(cluster_name, db, num_nodes, usr, pg, port1)

  pg_v = "pg" + str(pg)

  nd_port = port1

  ssh_install_pgedge(cluster_name, Passwd, port1)

  #for n in range(1, num_nodes+1):
  #  node_nm = "n" + str(n)
  #  node_dir = os.getcwd() + os.sep + cluster_dir + os.sep + node_nm
#
  #  util.message("\n\n" + \
  #    "###############################################################\n" + \
  #    "# creating node dir: " + node_dir)
  #  util.echo_cmd("mkdir " + node_dir, host="localhost")
#
  #  remote_dir = "localhost:" + node_dir
  #  util.echo_cmd("scp -pqr conf " + remote_dir + "/.")
  #  util.echo_cmd("scp -pqr hub  " + remote_dir + "/.")
  #  util.echo_cmd("scp -pq  nodectl " + remote_dir + "/.")
  #  util.echo_cmd("scp -pq  nc      " + remote_dir + "/.")
#
  #  nc = (node_dir + "/nodectl ")
  #  parms =  " -U " + str(User) + " -P " + str(Passwd) + " -d " + str(db) + \
  #           " -p " + str(nd_port) + " --pg " + str(pg)
  #  rc = util.echo_cmd(nc + "install pgedge" + parms, host="localhost")
  #  if rc != 0:
  #    sys.exit(rc)
#
  #  nd_port = nd_port + 1

  if app == "pgbench":
    pgbench.install(cluster_name)


def ssh_install_pgedge(cluster_name, passwd, port1):
  db, pg, count, usr, cert, nodes = load_json(cluster_name)
  for n in nodes:
    node_nm = n["nodename"]
    node_dir = n["path"]
    node_ip = n["ip"]
    node_port = n["port"]

    util.message("\n\n" + \
      "###############################################################\n" + \
      "# creating node dir: " + node_dir)
    util.echo_cmd("mkdir " + node_dir, host=node_ip)

    remote_dir = node_ip + ":" + node_dir
    util.echo_cmd("scp -pqr conf " + remote_dir + "/.")
    util.echo_cmd("scp -pqr hub  " + remote_dir + "/.")
    util.echo_cmd("scp -pq  nodectl " + remote_dir + "/.")
    util.echo_cmd("scp -pq  nc      " + remote_dir + "/.")

    nc = (node_dir + "/nodectl ")
    parms =  " -U " + str(usr) + " -P " + str(passwd) + " -d " + str(db) + \
             " -p " + str(node_port) + " --pg " + str(pg)
    rc = util.echo_cmd(nc + "install pgedge" + parms, host=node_ip)


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
  return cluster_name + " Cluster Validated Successfully!"


def init(cluster_name):
  """Initialize cluster for Spock."""
  util.exit_message("Coming Soon!")


def destroy(cluster_name):
  """Stop and then nuke a cluster."""

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


def command(cluster_name, node, cmd, args=None):
  """Run './nodectl' commands on one or 'all' nodes."""

  util.check_cluster_exists(cluster_name)

  cluster_dir = base_dir + "/" + str(cluster_name)

  if node != "all":
    full_cmd = cluster_dir + "/" + str(node) + "/nodectl " + str(cmd)
    if args != None:
        full_cmd = full_cmd + " " + str(args)
    rc = util.echo_cmd(full_cmd)
    return(rc)

  rc = 0
  nd=1
  node_dir = cluster_dir + "/n" + str(nd)

  while os.path.exists(node_dir):
    full_cmd = node_dir + "/nodectl " + str(cmd)
    if args != None:
        full_cmd = full_cmd + " " + str(args)
    rc = util.echo_cmd(full_cmd, 1)
    nd = nd + 1
    node_dir = cluster_dir + "/n" + str(nd)

  return(rc)


def app_install(cluster_name, app_name):
  """Install test application [ pgbench | spockbench | bmsql ]."""   

  if app_name ==  "pgbench":
    pgbench.install(cluster_name)
  else:
    util.exit_message("Invalid application name.")


def app_remove(cluster_name, app_name):
  """Remove test application from cluster."""
  if app_name ==  "pgbench":
    pgbench.remove(cluster_name)
  else:
    util.exit_message("Invalid application name.")
 

if __name__ == '__main__':
  fire.Fire({
    'create-local':   create_local,
    'create-remote':  create_remote,
    'create-cloud':   create_cloud,
    'destroy':        destroy,
    'validate':       validate,
    'init':           init,
    'command':        command,
    'app-install':    app_install,
    'app-remove':     app_remove
  })
