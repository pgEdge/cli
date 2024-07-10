
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os, json, datetime, meta, time
import util, fire, cluster

BASE_DIR = "cluster"


def create_local_json(cluster_name, db, num_nodes, usr, passwd, pg, ports, auto_ddl, hosts=None, paths=None, keys=None):
    """Create a json config file for a local cluster.
    
       Create a JSON configuration file that defines a local cluster. \n
       Example: localhost define demo lcdb 3 lcusr lcpasswd 16 5432
       :param cluster_name: The name of the cluster. A directory with this same name will be created in the cluster directory, and the JSON file will have the same name.
       :param db: The database name.
       :param num_nodes: The number of nodes in the cluster.
       :param usr: The username of the superuser created for this database.
       :param passwd: The password for the above user.
       :param pg: The postgres version of the database.
       :param ports: The starting port for this cluster. For local clusters, each node will have a port increasing by 1 from this port number. 
    """

    util.message(f"create_local_json({cluster_name}, {db}, {num_nodes}, {usr}, {passwd}, {pg}, {ports})", "debug")

    cluster_dir, cluster_file = cluster.get_cluster_info(cluster_name)
    ddl="off"
    if auto_ddl.lower() == "on":
        ddl="on"

    text_file = open(cluster_dir + os.sep + cluster_name + ".json", "w")
    cluster_json = {}
    cluster_json["name"] = cluster_name
    cluster_json["style"] = "localhost"
    cluster_json["create_date"] = datetime.date.today().isoformat()

    local_json = {}
    local_json["os_user"] = util.get_user()
    local_json["ssh_key"] = ""
    cluster_json["localhost"] = local_json

    database_json = {"databases": []}
    database_json["pg_version"] = pg
    database_json["auto_ddl"] = ddl
    db_json = {}
    db_json["username"] = usr
    db_json["password"] = passwd
    db_json["name"] = db
    database_json["databases"].append(db_json)
    cluster_json["database"] = database_json
    
    local_nodes = {"localhost": []}

    port1 = ports
    port_a = str(ports).split(",")
    if len(port_a) == num_nodes:
       pass
    else:
       if len(port_a) == 1:
          port1 = ports
       else:
          util.exit_message("ports param '{ports}' does NOT match num_nodes = {num_nodes}")

    for n in range(1, num_nodes + 1):
        node_array = {"nodes": []}
        node_json = {}
        node_json["name"] = "n" + str(n)
        node_json["is_active"] = True
        node_json["ip_address"] = "127.0.0.1"
        node_json["port"] = port1
        node_json["path"] = (
            os.getcwd()
            + os.sep
            + "cluster"
            + os.sep
            + cluster_name
            + os.sep
            + "n"
            + str(n)
        )
        node_array["nodes"].append(node_json)
        local_nodes["localhost"].append(node_array)
        port1 = port1 + 1

    cluster_json["node_groups"] = local_nodes

    try:
        text_file.write(json.dumps(cluster_json, indent=2))
        text_file.close()
    except Exception:
        util.exit_message("Unable to create JSON file", 1)


def remove(cluster_name):
    """Remove a cluster from json definition file of existing nodes.
    
       Remove a cluster. This will stop postgres on each node, and then remove the pgedge directory on each node.
       This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. \n 
       Example: localhost remove demo 
       :param cluster_name: The name of the cluster. 
    """
    db, db_settings, nodes = cluster.load_json(cluster_name)

    util.message("\n## Ensure that PG is stopped.")
    for nd in nodes:
        cmd = nd["path"] + os.sep + "pgedge stop 2> " + os.sep + "dev" + os.sep + "null"
        util.echo_cmd(cmd, host=nd["ip_address"], usr=nd["os_user"], key=nd["ssh_key"])

    util.message("\n## Ensure that pgEdge root directory is gone")
    for nd in nodes:
        cmd = f"rm -rf " + nd["path"] + os.sep + "pgedge"
        util.echo_cmd(cmd, host=nd["ip_address"], usr=nd["os_user"], key=nd["ssh_key"])


