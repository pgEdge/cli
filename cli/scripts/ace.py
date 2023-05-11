#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

"""ACE is the place of the Anti Chaos Engine"""

import os, sys, random, time, json, socket
import util, fire, meta, pgbench, cluster


def diff_schemas():
  """Compare schema on different cluster nodes"""
  pass


def diff_spock():
  """Compare spock setup on different cluster nodes"""
  pass


def diff_tables(cluster_name, node1, node2, table_name):
  """Compare table on different cluster nodes"""

  if not os.path.isdir("pgdiff"):
    util.message("Installing the required 'pgdiff' component.")
    os.system("./nodectl install pgdiff")

  util.message(f"Validating Cluster {cluster_name} exists")
  util.check_cluster_exists(cluster_name)

  if node1 == node2:
    util.exit_message("node1 must be different than node2")

  util.message(f"Validating nodes {node1} & {node2} exist")
  util.check_node_exists(cluster_name, node1)
  util.check_node_exists(cluster_name, node2)

  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)
  ##print(f"DEBUG: db = {db}, user={usr}, nodes = {nodes}")
  node1_con = ""
  node2_con = ""
  for nd in nodes:
    if nd["nodename"] == node1:
      prt = nd["port"]
      adr = nd["ip"]
      node1_con = f"db={db}, port={prt}, host={adr}, user={usr}"
      print(f"DEBUG: node1_con: '{node1_con}'")

    if nd["nodename"] == node2:
      prt = nd["port"]
      adr = nd["ip"]
      node2_con = f"db={db}, port={prt}, host={adr}, user={usr}"
      print(f"DEBUG: node2_con: '{node2_con}'")


if __name__ == '__main__':
  fire.Fire({
    'diff-tables':    diff_tables,
    'diff-schemas':   diff_schemas,
    'diff-spock':     diff_spock
  })
