#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, random, json, socket, datetime
import util, fire, meta, subprocess, requests
import pgbench, northwind, cluster

cluster_dir = "cluster"

def get_access_token(auth_json):
  ## Use pgEdge Cloud CLI to get access token
  access_token=None
  cred=json.dumps(auth_json).replace("{","").replace("}","")
  try:
    url = "https://api.pgedge.com/oauth/token"
    response = requests.post(url, json=auth_json)
    if str(response.status_code)=='200':
      access_token = response.json()["access_token"]
    else:
      util.exit_message(f"Unable to get token")
  except:
    util.exit_message(f"Unable to get token")
  return access_token


def get_pgedge(cmd):
  ## Call Get to pgEdge CLI
  with open(f"{cluster_dir}{os.sep}creds.json") as f:
    parsed_json = json.load(f)
    access=get_access_token(parsed_json)
  url = "https://api.pgedge.com/" + cmd 
  header={}
  header["Authorization"]="Bearer " + access
  response = requests.get(url, headers=header)
  if str(response.status_code)=='200':
    return response.json()
  else:
    util.exit_message(f"Unable to run {cmd}")


def login(client_id, client_secret):
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
    os.system(f"echo {access_token} > {cluster_dir}{os.sep}token.json") 
  except:
    util.exit_message(f"Unable to create creds file")
  print(f"Logged in to pgEdge Secure")
  return 0


def list_clusters():
  """List all clusters in a pgEdge Cloud Account"""
  response=get_pgedge("clusters")
  print(response)
  return 0


def list_cluster_nodes(cluster_id):
  """List all nodes in a pgEdge Cloud Account cluster"""
  response=get_pgedge(f"clusters/{cluster_id}/nodes")
  print(response)
  return 0
  

def import_cluster(cluster_id):
  """Enable nodeCtl cluster commands on a pgEdge Cloud Cluster"""
  cluster_def=get_pgedge(f"clusters/{cluster_id}")
  print(cluster_def)
  cluster_name=cluster_def["name"].lower()
  id=cluster_def["id"]
  db=cluster_def["database"]["name"]
  usr="pgedge"
  passwd=""
  pg=cluster_def["database"]["pg_version"]
  create_dt=cluster_def["created_at"]
  n=0
  nodes=[]
  node_def=get_pgedge(f"clusters/{cluster_id}/nodes")
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
  print("Cluster info json file created")
  return 0


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


def destroy_cluster(cluster_id):
  """Delete a pgEdge Cloud Cluster"""
  util.exit_message("Coming Soon!")


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