def cluster_create(
    cluster_name,
    num_nodes,
    pg="16",
    port1=6432,
    User="lcusr",
    Passwd="lcpasswd",
    db="lcdb",
    auto_ddl="off"
):
    """Create localhost cluster of N pgEdge nodes on different ports.
    
       Create a localhost cluster. Each node will be located in the cluster/<cluster_name>/<node_name> directory. Each database will have a different port. \n
       Example: localhost cluster-create demo 3 -U lcusr -P lcpasswd -d lcdb
       :param cluster_name: The name of the cluster. 
       :param num_nodes: The number of nodes in the cluster.
       :param usr: The username of the superuser created for this database.
       :param passwd: The password for the above user.
       :param pg: The postgreSQL version of the database.
       :param port1: The starting port for this cluster. For local clusters, each node will have a port increasing by 1 from this port number. 
       :param db: The database name.
       :param auto-ddl: Auto DDL on or off

Below is an example of the JSON file that is generated that defines a 2 node localhost cluster

{
  "name": "cl1",
  "style": "localhost",
  "create_date": "2024-02-23",
  "localhost": {
    "os_user": "rocky",
    "ssh_key": ""
  },
  "database": {
    "databases": [
      {
        "username": "lcusr",
        "password": "lcpasswd",
        "name": "lcdb"
      }
    ],
    "pg_version": "16",
    "auto_ddl": "off"
  },
  "node_groups": {
    "localhost": [
      {
        "nodes": [
          {
            "name": "n1",
            "is_active": true,
            "ip_address": "127.0.0.1",
            "port": 6432,
            "path": "/home/rocky/dev/cli/out/posix/cluster/cl1/n1"
          }
        ]
      },
      {
        "nodes": [
          {
            "name": "n2",
            "is_active": true,
            "ip_address": "127.0.0.1",
            "port": 6433,
            "path": "/home/rocky/dev/cli/out/posix/cluster/cl1/n2"
          }
        ]
      }
    ]
  }
    """

    util.message(f"localhost.cluster_create({cluster_name}, {num_nodes}, {pg}, {port1}, {User}, {Passwd}, {db})", "debug")

    util.message("# verifying passwordless ssh...")
    if util.is_password_less_ssh():
        pass
    else:
        util.exit_message("passwordless ssh not configured on localhost", 1)

    cluster_dir, cluster_file = cluster.get_cluster_info(cluster_name)

    try:
        num_nodes = int(num_nodes)
    except Exception:
        util.exit_message("num_nodes parameter is not an integer", 1)

    try:
        port1 = int(port1)
    except Exception:
        util.exit_message("port1 parameter is not an integer", 1)

    kount = meta.get_installed_count()
    if kount > 1:
        util.message(
            "WARNING: No other components should be installed when using 'cluster local'"
        )

    if num_nodes < 1:
        util.exit_message("num-nodes must be >= 1", 1)

    #  increment port1 to the first available port from it's initial value
    n = port1
    while util.is_socket_busy(n):
        util.message(f"# port {n} is busy")
        n = n + 1
    port1 = n

    util.message("# creating cluster dir: " + os.getcwd() + os.sep + cluster_dir)
    os.system("mkdir -p " + cluster_dir)

    pg = os.getenv("pgN", pg)
    db = os.getenv("pgName", db)
    User = os.getenv("pgeUser", User)
    Passwd = os.getenv("pgePasswd", Passwd)

    create_local_json(cluster_name, db, num_nodes, User, Passwd, pg, port1, auto_ddl)
    db, db_settings, nodes = cluster.load_json(cluster_name)

    cluster.ssh_install_pgedge(cluster_name, db[0]["name"], db_settings, db[0]["username"], db[0]["password"], nodes, True, " ", verbose=None)
    cluster.ssh_cross_wire_pgedge(cluster_name, db[0]["name"], db_settings, db[0]["username"], db[0]["password"], nodes, verbose=None)
    if len(db) > 1:
        for database in db[1:]:
            cluster.create_spock_db(nodes,database,db_settings)
            cluster.ssh_cross_wire_pgedge(cluster_name, database["name"], pg, database["username"], database["password"], nodes)        
    

def cluster_destroy(cluster_name):
    """Stop and then nuke a localhost cluster.
    
       Destroy a local cluster. This will stop postgres on each node, and then remove the pgedge directory for each node in a local cluster. \n
       Example: localhost cluster-destroy demo
       :param cluster_name: The name of the cluster. 
    """

    if not os.path.exists(BASE_DIR):
        util.exit_message("no cluster directory: " + str(BASE_DIR), 1)

    if cluster_name == "all":
        kount = 0
        for it in os.scandir(BASE_DIR):
            if it.is_dir():
                kount = kount + 1
                lc_destroy1(it.name)

        if kount == 0:
            util.exit_message("no cluster(s) to delete", 1)

    else:
        lc_destroy1(cluster_name)


def lc_destroy1(cluster_name):
    cluster_dir, cluster_file = cluster.get_cluster_info(cluster_name)

    cfg = cluster.get_cluster_json(cluster_name)

    if cfg:
        if "localhost" in cfg:
            cluster.command(cluster_name, "all", "stop")
        else:
            util.message(f"Cluster '{cluster_name}' is not a localhost cluster")

    util.echo_cmd("rm -rf " + cluster_dir)


if __name__ == "__main__":
    fire.Fire(
        {
            "cluster-create": cluster_create,
            "cluster-destroy": cluster_destroy,  
        }
    )
