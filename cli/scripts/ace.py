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
from psycopg import sql
from psycopg.rows import dict_row
from datetime import datetime
from multiprocessing import Manager, cpu_count, Value, Lock
from ordered_set import OrderedSet
from itertools import combinations
from mpire import WorkerPool
from concurrent.futures import ThreadPoolExecutor

l_dir = "/tmp"

# Shared variables needed by multiprocessing
queue = Manager().list()
result_queue = Manager().list()
diff_dict = Manager().dict()
row_diff_count = Value("I", 0)
lock = Lock()

# Set max number of rows up to which
# diff-tables will work
MAX_DIFF_ROWS = 10000
MIN_ALLOWED_BLOCK_SIZE = 1000
MAX_ALLOWED_BLOCK_SIZE = 100000
BLOCK_ROWS_DEFAULT = os.environ.get("ACE_BLOCK_ROWS", 10000)
MAX_CPU_RATIO_DEFAULT = os.environ.get("ACE_MAX_CPU_RATIO", 0.6)

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


def write_pg_dump(p_ip, p_db, p_port, p_prfx, p_schm, p_base_dir="/tmp"):
    out_file = get_dump_file_name(p_prfx, p_schm, p_base_dir)
    try:
        cmd = f"pg_dump -s -n {p_schm} -h {p_ip} -p {p_port} -d {p_db} > {out_file}"
        os.system(cmd)
    except Exception as e:
        util.exit_exception(e)
    return out_file


'''
Accepts a connection object and returns the version of spock installed

@param: conn - connection object
@return: float - version of spock installed

'''
def get_spock_version(conn):
    data = []
    sql = "SELECT spock.spock_version();"
    try:
        c = conn.cursor()
        c.execute(sql)
        data = c.fetchone()
        if data:
            return float(data[0])
    except Exception as e:
        fatal_error(e, sql, "get_spock_version()")

    return 0.0


def fix_schema(diff_file, sql1, sql2):
    newtable = False
    with open(diff_file) as diff_list:
        for i in diff_list.readlines():
            if re.search(r"\\,", i):
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


def parse_nodes(nodes) -> list:
    node_list = []
    if type(nodes) is str and nodes != "all":
        node_list = [s.strip() for s in nodes.split(",")]
    elif type(nodes) is not str:
        node_list = nodes

    if nodes != "all":
        rep_check = set(node_list)
        if len(rep_check) < len(node_list):
            util.message(
                "Ignoring duplicate node names",
                p_state="warning",
            )
            node_list = list(rep_check)
    
    return node_list


def schema_diff(cluster_name, nodes, schema_name):
    """Compare Postgres schemas on different cluster nodes"""

    util.message(f"## Validating cluster {cluster_name} exists")
    node_list = []
    try:
        node_list = parse_nodes(nodes)
    except ValueError as e:
        util.exit_message(
            f'Nodes should be a comma-separated list of nodenames. \
                E.g., --nodes="n1,n2". Error: {e}'
        )

    if len(node_list) > 3:
        util.exit_message(
            "schema-diff currently supports up to a three-way table comparison"
        )

    if nodes != "all" and len(node_list) == 1:
        util.exit_message("schema-diff needs at least two nodes to compare")

    util.check_cluster_exists(cluster_name)
    util.message(f"Cluster {cluster_name} exists", p_state="success")

    db, pg, node_info = cluster.load_json(cluster_name)

    cluster_nodes = []

    """
    Even though multiple databases are allowed, ACE will, for now,
    only take the first entry in the db list
    """
    database = db[0]
    database["db_name"] = database.pop("name")

    # Combine db and cluster_nodes into a single json
    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    for nd in cluster_nodes:
        if nodes == "all":
            node_list.append(nd["name"])

    sql1, sql2 = "", ""
    l_schema = schema_name
    file_list = []

    for nd in cluster_nodes:
        if nd["name"] in node_list:
            sql1 = write_pg_dump(
                nd["ip_address"], nd["db_name"], nd["port"], nd["name"], l_schema
            )
            file_list.append(sql1)

    if os.stat(file_list[0]).st_size == 0:
        util.exit_message(f"Schema {schema_name} does not exist on node {node_list[0]}")

    for n in range(1, len(file_list)):
        cmd = "diff " + file_list[0] + "  " + file_list[n] + " > /tmp/diff.txt"
        util.message("\n## Running # " + cmd + "\n")
        rc = os.system(cmd)
        if os.stat(file_list[n]).st_size == 0:
            util.exit_message(
                f"Schema {schema_name} does not exist on node {node_list[n]}"
            )
        if rc == 0:
            util.message(
                f"SCHEMAS ARE THE SAME- between {node_list[0]} and {node_list[n]} !!",
                p_state="success",
            )
        else:
            prRed(
                f"\u2718   SCHEMAS ARE NOT THE SAME- between {node_list[0]}"
                "and {node_list[n]}!!"
            )


