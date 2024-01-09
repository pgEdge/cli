#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

import os, json
import util, fire, requests
import cluster, configparser

cluster_dir = "cluster"
home_dir = os.getenv("HOME")


def get_access_token(profile="Default", client_id=None, client_secret=None):
    # Use pgEdge Cloud API to get access token
    access_token = None
    auth_json = {}
    if client_id is None:
        config = configparser.ConfigParser()
        config.read(f"{home_dir}{os.sep}.pgedge{os.sep}config")
        client_id = config[profile.upper()]["client_id"]
        client_secret = config[profile.upper()]["client_secret"]
    auth_json["client_id"] = client_id
    auth_json["client_secret"] = client_secret
    try:
        url = "https://api.pgedge.com/oauth/token"
        response = requests.post(url, json=auth_json)
        if str(response.status_code) == "200":
            access_token = response.json()["access_token"]
        else:
            util.exit_message("Unable to get token")
    except Exception:
        util.exit_message("Unable to get token")
    return access_token


def get_pgedge(cmd, profile="Default"):
    # Call GET to pgEdge API
    access = get_access_token(profile)
    url = "https://api.pgedge.com/" + cmd
    header = {}
    header["Authorization"] = "Bearer " + access
    response = requests.get(url, headers=header)
    if str(response.status_code) == "200":
        return response.json()
    else:
        util.exit_message(f"Unable to run get - {cmd}", 1)


def post_pgedge(cmd, data, profile="Default"):
    # Call POST to pgEdge API
    access = get_access_token(profile)
    url = "https://api.pgedge.com/" + cmd
    header = {}
    header["Authorization"] = "Bearer " + access
    response = requests.post(url, headers=header, json=data)
    if str(response.status_code) == "200":
        return response.json()
    else:
        util.exit_message(f"Unable to run post - {cmd}", 1)


def delete_pgedge(cmd, profile="Default"):
    # Call DELETE to pgEdge API
    access = get_access_token(profile)
    url = "https://api.pgedge.com/" + cmd
    header = {}
    header["Authorization"] = "Bearer " + access
    response = requests.delete(url, headers=header)
    if str(response.status_code) == "200":
        return response.json()
    else:
        util.exit_message(f"Unable to run delete - {cmd}", 1)


def config(client_id, client_secret, profile="Default"):
    """Connect nodeCtl with a pgEdge Cloud Account

    Connect NodeCtl with a pgEdge Cloud Account
    [ Requires creating an API client in pgEdge Cloud Account ]
      CLIENT_ID - Auth ID from created API client
      CLIENT_SECRET - Auth Secret from created API client
      PROFILE - profile for NodeCTL to use with this pgEdge Cloud Account
    """
    try:
        # Create Creds File
        os.system(f"mkdir -p {home_dir}{os.sep}.pgedge")
        config = configparser.ConfigParser()
        config["DEFAULT"] = {"client_id": client_id, "client_secret": client_secret}
        with open(f"{home_dir}{os.sep}.pgedge{os.sep}config", "w") as configfile:
            config.write(configfile)
        get_access_token(profile, client_id, client_secret)
    except Exception:
        util.exit_message("Unable to create creds file", 1)
    util.exit_message(f"Configured nodeCtl Secure with profile {profile}", 0)


def list_cloud_acct(profile="Default"):
    """List all cloud account ids in a pgEdge Cloud Account

    List all cloud account ids in a pgEdge Cloud Account
    [ Requires ./ctl secure config ]
      PROFILE - profile name of pgEdge Cloud Account for NodeCTL to use
    """
    response = get_pgedge("cloud-accounts", profile)
    print(util.json_dumps(response))


def list_clusters(profile="Default"):
    """List all clusters in a pgEdge Cloud Account

    List all clusters in a pgEdge Cloud Account
    [ Requires ./ctl secure config ]
      PROFILE - profile name of pgEdge Cloud Account for NodeCTL to use
    """
    response = get_pgedge("clusters", profile)
    print(util.json_dumps(response))


def cluster_status(cluster_id, profile="Default"):
    """Return info on a cluster in a pgEdge Cloud Account

    Returns cluster status in a pgEdge Cloud Account
    [ Requires ./ctl secure config ]
      CLUSTER_ID - the pgEdge Cloud Cluster ID
      PROFILE - profile name of pgEdge Cloud Account for NodeCTL to use
    """
    response = get_pgedge(f"clusters/{cluster_id}", profile)
    cluster_name = response["name"]
    status = response["status"]
    util.exit_message(f"Cluster {cluster_name} has status: {status}", 0)


def list_nodes(cluster_id, profile="Default"):
    """List all nodes in a pgEdge Cloud Account cluster

    List all nodes in a cluster in a pgEdge Cloud Account
    [ Requires ./ctl secure config ]
      CLUSTER_ID - the pgEdge Cloud Cluster ID
      PROFILE - profile name of pgEdge Cloud Account for NodeCTL to use
    """
    response = get_pgedge(f"clusters/{cluster_id}/nodes", profile)
    print(util.json_dumps(response))


