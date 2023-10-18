####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

"""ACE is the place of the Anti Chaos Engine"""

import os
import json

import subprocess
import re
import util
import fire
import cluster
import psycopg
from datetime import datetime
from multiprocessing import Manager, cpu_count, Value, Queue
from ordered_set import OrderedSet
from itertools import combinations
from mpire import WorkerPool
from concurrent.futures import ThreadPoolExecutor

l_dir = "/tmp"

# Shared variables needed by multiprocessing
queue = Manager().list()
result_queue = Manager().list()
row_diff_count = Value("I", 0)

# Set max number of rows up to which
# diff-tables will work
MAX_DIFF_ROWS = 10000
MAX_ALLOWED_BLOCK_SIZE = 100000
MAX_CPU_RATIO = 0.6

# Return codes for compare_checksums
BLOCK_OK = 0
MAX_DIFF_EXCEEDED = 1
BLOCK_MISMATCH = 2
BLOCK_ERROR = 3


def prCyan(skk):
    print("\033[96m {}\033[00m".format(skk))


def prRed(skk):
    print("\033[91m {}\033[00m".format(skk))


def get_csv_file_name(p_prfx, p_schm, p_tbl, p_base_dir="/tmp"):
    return p_base_dir + os.sep + p_prfx + "-" + p_schm + "-" + p_tbl + ".csv"


def get_dump_file_name(p_prfx, p_schm, p_base_dir="/tmp"):
    return p_base_dir + os.sep + p_prfx + "-" + p_schm + ".sql"


def write_pg_dump(p_ip, p_db, p_prfx, p_schm, p_base_dir="/tmp"):
    out_file = get_dump_file_name(p_prfx, p_schm, p_base_dir)
    try:
        cmd = (
            "pg_dump -s -n " + p_schm + " -h " + p_ip + " -d " + p_db + " > " + out_file
        )
        os.system(cmd)
    except Exception as e:
        util.exit_exception(e)
    return out_file


def fix_schema(diff_file, sql1, sql2):
    newtable = False
    with open(diff_file) as diff_list:
        for i in diff_list.readlines():
            if re.search("\,", i):
                # TODO: Fix this
                # linenum = i.split(",")[0]
                pass
            elif re.search(r"^< CREATE.", i):
                newtable = True
                print(i.replace("<", ""))
            elif re.search(r"^< ALTER.", i):
                print(i.replace("<", ""))
            elif re.search(r"^> CREATE TABLE.", i):
                print(
                    " DROP TABLE " + i.replace("> CREATE TABLE ", "").replace(" (", ";")
                )
            elif newtable:
                print(i.replace("<", ""))
                if re.search(r".;$", i):
                    newtable = False
            else:
                continue
    return 1


def get_row_count(p_con, p_schema, p_table):
    sql = f"SELECT count(*) FROM {p_schema}.{p_table}"

    try:
        cur = p_con.cursor()
        cur.execute(sql)
        r = cur.fetchone()
        cur.close()
    except Exception as e:
        util.exit_message("Error in get_row_count():\n" + str(e), 1)

    if not r:
        return 0

    rows = int(r[0])

    return rows


def get_cols(p_con, p_schema, p_table):
    sql = """
    SELECT ordinal_position, column_name
    FROM information_schema.columns
    WHERE table_schema = %s and table_name = %s
    ORDER BY 1, 2
    """

    try:
        cur = p_con.cursor()
        cur.execute(
            sql,
            [
                p_schema,
                p_table,
            ],
        )
        rows = cur.fetchall()
        cur.close()
    except Exception as e:
        util.exit_message("Error in get_cols():\n" + str(e), 1)

    if not rows:
        return None

    col_lst = []
    for row in rows:
        col_lst.append(str(row[1]))

    return ",".join(col_lst)


def get_key(p_con, p_schema, p_table):
    sql = """
    SELECT C.COLUMN_NAME
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS T,
    INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE C
    WHERE c.constraint_name = t.constraint_name
    AND c.table_schema = t.constraint_schema
    AND c.table_schema = %s AND c.table_name = %s
    AND T.CONSTRAINT_TYPE='PRIMARY KEY'
    """

    try:
        cur = p_con.cursor()
        cur.execute(
            sql,
            [
                p_schema,
                p_table,
            ],
        )
        rows = cur.fetchall()
        cur.close()
    except Exception as e:
        util.exit_message("Error in get_key():\n" + str(e), 1)

    if not rows:
        return None

    key_lst = []
    for row in rows:
        key_lst.append(str(row[0]))

    return ",".join(key_lst)