def spock_diff(cluster_name, nodes):
    """Compare spock meta data setup on different cluster nodes"""
    node_list = []
    try:
        node_list = parse_nodes(nodes)
    except ValueError as e:
        util.exit_message(
            f'Nodes should be a comma-separated list of nodenames. \
                E.g., --nodes="n1,n2". Error: {e}'
        )

    if len(node_list) > 3:
        util.exit_message(
            "spock-diff currently supports up to a three-way table comparison"
        )

    if nodes != "all" and len(node_list) == 1:
        util.exit_message("spock-diff needs at least two nodes to compare")

    util.check_cluster_exists(cluster_name)
    util.message(f"Cluster {cluster_name} exists", p_state="success")

    db, pg, node_info = cluster.load_json(cluster_name)

    cluster_nodes = []
    """
    Even though multiple databases are allowed, ACE will, for now,
    only take the first entry in the db list
    """
    database = db[0]
    database["db_name"] = database.pop("name")

    # Combine db and cluster_nodes into a single json
    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    conn_list = {}

    try:
        for nd in cluster_nodes:
            if nodes == "all":
                node_list.append(nd["name"])

            psql_conn = psycopg.connect(
                dbname=nd["db_name"],
                user=nd["username"],
                password=nd["password"],
                host=nd["ip_address"],
                port=nd.get("port", 5432),
                row_factory=dict_row,
            )
            conn_list[nd["name"]] = psql_conn

    except Exception as e:
        util.exit_message("Error in spock_diff() Getting Connections:" + str(e), 1)
    
    for nd in node_list:
        if nd not in conn_list.keys():
            util.exit_message(f"Specified nodename \"{nd}\" not present in cluster", 1)

    compare_spock = []
    print("\n")

    for cluster_node in cluster_nodes:
        cur = conn_list[cluster_node["name"]].cursor()
        if cluster_node["name"] not in node_list:
            continue
        diff_spock = {}
        hints = []
        print(" Spock - Config " + cluster_node["name"])
        print("~~~~~~~~~~~~~~~~~~~~~~~~~")
        prCyan("Node:")
        sql = """
        SELECT n.node_id, n.node_name, n.location, n.country,
           s.sub_id, s.sub_name, s.sub_enabled, s.sub_replication_sets
           FROM spock.node n LEFT OUTER JOIN spock.subscription s
           ON s.sub_target=n.node_id WHERE s.sub_name IS NOT NULL;
        """

        cur.execute(sql)
        node_info = cur.fetchall()

        print("  " + node_info[0]["node_name"])
        diff_spock["node"] = node_info[0]["node_name"]

        prCyan("  Subscriptions:")

        diff_spock["subscriptions"] = []
        for node in node_info:
            diff_sub = {}
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
                diff_spock["subscriptions"].append(diff_sub)

        # Query gets each table by which rep set they are in, values in each rep set are alphabetized
        sql = """
        SELECT set_name, string_agg(nspname || '.' || relname, '   ') as relname
        FROM (
            SELECT set_name, nspname, relname
            FROM spock.tables
            ORDER BY set_name, nspname, relname
        ) subquery
        GROUP BY set_name ORDER BY set_name;
        """

        cur.execute(sql)
        table_info = cur.fetchall()
        diff_spock["rep_set_info"] = []
        prCyan("Tables in RepSets:")
        if table_info == []:
            hints.append("Hint: No tables in database")
        for table in table_info:
            if table["set_name"] is None:
                print(" - Not in a replication set")
                hints.append(
                    "Hint: Tables not in replication set might not have primary keys,"
                    " or you need to run repset-add-table"
                )
            else:
                print(" - " + table["set_name"])

            diff_spock["rep_set_info"].append({table["set_name"]: table["relname"]})
            print("   - " + table["relname"])

        compare_spock.append(diff_spock)

        for hint in hints:
            prRed(hint)
        print("\n")

    print(" Spock - Diff")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~")
    for n in range(1, len(compare_spock)):
        if compare_spock[0]["rep_set_info"] == compare_spock[n]["rep_set_info"]:
            util.message(
                f"   Replication Rules are the same for {node_list[0]} and {node_list[n]}!!",
                p_state="success",
            )
        else:
            prRed(
                f"\u2718   Difference in Replication Rules between {node_list[0]} and {node_list[n]}"
            )


def run_query(worker_state, host, query):
    cur = worker_state[host]
    cur.execute(query)
    results = cur.fetchall()
    return results


def init_db_connection(shared_objects, worker_state):
    db, pg, node_info = cluster.load_json(shared_objects["cluster_name"])

    cluster_nodes = []
    database = shared_objects["database"]

    # Combine db and cluster_nodes into a single json
    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    for node in cluster_nodes:
        conn_str = f"dbname = {node['db_name']}      \
                    user={node['username']}          \
                    password={node['password']}   \
                    host={node['ip_address']}   \
                    port={node.get('port', 5432)}"

        worker_state[node["name"]] = psycopg.connect(conn_str).cursor()


