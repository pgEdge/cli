#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, random, json, socket, datetime
import util, fire, meta
import pgbench, northwind

cluster_dir = "cluster"

def get_access_token(auth_json):
  ## Use pgEdge Cloud CLI to get access token
  access_token=None
  cred=json.dumps(auth_json).replace("{","").replace("}","")
  try:
    os.system("~/go/bin/pgedge generateaccesstoken " + cred + " > " + cluster_dir + os.sep + "token.json") 
    parsed_json = None
    with open(cluster_dir + os.sep + "token.json") as f:
      parsed_json = json.load(f)
      access_token = parsed_json["access_token"]
  except:
    util.exit_message(f"Unable to get token")
  return access_token


def validate_profile(profile):
  pgede_dir = os.path.expanduser("~")
  found=False
  with open(pgede_dir + os.sep + ".pgedge" + os.sep + "credentials.json") as f:
      parsed_json = json.load(f)
      for prof in parsed_json["profiles"]:
        if profile==prof:
          found=True
  return found
    

def register(client_id, client_secret, profile="pgedge"):
  """Register nodeCtl with a pgEdge Cloud Account"""
  try:
    ## Create Creds File
    os.system("mkdir -p " + cluster_dir)
    text_file = open(cluster_dir + os.sep + "creds.json", "w")
    auth_json = {}
    auth_json["client_id"] = client_id
    auth_json["client_secret"] = client_secret
    text_file.write(json.dumps(auth_json))
    ## Get Access Token
    access_token=get_access_token(auth_json)
    ## Register Auth profile
    os.system("~/go/bin/pgedge auth add-profile " + profile + " " + access_token)  
  except:
    util.exit_message(f"Unable to create creds file")
  return "Registered with profile: " + profile


def list_clusters(profile="pgedge"):
  """List all clusters in a pgEdge Cloud Account"""
  if validate_profile(profile):
    os.system("~/go/bin/pgedge listclusters --profile=" + profile)
  else:
    util.exit_message(f"Profile needs to be registered")
  

def import_cluster(cluster_name, cluster_id, client_id=None, client_secret=None):
  """Enable nodeCtl cluster commands on a pgEdge Cloud Cluster"""
  util.exit_message("Coming Soon!")

def push_metrics(cluster_name, target_info, client_id=None, client_secret=None):
  """push pgEdge Metrics to a specified target"""
  util.exit_message("Coming Soon!")

def create_cluster(cluster_name, cluster_info, client_id=None, client_secret=None):
  """Create a pgEdge Cloud Cluster"""
  util.exit_message("Coming Soon!")

def destroy_cluster(cluster_name, cluster_id, client_id=None, client_secret=None):
  """Delete a pgEdge Cloud Cluster"""
  util.exit_message("Coming Soon!")


if __name__ == '__main__':
  fire.Fire({
    'register':        register,
    'list-clusters':   list_clusters,
    'import-cluster':  import_cluster,
    'push-metrics':    push_metrics,
    'create-cluster':  create_cluster,
    'destroy-cluster': destroy_cluster
  })
