#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, random, json, socket, datetime
import util, fire, meta, pgbench

base_dir = "cluster"


def create_local_json(cluster_name, db, num_nodes, usr, passwd, pg, port1):
  cluster_dir = base_dir + os.sep + cluster_name
  text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")
  cluster_json = {}
  cluster_json["cluster"] = cluster_name
  cluster_json["is_localhost"] = "True"
  cluster_json["create_dt"] = datetime.date.today().isoformat()
  cluster_json["db_name"] = db
  cluster_json["db_user"] = usr
  cluster_json["db_init_passwd"] = passwd
  cluster_json["os_user"] = util.get_user()
  cluster_json["ssh_key"] = ""
  cluster_json["pg_ver"] = pg
  cluster_json["count"] = num_nodes
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
  parsed_json = get_cluster_json(cluster_name)

  db_name=parsed_json["db_name"]
  pg=parsed_json["pg_ver"]
  count=parsed_json["count"]
  db_user=parsed_json["db_user"]
  db_passwd=parsed_json["db_init_passwd"]
  os_user=parsed_json["os_user"]
  ssh_key=parsed_json["ssh_key"]
  return db_name, pg, count, db_user, db_passwd, os_user, ssh_key, parsed_json["nodes"]


def runNC(node, nc_cmd, db, user, cert):
  import paramiko

  ## Set up ssh connection
  pk=None
  if cert and cert > "":
    if not (os.path.exists(cert)):
      util.exit_message("Unable to locate cert file", 1)
    pk = paramiko.RSAKey.from_private_key_file(cert)
  client = paramiko.SSHClient()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

  nc_message=[]
  for n in node:
    cmd=n["path"] + "nc " + nc_cmd
    # Execute Command
    try:
      if pk:
        client.connect(hostname=n["ip"], username=user, pkey=pk, timeout=3)
      else:
        client.connect(hostname=n["ip"], username=user, timeout=3)
      stdin, stdout, stderr = client.exec_command(cmd)
      output =  stdout.read()
      #print(output.decode('utf-8'), end="\n")
      client.close()
      nc_message.append(n["nodename"] + ": \n"  + output.decode('utf-8'))
    except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
        paramiko.SSHException, socket.error) as e:
        nc_message.append(n["nodename"] + ": \n SSH is not working correctly " + repr(e))

  return nc_message


def get_cluster_json(cluster_name):
  cluster_dir = base_dir + os.sep + cluster_name
  cluster_file = cluster_dir + os.sep + cluster_name + ".json"

  if not os.path.isdir(cluster_dir):
    util.exit_message(f"Cluster directory '{cluster_dir}' not found")

  if not os.path.isfile(cluster_file):
    util.exit_message(f"Cluster file '{cluster_file}' not found")

  parsed_json = None
  try:
    with open(cluster_file) as f:
      parsed_json = json.load(f)
  except Exception as e:
    util.exit_message(f"Unable to load cluster def file '{cluster_file}\n{e}")

  return(parsed_json)


def reset_remote(cluster_name):
  """Reset a test cluster from json definition file of existing nodes."""
  db, pg, count, user, db_passwd, os_user, key, nodes = load_json(cluster_name)

  util.message("\n## Ensure that PG is stopped.")
  for nd in nodes:
     cmd = nd["path"] + "/nodectl stop 2> /dev/null"
     util.echo_cmd(cmd, host=nd["ip"], usr=os_user, key=key)

  util.message(f"\n## Ensure that pgEdge root directory is gone")
  for nd in nodes:
     cmd = "rm -rf " + nd["path"]
     util.echo_cmd(cmd, host=nd["ip"], usr=os_user, key=key)


def init_remote(cluster_name, app=None):
  """Initialize a test cluster from json definition file of existing nodes."""

  util.message(f"## Loading cluster '{cluster_name}' json definition file")
  cj = get_cluster_json(cluster_name)

  util.message(f"\n## Checking node count")
  try:
    kount = cj["count"]
    nodes = cj["nodes"]
    if len(nodes) != kount:
      util.exit_message(f"Invalid node count '{kount}' versus actual nodes '{len(nodes)}'")
  except Exception as e:
    util.exit_message(f"error parsing config file\n{str(e)}")
  util.message(f"### Node count = {kount}")

  util.message(f"\n## Checking ssh'ing to each node")
  for nd in cj["nodes"]:
    rc = util.echo_cmd(usr=cj["os_user"], host=nd["ip"], key=cj["ssh_key"], cmd="hostname")
    if rc == 0:
      print("OK")
    else:
      util.exit_message("cannot ssh to node")

  ssh_install_pgedge(cluster_name, cj["db_init_passwd"])


def create_secure(cluster_name, locations="", pg=None, app=None, 
                 User="lcusr", Passwd="lcpasswd", db="lcdb"):
  """Coming Soon! Create a secure pgEdge cluster of N nodes."""
  util.exit_message("Coming Soon!")