def compare_checksums(shared_objects, worker_state, pkey1, pkey2):
    global row_diff_count

    if row_diff_count.value >= MAX_DIFF_ROWS:
        return

    p_key = shared_objects["p_key"]
    schema_name = shared_objects["schema_name"]
    table_name = shared_objects["table_name"]
    node_list = shared_objects["node_list"]
    cols = shared_objects["cols_list"]
    simple_primary_key = shared_objects["simple_primary_key"]

    where_clause = []

    if simple_primary_key:
        if pkey1 is not None:
            where_clause.append(
                sql.SQL("{p_key} >= {pkey1}").format(
                    p_key=sql.Identifier(p_key), pkey1=sql.Literal(pkey1)
                )
            )
        if pkey2 is not None:
            where_clause.append(
                sql.SQL("{p_key} < {pkey2}").format(
                    p_key=sql.Identifier(p_key), pkey2=sql.Literal(pkey2)
                )
            )
    else:
        """
        This is a slightly more complicated case since we have to split up
        the primary key and compare them with split values of pkey1 and pkey2
        """

        if pkey1 is not None:
            where_clause.append(
                sql.SQL("({p_key}) >= ({pkey1})").format(
                    p_key=sql.SQL(", ").join(
                        [sql.Identifier(col.strip()) for col in p_key.split(",")]
                    ),
                    pkey1=sql.SQL(", ").join([sql.Literal(val) for val in pkey1]),
                )
            )

        if pkey2 is not None:
            where_clause.append(
                sql.SQL("({p_key}) < ({pkey2})").format(
                    p_key=sql.SQL(", ").join(
                        [sql.Identifier(col.strip()) for col in p_key.split(",")]
                    ),
                    pkey2=sql.SQL(", ").join([sql.Literal(val) for val in pkey2]),
                )
            )
    
    if simple_primary_key:
        hash_sql = sql.SQL(
            "SELECT md5(cast(array_agg(t.* ORDER BY {p_key}) AS text)) FROM"
            "(SELECT * FROM {table_name} WHERE {where_clause}) t"
        ).format(
            p_key=sql.Identifier(p_key),
            table_name=sql.SQL("{}.{}").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
            ),
            where_clause=sql.SQL(" AND ").join(where_clause),
        )
    else:
        hash_sql = sql.SQL(
            "SELECT md5(cast(array_agg(t.* ORDER BY {p_key}) AS text)) FROM"
            "(SELECT * FROM {table_name} WHERE {where_clause}) t"
        ).format(
            p_key=sql.SQL(", ").join(
                [sql.Identifier(col.strip()) for col in p_key.split(",")]
            ),
            table_name=sql.SQL("{}.{}").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
            ),
            where_clause=sql.SQL(" AND ").join(where_clause),
        )

    block_sql = sql.SQL("SELECT * FROM {table_name} WHERE {where_clause}").format(
        table_name=sql.SQL("{}.{}").format(
            sql.Identifier(schema_name),
            sql.Identifier(table_name),
        ),
        where_clause=sql.SQL(" AND ").join(where_clause),
    )

    node_pairs = combinations(node_list, 2)

    block_result = {}
    block_result["offset"] = f"{pkey1}-{pkey2}"
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
        except Exception as e:
            print(f"query = {hash_sql.as_string(worker_state[host1])}", e)
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
            except Exception as e:
                print(f"query = {block_sql}", e)
                result_queue.append(BLOCK_ERROR)
                return

            # Transform all elements in t1_result and t2_result into strings before
            # consolidating them into a set
            # TODO: Test and add support for different datatypes here
            t1_result = [
                tuple(
                    str(x) if not isinstance(x, list) else str(sorted(x)) for x in row
                )
                for row in t1_result
            ]
            t2_result = [
                tuple(
                    str(x) if not isinstance(x, list) else str(sorted(x)) for x in row
                )
                for row in t2_result
            ]

            # Collect results into OrderedSets for comparison
            t1_set = OrderedSet(t1_result)
            t2_set = OrderedSet(t2_result)

            t1_diff = t1_set - t2_set
            t2_diff = t2_set - t1_set

            node_pair_key = f"{host1}/{host2}"

            if node_pair_key not in diff_dict:
                diff_dict[node_pair_key] = {}

            with lock:
                if len(t1_diff) > 0 or len(t2_diff) > 0:
                    temp_dict = {}
                    if host1 in diff_dict[node_pair_key]:
                        temp_dict[host1] = diff_dict[node_pair_key][host1]
                    else:
                        temp_dict[host1] = []
                    if host2 in diff_dict[node_pair_key]:
                        temp_dict[host2] = diff_dict[node_pair_key][host2]
                    else:
                        temp_dict[host2] = []

                    temp_dict[host1] += [dict(zip(cols, row)) for row in t1_diff]
                    temp_dict[host2] += [dict(zip(cols, row)) for row in t2_diff]

                    diff_dict[node_pair_key] = temp_dict

            with row_diff_count.get_lock():
                row_diff_count.value += max(len(t1_diff), len(t2_diff))

            if row_diff_count.value >= MAX_DIFF_ROWS:
                result_queue.append(MAX_DIFF_EXCEEDED)
                return
            else:
                result_queue.append(BLOCK_MISMATCH)

        else:
            result_queue.append(BLOCK_OK)


