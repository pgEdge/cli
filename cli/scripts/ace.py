#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

"""ACE is the place of the Anti Chaos Engine"""

import os, sys, random, time, json, socket, subprocess
import psycopg
import util, fire, meta, pgbench, cluster

l_dir = "/tmp"


def get_csv_file_name(p_prfx, p_schm, p_tbl, p_base_dir="/tmp"):
  return(p_base_dir + os.sep + p_prfx + "-" + p_schm + "-" + p_tbl + ".csv")


def write_tbl_csv(p_con, p_prfx, p_schm, p_tbl, p_cols, p_key, p_base_dir=None):
  try:
    out_file = get_csv_file_name(p_prfx, p_schm, p_tbl, p_base_dir)

    cur = p_con.cursor()

    sql = "SELECT " + p_cols + " " + \
          "  FROM " + p_schm + "." + p_tbl + " " + \
          "ORDER BY " + p_key

    copy_sql = "COPY (" + sql + ") TO STDOUT WITH DELIMITER ',' CSV HEADER;"

    print("\n### COPY table " + p_tbl + " to " + out_file + " #############")

    with open(out_file, "wb") as f:
      with cur.copy(copy_sql) as copy:
        for data in copy:
          f.write(data)

    with open(out_file, 'r') as fp:
      lines = len(fp.readlines())

    print(" detail rows = " + str(format(lines - 1, "n")))
  except Exception as e:
    util.exit_message("Error in write_tbl_csv():\n" + str(e), 1)

  return(out_file)


def get_cols(p_con, p_schema, p_table):
  sql = """
SELECT ordinal_position, column_name
  FROM information_schema.columns
 WHERE table_schema = %s and table_name = %s
ORDER BY 1, 2
"""

  try:
    cur = p_con.cursor()
    cur.execute(sql,[p_schema, p_table,])
    rows = cur.fetchall()
    cur.close()
  except Exception as e:
    util.exit_message("Error in get_cols():\n" + str(e), 1)

  if not rows:
    return(None)

  col_lst = []
  for row in rows:
    col_lst.append(str(row[1]))

  return(','.join(col_lst))


def get_key(p_con, p_schema, p_table):
  sql = """
SELECT C.COLUMN_NAME
  FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS T  , INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE C
 WHERE c.constraint_name = t.constraint_name
   AND c.table_schema = t.constraint_schema
   AND c.table_schema = %s AND c.table_name = %s
   AND T.CONSTRAINT_TYPE='PRIMARY KEY'
"""

  try:
    cur = p_con.cursor()
    cur.execute(sql,[p_schema, p_table,])
    rows = cur.fetchall()
    cur.close()
  except Exception as e:
   util.exit_message("Error in get_key():\n" + str(e), 1)

  if not rows:
    return(None)

  key_lst = []
  for row in rows:
    key_lst.append(str(row[0]))

  return(','.join(key_lst))


def diff_schemas():
  """Compare schema on different cluster nodes"""
  pass


def diff_spock():
  """Compare spock setup on different cluster nodes"""
  pass


def diff_tables(cluster_name, node1, node2, table_name):
  """Compare table on different cluster nodes"""

  if not os.path.isfile("/usr/local/bin/csvdiff"):
    util.message("Installing the required 'csvdiff' component.")
    os.system("./nodectl install csvdiff")

  util.message(f"Validating Cluster {cluster_name} exists")
  util.check_cluster_exists(cluster_name)

  if node1 == node2:
    util.exit_message("node1 must be different than node2")

  util.message(f"Validating nodes {node1} & {node2} exist")
  util.check_node_exists(cluster_name, node1)
  util.check_node_exists(cluster_name, node2)

  nm_lst = table_name.split(".")
  if len(nm_lst) != 2:
    util.exit_message("TableName must be of form 'schema.table_name'")
  l_schema = nm_lst[0]
  l_table = nm_lst[1]
  print(f"schema={l_schema}, table={l_table}")

  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)
  util.message(f"db={db}, user={usr}")
  con1 = None
  con2 = None
  try:
    for nd in nodes:
      if nd["nodename"] == node1:
        util.message("Getting Conection to Node1 - " + nd["ip"] + ":" + str(nd["port"]))
        con1 = psycopg.connect(dbname=db, user=usr, host=nd["ip"], port=nd["port"])

      if nd["nodename"] == node2:
        util.message("Getting Conection to Node2 - " + nd["ip"] + ":" + str(nd["port"]))
        con2 = psycopg.connect(dbname=db, user=usr, host=nd["ip"], port=nd["port"])

  except Exception as e:
    util.exit_message("Error in diff_tbls():\n" + str(e), 1)

  c1_cols = get_cols(con1, l_schema, l_table)
  c1_key = get_key(con1, l_schema, l_table)
  if c1_cols and c1_key:
    print(f"con1 tbl_cols = {c1_cols}   tbl_key = {c1_key}")
  else:
    util.exit_message("Table w/ Primary Key not in con1")

  c2_cols = get_cols(con2, l_schema, l_table)
  c2_key = get_key(con2, l_schema, l_table)
  if c2_cols and c2_key:
    print(f"con2 tbl_cols = {c2_cols}   tbl_key = {c2_key}")
  else:
    util.exit_message("Table w/ Primary Key not in con2")

  if (c1_cols != c2_cols) or (c1_key != c2_key):
    exit_message("Tables don't match in con1 & con2")

  csv1 = write_tbl_csv(con1, "con1", l_schema, l_table, c1_cols, c1_key, l_dir)

  csv2 = write_tbl_csv(con2, "con2", l_schema, l_table, c2_cols, c2_key, l_dir)

  cmd = "csvdiff -o json " + csv1 + "  " + csv2
  print("\n### Running # " + cmd + "\n")
  diff_s = subprocess.check_output(cmd, shell=True)
  diff_j = json.loads(diff_s)

  if diff_j['Additions'] or diff_j['Deletions'] or diff_j['Modifications']:
    print(json.dumps(diff_j, indent=2))
    rc = 1
  else:
    util.message("TABLES ARE IDENTICAL!!")
    rc = 0

  return(rc)



if __name__ == '__main__':
  fire.Fire({
    'diff-tables':    diff_tables,
    'diff-schemas':   diff_schemas,
    'diff-spock':     diff_spock
  })