def diff_schemas(cluster_name, node1, node2, schema_name):
    """Compare Postgres schemas on different cluster nodes"""
    if not os.path.isfile("/usr/local/bin/csvdiff"):
        util.message("Installing the required 'csvdiff' component.")
        os.system("./nodectl install csvdiff")

    util.message(f"## Validating cluster {cluster_name} exists")
    util.check_cluster_exists(cluster_name)

    if node1 == node2:
        util.exit_message("node1 must be different than node2")

    l_schema = schema_name

    il, db, pg, count, usr, passwd, os_user, cert, nodes = cluster.load_json(
        cluster_name
    )
    util.message(f"## db={db}, user={usr}\n")
    for nd in nodes:
        if nd["nodename"] == node1:
            sql1 = write_pg_dump(nd["ip"], db, "con1", l_schema)
        if nd["nodename"] == node2:
            sql2 = write_pg_dump(nd["ip"], db, "con2", l_schema)

    cmd = "diff " + sql1 + "  " + sql2 + " > /tmp/diff.txt"
    util.message("\n## Running # " + cmd + "\n")
    rc = os.system(cmd)
    if rc == 0:
        util.message("SCHEMAS ARE THE SAME!!")
        return rc
    else:
        util.message("SCHEMAS ARE NOT THE SAME!!")
        util.message("")
        rc = fix_schema("/tmp/diff.txt", sql1, sql2)
    return rc


def diff_spock(cluster_name, node1, node2):
    """Compare spock meta data setup on different cluster nodes"""
    util.check_cluster_exists(cluster_name)

    if node1 == node2:
        util.exit_message("node1 must be different than node2")

    il, db, pg, count, usr, passwd, os_usr, cert, cluster_nodes = cluster.load_json(
        cluster_name
    )
    compare_spock = []
    pg_v = util.get_pg_v(pg)
    print("\n")

    for cluster_node in cluster_nodes:
        if cluster_node["nodename"] not in [node1, node2]:
            continue
        diff_spock = {}
        diff_sub = {}
        hints = []
        print(" Spock - Config " + cluster_node["nodename"])
        print("~~~~~~~~~~~~~~~~~~~~~~~~~")
        prCyan("Node:")
        sql = """
        SELECT n.node_id, n.node_name, n.location, n.country,
           s.sub_id, s.sub_name, s.sub_enabled, s.sub_replication_sets
           FROM spock.node n LEFT OUTER JOIN spock.subscription s
           ON s.sub_target=n.node_id WHERE s.sub_name IS NOT NULL;
        """
        node_info = util.run_psyco_sql(pg_v, db, sql, cluster_node["ip"])
        print("  " + node_info[0]["node_name"])
        diff_spock["node"] = node_info[0]["node_name"]

        prCyan("  Subscriptions:")

        for node in node_info:
            if node["sub_name"] is None:
                hints.append("Hint: No subscriptions have been created on this node")
            else:
                print("    " + node["sub_name"])
                diff_sub["sub_name"] = node["sub_name"]
                diff_sub["sub_enabled"] = node["sub_enabled"]
                prCyan("    RepSets:")
                diff_sub["replication_sets"] = node["sub_replication_sets"]
                print("      " + json.dumps(node["sub_replication_sets"]))
                if node["sub_replication_sets"] == []:
                    hints.append("Hint: No replication sets added to subscription")
                elif node["sub_replication_sets"] == [
                    "default",
                    "default_insert_only",
                    "ddl_sql",
                ]:
                    hints.append(
                        "Hint: Only default replication sets added to subscription: "
                        + node["sub_name"]
                    )
                diff_spock["subscriptions"] = diff_sub

        sql = """
        SELECT set_name, string_agg(relname,'   ') as relname
        FROM spock.tables GROUP BY set_name ORDER BY set_name;
        """
        table_info = util.run_psyco_sql(pg_v, db, sql, cluster_node["ip"])
        diff_spock["rep_set_info"] = []
        prCyan("Tables in RepSets:")
        if table_info == []:
            hints.append("Hint: No tables in database")
        for table in table_info:
            if table["set_name"] is None:
                print(" - Not in a replication set")
                hints.append(
                    "Hint: Tables not in replication set might not have primary keys, \
                        or you need to run repset-add-table"
                )
            else:
                print(" - " + table["set_name"])

            diff_spock["rep_set_info"].append({table["set_name"]: table["relname"]})
            print("   - " + table["relname"])

        compare_spock.append(diff_spock)

        for hint in hints:
            prRed(hint)
        print("\n")

    if len(compare_spock) == 2:
        print(" Spock - Diff")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~")
        if compare_spock[0]["rep_set_info"] == compare_spock[1]["rep_set_info"]:
            prCyan("   Replication Rules are the same!!")
        else:
            prRed("    Difference in Replication Rules")

    return compare_spock