def table_diff(
    cluster_name,
    table_name,
    dbname=None,
    block_rows=BLOCK_ROWS_DEFAULT,
    max_cpu_ratio=MAX_CPU_RATIO_DEFAULT,
    output="json",
    nodes="all",
    diff_file=None,
):
    """Efficiently compare tables across cluster using checksums and blocks of rows"""
    
    if type(block_rows) is str:
        try:
            block_rows = int(block_rows)
        except Exception:
            util.exit_message("Invalid values for ACE_BLOCK_ROWS")
    elif type(block_rows) is not int:
        util.exit_message("Invalid value type for ACE_BLOCK_ROWS")
    
    # Capping max block size here to prevent the hash function from taking forever
    if block_rows > MAX_ALLOWED_BLOCK_SIZE:
        util.exit_message(f"Block row size should be <= {MAX_ALLOWED_BLOCK_SIZE}")
    if block_rows < MIN_ALLOWED_BLOCK_SIZE:
        util.exit_message(f"Block row size should be >= {MIN_ALLOWED_BLOCK_SIZE}")

    if type(max_cpu_ratio) is int:
        max_cpu_ratio = float(max_cpu_ratio)
    elif type(max_cpu_ratio) is str:
        try:
            max_cpu_ratio = float(max_cpu_ratio)
        except Exception:
            util.exit_message("Invalid values for ACE_MAX_CPU_RATIO")
    elif type(max_cpu_ratio) is not float:
        util.exit_message("Invalid value type for ACE_MAX_CPU_RATIO")

    if max_cpu_ratio > 1.0 or max_cpu_ratio < 0.0:
        util.exit_message("Invalid value range for ACE_MAX_CPU_RATIO or --max_cpu_ratio")

    if output not in ["csv", "json"]:
        util.exit_message(
            "table-diff currently supports only csv and json output formats"
        )

    node_list = []
    try:
        node_list = parse_nodes(nodes)
    except ValueError as e:
        util.exit_message(
            f'Nodes should be a comma-separated list of nodenames. \
                E.g., --nodes="n1,n2". Error: {e}'
        )

    if len(node_list) > 3:
        util.exit_message(
            "table-diff currently supports up to a three-way table comparison"
        )

    if nodes != "all" and len(node_list) == 1:
        util.exit_message("table-diff needs at least two nodes to compare")

    util.check_cluster_exists(cluster_name)
    util.message(f"Cluster {cluster_name} exists", p_state="success")

    nm_lst = table_name.split(".")
    if len(nm_lst) != 2:
        util.exit_message(f"TableName {table_name} must be of form 'schema.table_name'")
    l_schema = nm_lst[0]
    l_table = nm_lst[1]

    db, pg, node_info = cluster.load_json(cluster_name)

    cluster_nodes = []
    database = {}

    if dbname:
        for db_entry in db:
            if db_entry["name"] == dbname:
                database = db_entry
                break
    else:
        database = db[0]

    if not database:
        util.exit_message(f"Database '{dbname}' not found in cluster '{cluster_name}'")

    database["db_name"] = database.pop("name")

    # Combine db and cluster_nodes into a single json
    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    if nodes != "all" and len(node_list) > 1:
        for n in node_list:
            if not any(filter(lambda x: x["name"] == n, cluster_nodes)):
                util.exit_message("Specified nodenames not present in cluster")

    conn_list = []

    try:
        for nd in cluster_nodes:
            if nodes == "all":
                node_list.append(nd["name"])

            if (node_list and nd["name"] in node_list) or (not node_list):
                psql_conn = psycopg.connect(
                    dbname=nd["db_name"],
                    user=nd["username"],
                    password=nd["password"],
                    host=nd["ip_address"],
                    port=nd.get("port", 5432),
                )
                conn_list.append(psql_conn)

    except Exception as e:
        util.exit_message("Error in table_diff() Getting Connections:" + str(e), 1)

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

    simple_primary_key = True
    if len(key.split(",")) > 1:
        simple_primary_key = False

    row_count = 0
    total_rows = 0
    offsets = []

    diff_json = None
    conn_with_max_rows = None

    if not diff_file:
        for conn in conn_list:
            rows = get_row_count(conn, l_schema, l_table)
            total_rows += rows
            if rows > row_count:
                row_count = rows
                conn_with_max_rows = conn
    else:
        diff_json = json.loads(open(diff_file, "r").read())
        block_rows = diff_json["block_size"]

        for diff in diff_json["diffs"]:
            offsets.append(diff["offset"])

        row_count = block_rows * len(offsets)
        total_rows = row_count

    pkey_offsets = []

    if not conn_with_max_rows:
        util.message(
            "ALL TABLES ARE EMPTY",
            p_state="warning",
        )
        return

    # Use conn_with_max_rows to get the first and last primary key values
    # of every block row. Repeat until we no longer have any more rows.
    # Store results in pkey_offsets.

    if simple_primary_key:
        pkey_sql = sql.SQL("SELECT {key} FROM {table_name} ORDER BY {key}").format(
            key=sql.Identifier(key),
            table_name=sql.SQL("{}.{}").format(
                sql.Identifier(l_schema), sql.Identifier(l_table)
            ),
        )
    else:
        pkey_sql = sql.SQL("SELECT {key} FROM {table_name} ORDER BY {key}").format(
            key=sql.SQL(", ").join([sql.Identifier(col) for col in key.split(",")]),
            table_name=sql.SQL("{}.{}").format(
                sql.Identifier(l_schema), sql.Identifier(l_table)
            ),
        )

    def get_pkey_offsets(conn, pkey_sql, block_rows):
        pkey_offsets = []
        cur = conn.cursor()
        cur.execute(pkey_sql)
        rows = cur.fetchmany(block_rows)

        if simple_primary_key:
            rows[:] = [str(x[0]) for x in rows]
            pkey_offsets.append((None, str(rows[0])))
            prev_min_offset = str(rows[0])
            prev_max_offset = str(rows[-1])
        else:
            rows[:] = [tuple(str(i) for i in x) for x in rows]
            pkey_offsets.append((None, rows[0]))
            prev_min_offset = rows[0]
            prev_max_offset = rows[-1]

        while rows:
            rows = cur.fetchmany(block_rows)
            if simple_primary_key:
                rows[:] = [str(x[0]) for x in rows]
            else:
                rows[:] = [tuple(str(i) for i in x) for x in rows]

            if not rows:
                if prev_max_offset != prev_min_offset:
                    pkey_offsets.append((prev_min_offset, prev_max_offset))
                pkey_offsets.append((prev_max_offset, None))
                break

            curr_min_offset = rows[0]
            pkey_offsets.append((prev_min_offset, curr_min_offset))
            prev_min_offset = curr_min_offset
            prev_max_offset = rows[-1]

        cur.close()
        return pkey_offsets

    future = ThreadPoolExecutor().submit(
        get_pkey_offsets, conn_with_max_rows, pkey_sql, block_rows
    )
    pkey_offsets = future.result()

    total_blocks = row_count // block_rows
    total_blocks = total_blocks if total_blocks > 0 else 1
    cpus = cpu_count()
    max_procs = int(cpus * max_cpu_ratio * 2) if cpus > 1 else 1

    # If we don't have enough blocks to keep all CPUs busy, use fewer processes
    procs = max_procs if total_blocks > max_procs else total_blocks

    start_time = datetime.now()

    """
    Generate offsets for each process to work on.
    We go up to the max rows among all nodes because we want our set difference logic
    to capture diffs even if rows are absent in one node
    """
    if not diff_file:
        offsets = [x for x in range(0, row_count + 1, block_rows)]

    cols_list = cols.split(",")
    cols_list = [col for col in cols_list if not col.startswith("_Spock_")]

    # Shared variables needed by all workers
    shared_objects = {
        "cluster_name": cluster_name,
        "database": database,
        "node_list": node_list,
        "schema_name": l_schema,
        "table_name": l_table,
        "cols_list": cols_list,
        "p_key": key,
        "block_rows": block_rows,
        "simple_primary_key": simple_primary_key,
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
            pkey_offsets,
            worker_init=init_db_connection,
            progress_bar=True,
            iterable_len=len(pkey_offsets),
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

        for node_pair in diff_dict.keys():
            node1, node2 = node_pair.split("/")
            diff_count = max(
                len(diff_dict[node_pair][node1]), len(diff_dict[node_pair][node2])
            )
            util.message(
                f"FOUND {diff_count} DIFFS BETWEEN {node1} AND {node2}",
                p_state="warning",
            )

        print()

        if output == "json":
            write_diffs_json(block_rows)

        elif output == "csv":
            write_diffs_csv()

    else:
        util.message("TABLES MATCH OK\n", p_state="success")

    run_time = util.round_timedelta(datetime.now() - start_time).total_seconds()
    run_time_str = f"{run_time:.2f}"

    print()

    util.message(
        f"TOTAL ROWS CHECKED = {total_rows}\nRUN TIME = {run_time_str} seconds",
        p_state="info",
    )


def write_diffs_json(block_rows):
    dirname = datetime.now().astimezone(None).strftime("%Y-%m-%d_%H:%M:%S")

    if not os.path.exists("diffs"):
        os.mkdir("diffs")

    dirname = os.path.join("diffs", dirname)
    os.mkdir(dirname)

    filename = os.path.join(dirname, "diff.json")

    with open(filename, "w") as f:
        f.write(json.dumps(dict(diff_dict), default=str))

    util.message(
        f"Diffs written out to" f" {util.set_colour(filename, 'blue')}",
        p_state="info",
    )


# TODO: Come up with better naming convention for diff files
def write_diffs_csv():
    import pandas as pd

    dirname = datetime.now().astimezone(None).strftime("%Y-%m-%d_%H:%M:%S")

    if not os.path.exists("diffs"):
        os.mkdir("diffs")

    dirname = os.path.join("diffs", dirname)
    os.mkdir(dirname)

    for node_pair in diff_dict.keys():
        node1, node2 = node_pair.split("/")
        node_pair_str = f"{node1}__{node2}"
        node_pair_dir = os.path.join(dirname, node_pair_str)

        # Create directory for node pair if it doesn't exist
        if not os.path.exists(node_pair_dir):
            os.mkdir(node_pair_dir)

        t1_write_path = os.path.join(node_pair_dir, node1 + ".csv")
        t2_write_path = os.path.join(node_pair_dir, node2 + ".csv")

        df1 = pd.DataFrame.from_dict(diff_dict[node_pair][node1])
        df2 = pd.DataFrame.from_dict(diff_dict[node_pair][node2])

        df1.to_csv(t1_write_path, header=True, index=False)
        df2.to_csv(t2_write_path, header=True, index=False)
        diff_file_name = os.path.join(dirname, f"{node_pair_str}/out.diff")

        t1_write_path = os.path.join(dirname, node_pair_str, node1 + ".csv")
        t2_write_path = os.path.join(dirname, node_pair_str, node2 + ".csv")

        cmd = f"diff -u {t1_write_path} {t2_write_path} | ydiff > {diff_file_name}"
        subprocess.check_output(cmd, shell=True)

        util.message(
            f"DIFFS BETWEEN {util.set_colour(node1, 'blue')}"
            f" AND {util.set_colour(node2, 'blue')}: {diff_file_name}",
            p_state="info",
        )


def table_rerun(cluster_name, diff_file, table_name, dbname=None):
    """Re-run differences on the results of a recent table-diff"""

    if not os.path.exists(diff_file):
        util.exit_message(f"Diff file {diff_file} not found")

    util.check_cluster_exists(cluster_name)
    util.message(f"Cluster {cluster_name} exists", p_state="success")

    nm_lst = table_name.split(".")
    if len(nm_lst) != 2:
        util.exit_message(f"TableName {table_name} must be of form 'schema.table_name'")
    l_schema = nm_lst[0]
    l_table = nm_lst[1]

    db, pg, node_info = cluster.load_json(cluster_name)

    cluster_nodes = []
    database = {}

    if dbname:
        for db_entry in db:
            if db_entry["name"] == dbname:
                database = db_entry
                break
    else:
        database = db[0]

    if not database:
        util.exit_message(f"Database '{dbname}' not found in cluster '{cluster_name}'")

    database["db_name"] = database.pop("name")

    # Combine db and cluster_nodes into a single json
    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    conn_list = {}

    try:
        for nd in cluster_nodes:
            conn_list[nd["name"]] = psycopg.connect(
                dbname=nd["db_name"],
                user=nd["username"],
                password=nd["password"],
                host=nd["ip_address"],
                port=nd.get("port", 5432),
            )
    except Exception as e:
        util.exit_message("Error in diff_tbls() Getting Connections:" + str(e), 1)

    util.message("Connections successful to nodes in cluster", p_state="success")

    cols = None
    key = None

    for node, conn in conn_list.items():
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

    start_time = datetime.now()

    try:
        diff_json = json.loads(open(diff_file, "r").read())
    except Exception:
        util.exit_message("Could not load diff file as JSON")

    try:
        if any([set(list(diff_json[k].keys())) != set(k.split('/')) for k in diff_json.keys()]):
            util.exit_message("Contents of diff file improperly formatted")
    except Exception:
        util.exit_message("Contents of diff file improperly formatted")

    """
    We first need to identify the tuples we need to recheck.
    For that, we iterate through the diffs and get the primary key values.
    However, if the primary key is a composite key, we need to get all the columns,
    and then use all of them to extract the respective tuples from the database

    We need to collect a maximal set of rows for each pair of nodes. E.g., if we have
    7 rows in node A and 5 rows in node B, we need to collect a union of both those
    sets of rows. This is because we want to capture the case where a row is missing
    and the case where a row is present but has different values.

    Our data structure that captures this is a dictionary of the form:
    {
        "node1/node2": [[key1, key2, key3], [key3, key4, key5] ...],
        "node1/node3": [[key1, key2, key3], [key3, key4, key5] ...],
        "node2/node3": [[key1, key2, key3], [key3, key4, key5] ...]
    }
    """

    diff_values = {}
    simple_primary_key = True

    if len(key.split(",")) > 1:
        # We have a composite key situation here
        key_cols = key.split(",")
        simple_primary_key = False

        node_pairs = diff_json.keys()

        for node_pair in node_pairs:
            if node_pair not in diff_values:
                diff_values[node_pair] = set()

            for node in node_pair.split("/"):
                for row in diff_json[node_pair][node]:
                    diff_values[node_pair].add(tuple(row[col] for col in key_cols))
    else:
        # We have a single column primary key
        node_pairs = diff_json.keys()

        for node_pair in node_pairs:
            if node_pair not in diff_values:
                diff_values[node_pair] = set()

            for node in node_pair.split("/"):
                for row in diff_json[node_pair][node]:
                    diff_values[node_pair].add(row[key])

    # Transform the set of tuples into a list of tuples
    for node_pair in diff_values.keys():
        diff_values[node_pair] = list(diff_values[node_pair])

    cols_list = cols.split(",")
    cols_list = [col for col in cols_list if not col.startswith("_Spock_")]

    def run_query(cur, query):
        cur.execute(query)
        results = cur.fetchall()
        return results

    diff_rerun = {}
    diffs_found = False

    for node_pair_key, values in diff_values.items():
        node1, node2 = node_pair_key.split("/")

        node1_cur = conn_list[node1].cursor()
        node2_cur = conn_list[node2].cursor()

        node1_set = OrderedSet()
        node2_set = OrderedSet()

        if simple_primary_key:
            for index in values:
                sql = f"""
                SELECT *
                FROM {table_name}
                WHERE "{key}" = '{index}';
                """

                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(run_query, node1_cur, sql),
                        executor.submit(run_query, node2_cur, sql),
                    ]

                    t1_result, t2_result = [f.result() for f in futures]
                    t1_result = t1_result[0] if t1_result else None
                    t2_result = t2_result[0] if t2_result else None

                    if t1_result is not None and t2_result is not None:
                        t1_result = tuple(
                            str(x) if not isinstance(x, list) else str(sorted(x))
                            for x in t1_result
                        )
                        t2_result = tuple(
                            str(x) if not isinstance(x, list) else str(sorted(x))
                            for x in t2_result
                        )

                        node1_set.add(t1_result)
                        node2_set.add(t2_result)
        else:
            for indices in values:
                sql = f"""
                SELECT *
                FROM {table_name}
                WHERE
                """

                ctr = 0
                for k in key.split(","):
                    sql += f" \"{k}\" = '{indices[ctr]}' AND"
                    ctr += 1

                # Get rid of the last "AND" and add a semicolon
                sql = sql[:-3] + ";"

                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(run_query, node1_cur, sql),
                        executor.submit(run_query, node2_cur, sql),
                    ]

                    t1_result, t2_result = [f.result() for f in futures]
                    t1_result = t1_result[0] if t1_result else None
                    t2_result = t2_result[0] if t2_result else None

                    if t1_result is not None and t2_result is not None:
                        t1_result = tuple(
                            str(x) if not isinstance(x, list) else str(sorted(x))
                            for x in t1_result
                        )
                        t2_result = tuple(
                            str(x) if not isinstance(x, list) else str(sorted(x))
                            for x in t2_result
                        )

                        node1_set.add(t1_result)
                        node2_set.add(t2_result)

        node1_diff = node1_set - node2_set
        node2_diff = node2_set - node1_set

        if len(node1_diff) > 0 or len(node2_diff) > 0:
            diffs_found = True
            diff_rerun[node_pair_key] = {
                node1: [dict(zip(cols_list, row)) for row in node1_diff],
                node2: [dict(zip(cols_list, row)) for row in node2_diff],
            }

    dirname = datetime.now().astimezone(None).strftime("%Y-%m-%d_%H:%M:%S")

    if not os.path.exists("diffs"):
        os.mkdir("diffs")

    dirname = os.path.join("diffs", dirname)
    os.mkdir(dirname)

    filename = os.path.join(dirname, "diff.json")

    with open(filename, "w") as f:
        f.write(json.dumps(diff_rerun, default=str))

    print()

    if diffs_found:
        util.message(
            f"FOUND DIFFS BETWEEN NODES: written out to {util.set_colour(filename, 'blue')}",
            p_state="warning",
        )
    else:
        util.message("TABLES MATCH OK\n", p_state="success")

    print()

    util.message("RUN TIME = " + str(util.round_timedelta(datetime.now() - start_time)))


