#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, random, json, socket, datetime
import util, fire, meta, subprocess
import pgbench, northwind, cluster

cluster_dir = "cluster"

def get_access_token(auth_json):
  ## Use pgEdge Cloud CLI to get access token
  access_token=None
  cred=json.dumps(auth_json).replace("{","").replace("}","")
  try:
    os.system(f"~/go/bin/pgedge generateaccesstoken {cred} > {cluster_dir}{os.sep}token.json") 
    parsed_json = None
    with open(f"{cluster_dir}{os.sep}token.json") as f:
      parsed_json = json.load(f)
      access_token = parsed_json["access_token"]
  except:
    util.exit_message(f"Unable to get token")
  return access_token


def validate_profile(profile):
  pgede_dir = os.path.expanduser("~")
  found=False
  with open(f"{pgede_dir}{os.sep}.pgedge{os.sep}credentials.json") as f:
      parsed_json = json.load(f)
      for prof in parsed_json["profiles"]:
        if profile==prof:
          found=True
  return found


def call_pgedgecli(cmd, profile):
  ## Execute a pgEdgeCLI command
  if validate_profile(profile):
    os.system(f"~/go/bin/pgedge {cmd} --profile={profile}")
  else:
    util.exit_message(f"You must log into this profile")


def get_pgedgecli(cmd, profile):
  ## Execute a pgEdgeCLI command and save output
  return_json={}
  if validate_profile(profile):
    return_json=subprocess.check_output(f"~/go/bin/pgedge {cmd} --profile={profile}", shell=True)
  else:
    util.exit_message(f"You must log into this profile")
  return json.loads(return_json.decode('utf8'))
    

def login(client_id, client_secret, profile="pgedge"):
  """Login nodeCtl with a pgEdge Cloud Account"""
  try:
    ## Create Creds File
    os.system(f"mkdir -p {cluster_dir}")
    text_file = open(f"{cluster_dir}{os.sep}creds.json", "w")
    auth_json = {}
    auth_json["client_id"] = client_id
    auth_json["client_secret"] = client_secret
    text_file.write(json.dumps(auth_json))
    ## Get Access Token
    access_token=get_access_token(auth_json)
    ## Register Auth profile
    os.system(f"~/go/bin/pgedge auth add-profile {profile} {access_token}")  
  except:
    util.exit_message(f"Unable to create creds file")
  return f"Logged in with profile: {profile}"


def list_clusters(profile="pgedge"):
  """List all clusters in a pgEdge Cloud Account"""
  call_pgedgecli("listclusters", profile)


def list_cluster_nodes(cluster_id, profile="pgedge"):
  """List all nodes in a pgEdge Cloud Account cluster"""
  call_pgedgecli(f"listclusternodes {cluster_id}", profile)
  

def import_cluster(cluster_id, profile="pgedge"):
  """Enable nodeCtl cluster commands on a pgEdge Cloud Cluster"""
  cluster_def=get_pgedgecli(f"listclusters {cluster_id}", profile)
  cluster_name=cluster_def[0]["name"].lower()
  id=cluster_def[0]["id"]
  db=cluster_def[0]["database"]["name"]
  usr="pgedge"
  passwd=""
  pg=cluster_def[0]["database"]["pg_version"]
  create_dt=cluster_def[0]["created_at"]
  n=0
  nodes=[]
  node_def=get_pgedgecli(f"listclusternodes {cluster_id}", profile)
  for node in node_def:
    node_json={}
    n=n+1
    node_json["name"]=node["name"]
    node_json["id"]=node["id"]
    node_json["path"]="/opt/pgedge"
    node_json["port"]="5432"
    node_json["ip"]=node["public_ip_address"]
    nodes.append(node_json)
  cluster.create_remote_json(cluster_name, db, n, usr, passwd, pg, create_dt, id, nodes)
  return("Cluster info json file created")


def get_cluster_id(cluster_name):
  """Return the cluster id based on a cluster display name"""
  try:
    with open(f"{cluster_dir}{os.sep}{cluster_name}{os.sep}{cluster_name}.json") as f:
      parsed_json = json.load(f)
      cluster_id=parsed_json["id"]
  except:
    util.exit_message(f"Cannot find cluster, you may need to import-cluster")
  return cluster_id


def get_node_id(cluster_name,node_name):
  """Return the node id based on cluster and node display name"""
  try:
    with open(f"{cluster_dir}{os.sep}{cluster_name}{os.sep}{cluster_name}.json") as f:
      parsed_json = json.load(f)
      for n in parsed_json["nodes"]:
        if n["name"]==node_name:
          node_id=n["id"]
  except:
    util.exit_message(f"Cannot find node, you may need to import-cluster")
  return node_id


def push_metrics(cluster_name, target_info, client_id=None, client_secret=None):
  """push pgEdge Metrics to a specified target"""
  util.exit_message("Coming Soon!")


def create_cluster(cluster_name, cluster_info, client_id=None, client_secret=None):
  """Create a pgEdge Cloud Cluster"""
  util.exit_message("Coming Soon!")


def destroy_cluster(cluster_id, profile="pgedge"):
  """Delete a pgEdge Cloud Cluster"""
  call_pgedgecli(f"deletecluster {cluster_id}", profile)


if __name__ == '__main__':
  fire.Fire({
    'login':              login,
    'list-clusters':      list_clusters,
    'list-cluster-nodes': list_cluster_nodes,
    'import-cluster':     import_cluster,
    'get-cluster-id':     get_cluster_id,
    'get-node-id':        get_node_id,
    'push-metrics':       push_metrics,
    'create-cluster':     create_cluster,
    'destroy-cluster':    destroy_cluster
  })