def run_query(worker_state, host, query):
    cur = worker_state[host]
    cur.execute(query)
    results = cur.fetchall()
    return results


def init_db_connection(shared_objects, worker_state):
    # Read cluster information and connect to the local instance of pgcat
    il, db, pg, count, usr, passwd, os_usr, cert, nodes = cluster.load_json(
        shared_objects["cluster_name"]
    )

    for node in nodes:
        conn_str = f"dbname = {db}      \
                    user={usr}          \
                    password={passwd}   \
                    host={node['ip']}   \
                    port={node.get('port', 5432)}"

        worker_state[node["nodename"]] = psycopg.connect(conn_str).cursor()


def compare_checksums(
    shared_objects,
    worker_state,
    offset,
):
    global row_diff_count

    if row_diff_count.value >= MAX_DIFF_ROWS:
        return

    p_key = shared_objects["p_key"]
    table_name = shared_objects["table_name"]
    block_rows = shared_objects["block_rows"]
    node_list = shared_objects["node_list"]
    cols = shared_objects["cols_list"]

    hash_sql = f"""
    SELECT md5(cast(array_agg(t.* ORDER BY {p_key}) AS text))
    FROM (SELECT *
            FROM {table_name}
            ORDER BY {p_key}
            OFFSET {offset}
            LIMIT {block_rows}) t;
    """

    block_sql = f"""
    SELECT *
    FROM {table_name}
    ORDER BY {p_key}
    OFFSET {offset}
    LIMIT {block_rows}
    """

    node_pairs = combinations(node_list, 2)

    block_result = {}
    block_result["offset"] = offset
    block_result["diffs"] = []

    for node_pair in node_pairs:
        host1 = node_pair[0]
        host2 = node_pair[1]

        # Return early if we have already exceeded the max number of diffs
        if row_diff_count.value >= MAX_DIFF_ROWS:
            queue.append(block_result)
            return

        try:
            # Run the checksum query on both nodes in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(run_query, worker_state, host1, hash_sql),
                    executor.submit(run_query, worker_state, host2, hash_sql),
                ]
                hash1, hash2 = [f.result()[0][0] for f in futures]
        except Exception:
            result_queue.append(BLOCK_ERROR)
            return

        if hash1 != hash2:
            try:
                # Run the block query on both nodes in parallel
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(run_query, worker_state, host1, block_sql),
                        executor.submit(run_query, worker_state, host2, block_sql),
                    ]
                    t1_result, t2_result = [f.result() for f in futures]
            except Exception:
                result_queue.append(BLOCK_ERROR)
                return

            # Collect results into OrderedSets for comparison
            t1_set = OrderedSet(t1_result)
            t2_set = OrderedSet(t2_result)

            t1_diff = t1_set - t2_set
            t2_diff = t2_set - t1_set

            if len(t1_diff) > 0 or len(t2_diff) > 0:
                block_result["diffs"].append(
                    {
                        host1: [dict(zip(cols, row)) for row in t1_diff],
                        host2: [dict(zip(cols, row)) for row in t2_diff],
                    }
                )

            with row_diff_count.get_lock():
                row_diff_count.value += max(len(t1_diff), len(t2_diff))

            if row_diff_count.value >= MAX_DIFF_ROWS:
                queue.append(block_result)
                result_queue.append(MAX_DIFF_EXCEEDED)
                return
            else:
                result_queue.append(BLOCK_MISMATCH)

        else:
            result_queue.append(BLOCK_OK)

    if len(block_result["diffs"]) > 0:
        queue.append(block_result)