def table_repair(
    cluster_name, diff_file, source_of_truth, table_name, dbname=None, dry_run=False
):
    """Apply changes from a table-diff source of truth to destination table"""
    import pandas as pd

    # Check if diff_file exists on disk
    if not os.path.exists(diff_file):
        util.exit_message(f"Diff file {diff_file} does not exist")
    
    if type(dry_run) is int:
        if dry_run < 0 or dry_run > 1:
            util.exit_message("Dry run should be True (1) or False (0)")
        dry_run = bool(dry_run)
    
    if type(dry_run) is not bool:
        util.exit_message("Dry run should be True (1) or False (0)")

    util.check_cluster_exists(cluster_name)
    util.message(f"Cluster {cluster_name} exists", p_state="success")

    nm_lst = table_name.split(".")
    if len(nm_lst) != 2:
        util.exit_message(f"TableName {table_name} must be of form 'schema.table_name'")

    l_schema = nm_lst[0]
    l_table = nm_lst[1]

    db, pg, node_info = cluster.load_json(cluster_name)

    cluster_nodes = []
    database = {}

    if dbname:
        for db_entry in db:
            if db_entry["name"] == dbname:
                database = db_entry
                break
    else:
        database = db[0]

    if not database:
        util.exit_message(f"Database '{dbname}' not found in cluster '{cluster_name}'")

    database["db_name"] = database.pop("name")

    # Combine db and cluster_nodes into a single json
    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    # Check to see if source_of_truth node is present in cluster
    if not any(node.get("name") == source_of_truth for node in cluster_nodes):
        util.exit_message(
            f"Source of truth node {source_of_truth} not present in cluster"
        )

    start_time = datetime.now()

    conns = {}
    try:
        for nd in cluster_nodes:
            conns[nd["name"]] = psycopg.connect(
                dbname=nd["db_name"],
                user=nd["username"],
                password=nd["password"],
                host=nd["ip_address"],
                port=nd.get("port", 5432),
            )

    except Exception as e:
        util.exit_message("Error in diff_tbls() Getting Connections:" + str(e), 1)

    util.message("Connections successful to nodes in cluster", p_state="success")

    cols = None
    key = None

    for conn in conns.values():
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

    try:
        diff_json = json.loads(open(diff_file, "r").read())
    except Exception:
        util.exit_message("Could not load diff file as JSON")

    try:
        if any([set(list(diff_json[k].keys())) != set(k.split('/')) for k in diff_json.keys()]):
            util.exit_message("Contents of diff file improperly formatted")
    except Exception:
        util.exit_message("Contents of diff file improperly formatted")

    true_df = pd.DataFrame()

    """
    The structure of the diff_json is as follows:
    {
        "node1/node2": {
            "node1": [row1, row2, row3],
            "node2": [row1, row2, row3]
        },
        "node1/node3": {
            "node1": [row1, row2, row3],
            "node3": [row1, row2, row3]
        }
    }

    true_rows extracts all rows from the source of truth node across all node diffs
    and dedupes them.
    We use true_rows if the node_pair does not contain the source of truth node.
    This case can happen only when another node has the same rows as the source of
    truth node, but the third node has some differences. The proof of this is trivial,
    and is left as an exercise to the reader.

    Strategy for repair:
    1.  Extract all rows from source of truth node across all node_pairs
        and store them in true_rows.
    2.  Check to see if the node_pair has the source of truth node.
        If yes, then use rows from the source of truth node in the node_pair.
        Otherwise, use true_rows obtained in step 1. At the end of this step,
        true_rows either has node-specific diffs or all diffs--as computed in step 1.
    3.  We could have four different situations when checking true_rows
        against other nodes:
        a.  Rows are present in source of truth node but not in other nodes.
        b.  Rows are present in source of truth node and in other nodes but have
            different values.
        c.  Rows are present in other nodes but not in source of truth node.
        d.  Both source of truth node and the other node have rows, but some need to be
            inserted, some deleted and some updated.

    4.  Here is how we handle each of these situations:
        a.  We simply insert the rows into the other nodes.
        b.  We update the rows in the other nodes with the values from the source of
            truth node.
        c.  We delete the rows from the other nodes.
        d.  We insert/update/delete rows in the other nodes as needed.

    5.  But how do we know which rows to insert/update/delete? We need to do some
        set operations to figure this out. We will call the source of truth node
        as the ST node and the other node as the 'D' (divergent) node. We perform
        these set operations using the primary key of the table.
        a.  Rows to insert in D node: ST node - D node
        b.  Rows to update in D node: ST node intersection D node
        c.  Rows to delete in D node: D node - ST node

    """

    # Gather all rows from source of truth node across all node pairs
    true_rows = [
        entry
        for node_pair in diff_json.keys()
        for entry in diff_json[node_pair].get(source_of_truth, [])
    ]

    # Collect all rows from our source of truth node and dedupe
    true_df = pd.concat([true_df, pd.DataFrame(true_rows)], ignore_index=True)
    true_df.drop_duplicates(inplace=True)

    if not true_df.empty:
        # Convert them to a list of tuples after deduping
        true_rows = [
            tuple(str(x) for x in row) for row in true_df.to_records(index=False)
        ]

    print()

    # XXX: Fix dry run later
    nodes_to_repair = ",".join(
        [nd["name"] for nd in cluster_nodes if nd["name"] != source_of_truth]
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
    # Remove metadata columsn "_Spock_CommitTS_" and "_Spock_CommitOrigin_"
    # from cols_list
    cols_list = [col for col in cols_list if not col.startswith("_Spock_")]
    simple_primary_key = True
    keys_list = []

    if len(key.split(",")) > 1:
        simple_primary_key = False
        keys_list = key.split(",")

    total_upserted = {}
    total_deleted = {}

    for node_pair in diff_json.keys():
        node1, node2 = node_pair.split("/")

        true_rows = (
            [
                tuple(str(x) for x in entry.values())
                for entry in diff_json[node_pair][source_of_truth]
            ]
            if source_of_truth in [node1, node2]
            else true_rows
        )

        divergent_rows = []
        divergent_node = None

        if node1 == source_of_truth:
            divergent_rows = [
                tuple(str(x) for x in row.values())
                for row in diff_json[node_pair][node2]
            ]
            divergent_node = node2
        elif node2 == source_of_truth:
            divergent_rows = [
                tuple(str(x) for x in row.values())
                for row in diff_json[node_pair][node1]
            ]
            divergent_node = node1
        else:
            """
            It's possible that only one node or both nodes have divergent rows.
            Instead of attempting to fix one or both nodes here and then
            skipping them later, it's probably best to ignore all differences
            between divergent nodes and continue with the next node pair.
            """
            continue

        true_set = OrderedSet(true_rows)
        divergent_set = OrderedSet(divergent_rows)

        rows_to_upsert = true_set - divergent_set  # Set difference
        rows_to_delete = divergent_set - true_set

        rows_to_upsert_json = []
        rows_to_delete_json = []

        if rows_to_upsert:
            rows_to_upsert_json = [dict(zip(cols_list, row)) for row in rows_to_upsert]
        if rows_to_delete:
            rows_to_delete_json = [dict(zip(cols_list, row)) for row in rows_to_delete]

        filtered_rows_to_delete = []

        upsert_lookup = {}

        """
        We need to construct a lookup table for the upserts.
        This is because we need to delete only those rows from
        the divergent node that are not a part of the upserts
        """
        for row in rows_to_upsert_json:
            if simple_primary_key:
                upsert_lookup[row[key]] = 1
            else:
                upsert_lookup[tuple(row[col] for col in keys_list)] = 1

        for entry in rows_to_delete_json:
            if simple_primary_key:
                if entry[key] in upsert_lookup:
                    continue
            else:
                if tuple(entry[col] for col in keys_list) in upsert_lookup:
                    continue

            filtered_rows_to_delete.append(entry)

        if divergent_node not in total_upserted:
            total_upserted[divergent_node] = len(rows_to_upsert_json)

        if divergent_node not in total_deleted:
            total_deleted[divergent_node] = len(filtered_rows_to_delete)

        delete_keys = []

        if rows_to_delete:
            if simple_primary_key:
                delete_keys = tuple((row[key],) for row in filtered_rows_to_delete)
            else:
                delete_keys = tuple(
                    tuple(row[col] for col in keys_list)
                    for row in filtered_rows_to_delete
                )

        """
        Here we are constructing an UPSERT query from true_rows and
        applying it to all nodes
        """
        if simple_primary_key:
            update_sql = f"""
            INSERT INTO {table_name}
            VALUES ({','.join(['%s'] * len(cols_list))})
            ON CONFLICT ("{key}") DO UPDATE SET
            """
        else:
            update_sql = f"""
            INSERT INTO {table_name}
            VALUES ({','.join(['%s'] * len(cols_list))})
            ON CONFLICT
            ({','.join(['"' + col + '"' for col in keys_list])}) DO UPDATE SET
            """

        for col in cols_list:
            update_sql += f'"{col}" = EXCLUDED."{col}", '

        update_sql = update_sql[:-2] + ";"

        delete_sql = None

        if simple_primary_key:
            delete_sql = f"""
            DELETE FROM {table_name}
            WHERE "{key}" = %s;
            """
        else:
            delete_sql = f"""
            DELETE FROM {table_name}
            WHERE
            """

            for k in keys_list:
                delete_sql += f' "{k}" = %s AND'

            delete_sql = delete_sql[:-3] + ";"

        conn = conns[divergent_node]
        cur = conn.cursor()
        spock_version = get_spock_version(conn)

        # FIXME: Do not use harcoded version numbers
        # Read required version numbers from a config file
        if spock_version >= 4.0:
            cur.execute("SELECT spock.repair_mode(true);")

        if rows_to_upsert:
            upsert_tuples = [tuple(row.values()) for row in rows_to_upsert_json]

            # Performing the upsert
            cur.executemany(update_sql, upsert_tuples)

        if delete_keys:
            # Performing the deletes
            if len(delete_keys) > 0:
                cur.executemany(delete_sql, delete_keys)

        if spock_version >= 4.0:
            cur.execute("SELECT spock.repair_mode(false);")

        conn.commit()

    run_time = util.round_timedelta(datetime.now() - start_time).total_seconds()
    run_time_str = f"{run_time:.2f}"

    util.message(
        f"Successfully applied diffs to {table_name} in cluster {cluster_name}\n",
        p_state="success",
    )

    util.message("*** SUMMARY ***\n", p_state="info")

    for node in total_upserted.keys():
        util.message(
            f"{node} UPSERTED = {total_upserted[node]} rows",
            p_state="info",
        )

    print()

    for node in total_deleted.keys():
        util.message(
            f"{node} DELETED = {total_deleted[node]} rows",
            p_state="info",
        )

    print()

    util.message(
        f"RUN TIME = {run_time_str} seconds",
        p_state="info",
    )

    print()

    if spock_version < 4.0:
        util.message(
            "WARNING: Unable to pause/resume replication during repair due to"
            "an older spock version. Please do a manual check as repair may"
            "have caused further divergence",
            p_state="warning",
        )


def repset_diff(
    cluster_name,
    repset_name,
    dbname=None,
    block_rows=BLOCK_ROWS_DEFAULT,
    max_cpu_ratio=MAX_CPU_RATIO_DEFAULT,
    output="json",
    nodes="all",
):
    """Loop thru a replication-sets tables and run table-diff on them"""

    if type(block_rows) is str:
        try:
            block_rows = int(block_rows)
        except Exception:
            util.exit_message("Invalid values for ACE_BLOCK_ROWS or --block_rows")
    elif type(block_rows) is not int:
        util.exit_message("Invalid value type for ACE_BLOCK_ROWS or --block_rows")
    
    # Capping max block size here to prevent the hash function from taking forever
    if block_rows > MAX_ALLOWED_BLOCK_SIZE:
        util.exit_message(f"Block row size should be <= {MAX_ALLOWED_BLOCK_SIZE}")
    if block_rows < MIN_ALLOWED_BLOCK_SIZE:
        util.exit_message(f"Block row size should be >= {MIN_ALLOWED_BLOCK_SIZE}")

    if type(max_cpu_ratio) is int:
        max_cpu_ratio = float(max_cpu_ratio)
    elif type(max_cpu_ratio) is str:
        try:
            max_cpu_ratio = float(max_cpu_ratio)
        except Exception:
            util.exit_message("Invalid values for ACE_MAX_CPU_RATIO or --max_cpu_ratio")
    elif type(max_cpu_ratio) is not float:
        util.exit_message("Invalid value type for ACE_MAX_CPU_RATIO or --max_cpu_ratio")

    if max_cpu_ratio > 1.0 or max_cpu_ratio < 0.0:
        util.exit_message("Invalid value range for ACE_MAX_CPU_RATIO or --max_cpu_ratio")

    if output not in ["csv", "json"]:
        util.exit_message(
            "Diff-tables currently supports only csv and json output formats"
        )

    node_list = []
    try:
        node_list = parse_nodes(nodes)
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

    db, pg, node_info = cluster.load_json(cluster_name)

    cluster_nodes = []
    database = {}

    if dbname:
        for db_entry in db:
            if db_entry["name"] == dbname:
                database = db_entry
                break
    else:
        database = db[0]

    if not database:
        util.exit_message(f"Database '{dbname}' not found in cluster '{cluster_name}'")

    database["db_name"] = database.pop("name")

    # Combine db and cluster_nodes into a single json
    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    if nodes != "all" and len(node_list) > 1:
        for n in node_list:
            if not any(filter(lambda x: x["name"] == n, cluster_nodes)):
                util.exit_message("Specified nodenames not present in cluster")

    conn_list = []

    try:
        for nd in cluster_nodes:
            if nodes == "all":
                node_list.append(nd["name"])

            if (node_list and nd["name"] in node_list) or (not node_list):
                psql_conn = psycopg.connect(
                    dbname=nd["db_name"],
                    user=nd["username"],
                    password=nd["password"],
                    host=nd["ip_address"],
                    port=nd.get("port", 5432),
                )
                conn_list.append(psql_conn)

    except Exception as e:
        util.exit_message("Error in diff_tbls() Getting Connections:" + str(e), 1)

    util.message("Connections successful to nodes in cluster", p_state="success")

    # Connecting to any one of the nodes in the cluster should suffice
    conn = conn_list[0]
    cur = conn.cursor()

    # Check if repset exists
    sql = (
        "select set_name from spock.replication_set;"
    )
    cur.execute(sql)
    repset_list = [item[0] for item in cur.fetchall()]
    if repset_name not in repset_list:
        util.exit_message(f"Repset {repset_name} not found")

    # No need to sanitise repset_name here since psycopg does it for us
    sql = (
        "SELECT concat_ws('.', nspname, relname) FROM spock.tables where set_name = %s;"
    )
    cur.execute(sql, (repset_name,))
    tables = cur.fetchall()

    if not tables:
        util.message(
            "Repset may be empty",
            p_state="warning",
        )

    # Convert fetched rows into a list of strings
    tables = [table[0] for table in tables]

    for table in tables:
        util.message(f"\n\nCHECKING TABLE {table}...\n", p_state="info")
        table_diff(cluster_name, table)


if __name__ == "__main__":
    fire.Fire(
        {
            "table-diff": table_diff,
            "table-repair": table_repair,
            "table-rerun": table_rerun,
            "repset-diff": repset_diff,
            "schema-diff": schema_diff,
            "spock-diff": spock_diff,
        }
    )
