#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, random, time, json, socket
import util, fire, meta, pgbench 


def diff_schemas():
  pass


def diff_spock_config():
  pass


def diff_tables(cluster_name, node1, node2, table_name):
  """Compare table on different cluster nodes"""

  if not os.path.isdir("pgdiff"):
    util.message("Installing the required 'pgdiff' component.")
    os.system("./nodectl install pgdiff")

  util.check_cluster_exists(cluster_name)

  if node1 == node2:
    util.exit_message("node1 must be different than node2")

  util.check_node_exists(cluster_name, node1)
  util.check_node_exists(cluster_name, node2)
    

if __name__ == '__main__':
  fire.Fire({
    'diff-tables':       diff_tables,
    'diff-schemas':      diff_schemas,
    'diff-spock-config': diff_spock_config
  })