def import_cluster_def(cluster_id, profile="Default"):
    """Enable nodeCtl cluster commands on a pgEdge Cloud Cluster

    Import information on a pgEdge Cloud Cluster into a json file for ./ctl cluster
    [ Requires ./ctl secure config ]
      CLUSTER_ID - the pgEdge Cloud Cluster ID
      PROFILE - profile name of pgEdge Cloud Account for NodeCTL to use
    [ Requires ssh connection to then use ./ctl cluster commands ]
    """
    cluster_def = get_pgedge(f"clusters/{cluster_id}", profile)
    cluster_name = cluster_def["name"].lower()
    id = cluster_def["id"]
    db = cluster_def["database"]["name"]
    usr = "pgedge"
    passwd = ""
    pg = cluster_def["database"]["pg_version"]
    create_dt = cluster_def["created_at"]
    n = 0
    nodes = []
    node_def = get_pgedge(f"clusters/{cluster_id}/nodes", profile)
    for node in node_def:
        node_json = {}
        n = n + 1
        node_json["name"] = node["name"]
        node_json["id"] = node["id"]
        node_json["path"] = "/opt/pgedge"
        node_json["port"] = "5432"
        node_json["ip"] = node["public_ip_address"]
        nodes.append(node_json)
    cluster.create_remote_json(
        cluster_name, db, n, usr, passwd, pg, create_dt, id, nodes
    )
    util.exit_message("Cluster info json file created", 0)


def get_cluster_id(cluster_name):
    """Return the cluster id based on a cluster display name

    Return the cluster id based on a cluster display name
    [ Requires ./ctl secure import-cluster-def ]
      CLUSTER_NAME - the display name of the pgEdge Cloud Cluster
    """
    try:
        with open(
            f"{cluster_dir}{os.sep}{cluster_name}{os.sep}{cluster_name}.json"
        ) as f:
            parsed_json = json.load(f)
            cluster_id = parsed_json["id"]
    except Exception:
        util.exit_message("Cannot find cluster, you may need to import-cluster", 1)
    util.exit_message(cluster_id, 0)


def get_node_id(cluster_name, node_name):
    """Return the node id based on cluster and node display name

    Return the cluster id based on a cluster display name
    [ Requires ./ctl secure import-cluster-def ]
      CLUSTER_NAME - the display name of the pgEdge Cloud Cluster
      NODE_NAME - the display name of the pgEdge Cloud Node
    """
    try:
        with open(
            f"{cluster_dir}{os.sep}{cluster_name}{os.sep}{cluster_name}.json"
        ) as f:
            parsed_json = json.load(f)
            for n in parsed_json["nodes"]:
                if n["name"] == node_name:
                    node_id = n["id"]
    except Exception:
        util.exit_message("Cannot find node, you may need to import-cluster", 1)
    util.exit_message(node_id, 0)


def create_cluster(cluster_name, profile="Default"):
    """Create a new Cloud Cluster based on json file

    Create a new cluster in a pgEdge Cloud Account
    [ Requires ./ctl secure config ]
      CLUSTER_NAME - the name of the json file and display name of the to be created cluster
      PROFILE - profile name of pgEdge Cloud Account for NodeCTL to use
    See documentation for sample json files
    """
    with open(f"{cluster_name}.json") as f:
        parsed_json = json.load(f)
    post_pgedge("clusters", parsed_json)
    response = get_pgedge("clusters", profile)
    for cluster in response:
        if cluster["name"] == cluster_name:
            cluster_id = cluster["id"]
    util.exit_message(f"Creating Cluster with id {cluster_id}", 0)


def destroy_cluster(cluster_id, profile="Default"):
    """Delete a pgEdge Cloud Cluster

    Delete a cluster in a pgEdge Cloud Account
    [ Requires ./ctl secure config ]
      CLUSTER_ID - the pgEdge Cloud Cluster ID
      PROFILE - profile name of pgEdge Cloud Account for NodeCTL to use
    """
    delete_pgedge(f"clusters/{cluster_id}", profile)
    util.exit_message(f"Deleting Cluster with id {cluster_id}", 0)


if __name__ == "__main__":
    fire.Fire(
        {
            "config": config,
            "list-cloud-acct": list_cloud_acct,
            "list-clusters": list_clusters,
            "cluster-status": cluster_status,
            "list-nodes": list_nodes,
            "import-cluster-def": import_cluster_def,
            "get-cluster-id": get_cluster_id,
            "get-node-id": get_node_id,
            "create-cluster": create_cluster,
            "destroy-cluster": destroy_cluster,
        }
    )
