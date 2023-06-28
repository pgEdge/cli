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
  cluster_json["create_dt"] = datetime.date.today().isoformat()
  cluster_json["db_name"] = db
  cluster_json["db_user"] = db
  cluster_json["db_init_passwd"] = passwd
  cluster_json["os_user"] = usr
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
  cluster_dir = base_dir + os.sep + cluster_name

  try:
    with open(cluster_dir + os.sep  + cluster_name + ".json") as f:
      parsed_json = json.load(f)
  except Exception as e:
    util.exit_message("Unable to load JSON cluster def file", 1)
  db_name=parsed_json["db_name"]
  pg=parsed_json["pg_ver"]
  count=parsed_json["count"]
  db_user=parsed_json["db_user"]
  db_passwd=parsed_json["db_init_passwd"]
  os_user=parsed_json["os_user"]
  cert=parsed_json["ssh_key"]
  return db_name, pg, count, db_user, db_passwd, os_user, cert, parsed_json["nodes"]


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


def init_remote(cluster_name, num_nodes, pg=None, app=None, port1=6432, 
                 User="lcusr", Passwd="lcpasswd", db="lcdb"):
  """Coming Soon! Initialize a test cluster from json definition file of existing nodes."""


def create_local(cluster_name, num_nodes, pg=None, app=None, port1=6432, 
                 User="lcusr", Passwd="lcpasswd", db="lcdb"):
  """Create a localhost test cluster of N pgEdge nodes on different ports."""

  util.message("# verifying passwordless ssh...")
  if util.is_password_less_ssh():
    pass
  else:
    util.exit_message("try https://blog.pgedge.org/index.php/2023/04/07/passwordless-ssh-to-localhost/", 1)

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

  if pg == None:
    pg = os.getenv("pgN", None)
    if pg == None:
      pg = "15"

  create_local_json(cluster_name, db, num_nodes, User, Passwd, pg, port1)

  pg_v = "pg" + str(pg)

  nd_port = port1

  ssh_install_pgedge(cluster_name, Passwd)

  if app == "pgbench":
    pgbench.install(cluster_name)


def ssh_install_pgedge(cluster_name, passwd):
  db, pg, count, db_user, db_passwd, os_user, cert, nodes = load_json(cluster_name)
  util.message("#")
  util.message(f"# ssh_install_pgedge: cluster={cluster_name}, db={db}, pg={pg} db_user={db_user}, count={count}")
  for n in nodes:
    ndnm = n["nodename"]
    ndpath = n["path"]
    ndip = n["ip"]
    ndport = n["port"]
    util.message(f"#   node={ndnm}, host={ndip}, port={ndport}, path={ndpath}")

    util.echo_cmd("mkdir " + ndpath, host=ndip)

    remote = ndip + ":" + ndpath
    util.echo_cmd("scp -pqr conf " + remote + "/.")
    util.echo_cmd("scp -pqr hub  " + remote + "/.")
    util.echo_cmd("scp -pq  nodectl " + remote + "/.")
    util.echo_cmd("scp -pq  nc      " + remote + "/.")

    nc = (ndpath + "/nodectl ")
    parms =  " -U " + str(db_user) + " -P " + str(passwd) + " -d " + str(db) + \
             " -p " + str(ndport) + " --pg " + str(pg)
    rc = util.echo_cmd(nc + " install pgedge" + parms, host=ndip)
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
    'create-local':   create_local,
    'init-remote':    init_remote,
    'destroy':        destroy,
    'validate':       validate,
    'command':        command,
    'app-install':    app_install,
    'app-remove':     app_remove
  })