def table_diff(
    cluster_name,
    table_name,
    block_rows=1000,
    max_cpu_ratio=MAX_CPU_RATIO,
    output="csv",
    nodes="all",
):
    """Efficiently compare tables across cluster using checksums and blocks of rows."""

    # Capping max block size here to prevent the hash function from taking forever
    if block_rows > MAX_ALLOWED_BLOCK_SIZE:
        util.exit_message(f"Desired block row size is > {MAX_ALLOWED_BLOCK_SIZE}")

    if output not in ["csv", "json"]:
        util.exit_message(
            "Diff-tables currently supports only csv and json output formats"
        )

    bad_br = True
    try:
        b_r = int(block_rows)
        if b_r >= 1000:
            bad_br = False
    except ValueError:
        pass
    if bad_br:
        util.exit_message(f"block_rows param '{block_rows}' must be integer >= 1000")

    node_list = []

    try:
        if nodes != "all":
            node_list = [s.strip() for s in nodes.split(",")]
    except ValueError as e:
        util.exit_message(
            f'Nodes should be a comma-separated list of nodenames. \
                E.g., --nodes="n1,n2". Error: {e}'
        )

    if len(node_list) > 3:
        util.exit_message(
            "diff-tables currently supports up to a three-way table comparison"
        )

    if nodes != "all" and len(node_list) == 1:
        util.exit_message("diff-tables needs at least two nodes to compare")

    util.check_cluster_exists(cluster_name)
    util.message(f"Cluster {cluster_name} exists", p_state="success")

    nm_lst = table_name.split(".")
    if len(nm_lst) != 2:
        util.exit_message(f"TableName {table_name} must be of form 'schema.table_name'")
    l_schema = nm_lst[0]
    l_table = nm_lst[1]

    il, db, pg, count, usr, passwd, os_usr, cert, cluster_nodes = cluster.load_json(
        cluster_name
    )

    if nodes != "all" and len(node_list) > 1:
        for n in node_list:
            if not any(filter(lambda x: x["nodename"] == n, cluster_nodes)):
                util.exit_message("Specified nodenames not present in cluster")

    conn_list = []

    try:
        for nd in cluster_nodes:
            if nodes == "all":
                node_list.append(nd["nodename"])

            if (node_list and nd["nodename"] in node_list) or (not node_list):
                psql_conn = psycopg.connect(
                    dbname=db,
                    user=usr,
                    password=passwd,
                    host=nd["ip"],
                    port=nd.get("port", 5432),
                )
                conn_list.append(psql_conn)

    except Exception as e:
        util.exit_message("Error in diff_tbls() Getting Connections:" + str(e), 1)

    util.message("Connections successful to nodes in cluster", p_state="success")

    cols = None
    key = None

    for conn in conn_list:
        curr_cols = get_cols(conn, l_schema, l_table)
        curr_key = get_key(conn, l_schema, l_table)

        if not curr_cols:
            util.exit_message(f"Invalid table name '{table_name}'")
        if not curr_key:
            util.exit_message(f"No primary key found for '{table_name}'")

        if (not cols) and (not key):
            cols = curr_cols
            key = curr_key
            continue

        if (curr_cols != cols) or (curr_key != key):
            util.exit_message("Table schemas don't match")

        cols = curr_cols
        key = curr_key

    util.message(f"Table {table_name} is comparable across nodes", p_state="success")

    row_count = 0
    total_rows = 0

    for conn in conn_list:
        rows = get_row_count(conn, l_schema, l_table)
        total_rows += rows
        if rows > row_count:
            row_count = rows

    total_blocks = row_count // block_rows
    total_blocks = total_blocks if total_blocks > 0 else 1
    cpus = cpu_count()
    max_procs = int(cpus * max_cpu_ratio * 2) if cpus > 1 else 1
    procs = (
        max_procs if total_blocks > max_procs else total_blocks
    )  # if we don't have enough blocks to keep all CPUs busy, use fewer processes

    start_time = datetime.now()

    """
    Generate offsets for each process to work on.
    We go up to the max rows among all nodes because we want our set difference logic
    to capture diffs even if rows are absent in one node
    """
    offsets = [x for x in range(0, row_count + 1, block_rows)]

    cols_list = cols.split(",")

    # Shared variables needed by all workers
    shared_objects = {
        "cluster_name": cluster_name,
        "node_list": node_list,
        "table_name": table_name,
        "cols_list": cols_list,
        "p_key": key,
        "block_rows": block_rows,
    }

    print("")
    util.message("Starting jobs to compare tables...\n", p_state="info")

    with WorkerPool(
        n_jobs=procs,
        shared_objects=shared_objects,
        use_worker_state=True,
    ) as pool:
        pool.map_unordered(
            compare_checksums,
            offsets,
            worker_init=init_db_connection,
            progress_bar=True,
            iterable_len=len(offsets),
        )

    mismatch = False
    diffs_exceeded = False
    errors = False

    for result in result_queue:
        if result == MAX_DIFF_EXCEEDED:
            diffs_exceeded = True

        if result == BLOCK_MISMATCH or result == MAX_DIFF_EXCEEDED:
            mismatch = True

        if result == BLOCK_ERROR:
            errors = True

    print("")

    if errors:
        util.exit_message(
            "There were one or more errors while connecting to databases.\n \
                Please examine the connection information provided, or the nodes' \
                    status before running this script again."
        )

    # Mismatch is True if there is a block mismatch or if we have
    # estimated that diffs may be greater than max allowed diffs
    if mismatch:
        if diffs_exceeded:
            util.message(
                f"TABLES DO NOT MATCH. DIFFS HAVE EXCEEDED {MAX_DIFF_ROWS} ROWS",
                p_state="warning",
            )

        else:
            util.message("TABLES DO NOT MATCH", p_state="warning")

        """
        Read the result queue and count differences between each node pair
        in the cluster
        """

        diff_count = {}
        for entry in queue:
            diff_list = entry["diffs"]

            if not diff_list:
                continue

            for diff_json in diff_list:
                node1, node2 = diff_json.keys()
                diff_count[node1 + "_" + node2] = diff_count.get(
                    node1 + "_" + node2, 0
                ) + max(len(diff_json[node1]), len(diff_json[node2]))

        for key in diff_count.keys():
            node1, node2 = key.split("_")
            util.message(
                f"FOUND {diff_count[key]} DIFFS BETWEEN {node1} AND {node2}",
                p_state="warning",
            )

        if output == "json":
            write_diffs_json(block_rows)

        elif output == "csv":
            write_diffs_csv()

    else:
        util.message("TABLES MATCH OK\n", p_state="success")

    run_time = datetime.now() - start_time
    util.message(
        f"TOTAL ROWS CHECKED = {total_rows}. RUN TIME = {run_time}", p_state="info"
    )