def create_local(cluster_name, num_nodes, pg="16", app=None, port1=6432, 
                 User="lcusr", Passwd="lcpasswd", db="lcdb"):
  """Create a localhost test cluster of N pgEdge nodes on different ports."""

  util.message("# verifying passwordless ssh...")
  if util.is_password_less_ssh():
    pass
  else:
    util.exit_message("passwordless ssh not configured on localhost", 1)

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
    util.exit_message("num-nodes must be >= 1", 1)

  usr = util.get_user()

  for n in range(port1, port1 + num_nodes):
    util.message("# checking port " + str(n) + " availability...")
    if not util.is_socket_busy(n):
      break

  if os.path.exists(cluster_dir):
    util.exit_message("cluster already exists: " + str(cluster_dir), 1)

  util.message("# creating cluster dir: " + os.getcwd() + os.sep + cluster_dir)
  os.system("mkdir -p " + cluster_dir)

  pg = os.getenv("pgN", pg)
  db = os.getenv('pgName', db)
  User = os.getenv('pgeUser', User)
  Passwd = os.getenv('pgePasswd', Passwd)

  create_local_json(cluster_name, db, num_nodes, User, Passwd, pg, port1)

  pg_v = "pg" + str(pg)

  nd_port = port1

  ssh_install_pgedge(cluster_name, Passwd)

  if app == "pgbench":
    pgbench.install(cluster_name)


def ssh_install_pgedge(cluster_name, passwd):
  db, pg, count, db_user, db_passwd, os_user, ssh_key, nodes = load_json(cluster_name)
  util.message("#")
  util.message(f"# ssh_install_pgedge: cluster={cluster_name}, db={db}, pg={pg} db_user={db_user}, count={count}")
  for n in nodes:
    ndnm = n["nodename"]
    ndpath = n["path"]
    ndip = n["ip"]
    ndport = n["port"]
    util.message(f"#   node={ndnm}, host={ndip}, port={ndport}, path={ndpath}")

    cmd1 = f"mkdir -p {ndpath}; cd {ndpath}; unset REPO; "
    cmd2 = "python3 -c \"\$(curl -fsSL https://pgedge-download.s3.amazonaws.com/REPO/install.py)\""
    util.echo_cmd(cmd1 + cmd2, host=n["ip"], usr=os_user, key=ssh_key)
    
    nc = (ndpath + "/pgedge/nodectl ")
    parms =  " -U " + str(db_user) + " -P " + str(passwd) + " -d " + str(db) + \
             " -p " + str(ndport) + " --pg " + str(pg)
    rc = util.echo_cmd(nc + " install pgedge" + parms, host=n["ip"], usr=os_user, key=ssh_key)
    util.message("#")


def validate(cluster_name):
  """Validate a cluster configuration"""
  db, pg, count, user, db_passwd, os_user, cert, nodes = load_json(cluster_name)
  message = runNC(nodes, "info", db, user, cert)
  if len(message) == len(nodes):
    for n in message:
      if "NodeCtl" not in n:
          util.exit_message("Validation of the cluster failed for " + n[:2], 1)
  else:
    util.exit_message("Validation of the cluster failed", 1)
  return cluster_name + " Cluster Validated Successfully!"


def destroy_local(cluster_name):
  """Stop and then nuke a localhost cluster."""

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

  cfg = get_cluster_json(cluster_name)

  try:
    is_localhost = cfg["is_localhost"]
  except Exception as e:
    is_localhost = "False"

  if is_localhost == "True":
    command(cluster_name, "all", "stop")
    util.echo_cmd("rm -rf " + cluster_dir)
  else:
    util.message(f"Cluster '{cluster_name}' is not a localhost cluster")


def command(cluster_name, node, cmd, args=None):
  """Run './nodectl' commands on one or 'all' nodes."""

  util.check_cluster_exists(cluster_name)

  cluster_dir = base_dir + "/" + str(cluster_name)

  if node != "all":
    full_cmd = cluster_dir + "/" + str(node) + "/pgedge/nodectl " + str(cmd)
    if args != None:
        full_cmd = full_cmd + " " + str(args)
    rc = util.echo_cmd(full_cmd)
    return(rc)

  rc = 0
  nd=1
  node_dir = cluster_dir + "/n" + str(nd)

  while os.path.exists(node_dir):
    full_cmd = node_dir + "/pgedge/nodectl " + str(cmd)
    if args != None:
        full_cmd = full_cmd + " " + str(args)
    rc = util.echo_cmd(full_cmd, 1)
    nd = nd + 1
    node_dir = cluster_dir + "/n" + str(nd)

  return(rc)


def app_install(cluster_name, app_name, factor=1):
  """Install test application [ pgbench | spockbench | bmsql ]."""   

  if app_name ==  "pgbench":
    pgbench.install(cluster_name, factor)
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
    'create-secure':  create_secure,
    'create-local':   create_local,
    'destroy-local':  destroy_local,
    'init-remote':    init_remote,
    'reset-remote':   reset_remote,
    'validate':       validate,
    'command':        command,
    'app-install':    app_install,
    'app-remove':     app_remove
  })