def write_diffs_json(block_rows):
    output_json = {}

    output_json["total_diffs"] = row_diff_count.value
    output_json["block_size"] = block_rows
    output_json["diffs"] = [cur_entry for cur_entry in queue]

    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = "diff_" + ts + ".json"

    with open(filename, "w") as f:
        f.write(json.dumps(output_json, default=str))

    util.message(f"Diffs written out to {filename}", p_state="info")


# TODO: Come up with better naming convention for diff files
def write_diffs_csv():
    import pandas as pd

    seen_nodepairs = {}

    for entry in queue:
        diff_list = entry["diffs"]

        if not diff_list:
            continue

        for diff_json in diff_list:
            node1, node2 = diff_json.keys()
            t1_write_path = node1 + "_X_" + node2 + "_" + node1 + ".csv"
            t2_write_path = node1 + "_X_" + node2 + "_" + node2 + ".csv"

            df1 = pd.DataFrame.from_dict(diff_json[node1])
            df2 = pd.DataFrame.from_dict(diff_json[node2])

            lookup_str = node1 + "," + node2

            if lookup_str in seen_nodepairs:
                df1.to_csv(t1_write_path, mode="a", header=False, index=False)
                df2.to_csv(t2_write_path, mode="a", header=False, index=False)
            else:
                seen_nodepairs[lookup_str] = 1
                df1.to_csv(t1_write_path, header=True, index=False)
                df2.to_csv(t2_write_path, header=True, index=False)

    for node_pair in seen_nodepairs.keys():
        n1, n2 = node_pair.split(",")
        diff_file_name = n1 + "_X_" + n2 + ".diff"
        t1_write_path = n1 + "_X_" + n2 + "_" + n1 + ".csv"
        t2_write_path = n1 + "_X_" + n2 + "_" + n2 + ".csv"
        cmd = f"diff -u {t1_write_path} {t2_write_path} | ydiff > {diff_file_name}"
        subprocess.check_output(cmd, shell=True)

        util.message(
            f"Diffs between {n1} and {n2} have been written out to {diff_file_name}",
            p_state="info",
        )


def table_repair(cluster_name, diff_file, source_of_truth, table_name, dry_run=False):
    import pandas as pd

    # Check if diff_file exists on disk
    if not os.path.exists(diff_file):
        util.exit_message(f"Diff file {diff_file} does not exist")

    util.check_cluster_exists(cluster_name)
    util.message(f"Cluster {cluster_name} exists", p_state="success")

    nm_lst = table_name.split(".")
    if len(nm_lst) != 2:
        util.exit_message(f"TableName {table_name} must be of form 'schema.table_name'")

    l_schema = nm_lst[0]
    l_table = nm_lst[1]

    il, db, pg, count, usr, passwd, os_usr, cert, cluster_nodes = cluster.load_json(
        cluster_name
    )

    # Check to see if source_of_truth node is present in cluster
    if not any(node.get("nodename") == source_of_truth for node in cluster_nodes):
        util.exit_message(
            f"Source of truth node {source_of_truth} not present in cluster"
        )

    conn_list = []
    try:
        for nd in cluster_nodes:
            conn_list.append(
                psycopg.connect(
                    dbname=db,
                    user=usr,
                    password=passwd,
                    host=nd["ip"],
                    port=nd.get("port", 5432),
                )
            )

    except Exception as e:
        util.exit_message("Error in diff_tbls() Getting Connections:" + str(e), 1)

    util.message("Connections successful to nodes in cluster", p_state="success")

    cols = None
    key = None

    for conn in conn_list:
        curr_cols = get_cols(conn, l_schema, l_table)
        curr_key = get_key(conn, l_schema, l_table)

        if not curr_cols:
            util.exit_message(f"Invalid table name '{table_name}'")
        if not curr_key:
            util.exit_message(f"No primary key found for '{table_name}'")

        if (not cols) and (not key):
            cols = curr_cols
            key = curr_key
            continue

        if (curr_cols != cols) or (curr_key != key):
            util.exit_message("Table schemas don't match")

        cols = curr_cols
        key = curr_key

    util.message(f"Table {table_name} is comparable across nodes", p_state="success")

    with open(diff_file) as f:
        diff_json = json.load(f)

    true_df = pd.DataFrame()
    true_rows = [
        entry
        for diff in diff_json["diffs"]
        for d in diff["diffs"]
        for entry in d.get(source_of_truth, [])
    ]

    # Collect all rows from our source of truth node and dedupe
    true_df = pd.concat([true_df, pd.DataFrame(true_rows)], ignore_index=True)
    true_df.drop_duplicates(inplace=True)

    true_df[key] = true_df[key].astype(str)

    # Remove the key column from the list of columns
    true_df = true_df[[c for c in true_df if c not in [key]]]
    for conn in conn_list:
        # Unpack true_df into (key, row) tuples
        true_rows = true_df.to_records(index=False)

    true_rows = [tuple(str(x) for x in row) for row in true_rows]

    print()

    nodes_to_repair = ",".join(
        [nd["nodename"] for nd in cluster_nodes if nd["nodename"] != source_of_truth]
    )
    dry_run_msg = (
        "######## DRY RUN ########\n\n"
        f"Repair would have attempted to upsert {len(true_rows)} rows on "
        f"{nodes_to_repair}\n\n"
        "######## END DRY RUN ########"
    )
    if dry_run:
        util.message(dry_run_msg, p_state="alert")
        return

    cols_list = cols.split(",")
    # Remove the key column from the list of columns
    cols_list.remove(key)

    """
    Here we are constructing an UPDATE query from true_rows and applying it to all nodes
    """
    update_sql = f"""
    INSERT INTO {table_name} ({','.join(cols_list)})
    VALUES ({','.join(['%s'] * len(cols_list))})
    ON CONFLICT ({key}) DO UPDATE SET
    """

    for col in cols_list:
        update_sql += f"{col} = EXCLUDED.{col}, "

    update_sql = update_sql[:-2] + ";"

    # Apply the diffs to all nodes in the cluster
    for conn in conn_list:
        try:
            cur = conn.cursor()
            cur.executemany(update_sql, true_rows)
            conn.commit()
            cur.close()
        except Exception as e:
            print(update_sql, true_rows)
            util.exit_message("Error in repair():" + str(e), 1)

    util.message(
        f"Successfully applied diffs to {table_name} in cluster {cluster_name}",
        p_state="success",
    )


if __name__ == "__main__":
    fire.Fire(
        {
            "table-diff": table_diff,
            "diff-schemas": diff_schemas,
            "diff-spock": diff_spock,
            "table-repair": table_repair,
        }
    )

