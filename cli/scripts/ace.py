####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

"""ACE is the place of the Anti Chaos Engine"""

import os, sys, itertools, csv, random, time, json, socket, subprocess, re, asyncio
import util, fire, meta, cluster, psycopg
from datetime import datetime
from multiprocessing import Manager, Pool, cpu_count, Value, Queue
from tqdm import tqdm
from ordered_set import OrderedSet
from itertools import combinations

l_dir = "/tmp"

# Shared variables needed by multiprocessing
queue = Manager().list()
result_queue = Manager().list()
job_queue = Queue()
row_diff_count = Value("I", 0)

# Set max number of rows up to which
# diff-tables will work
MAX_DIFF_ROWS = 10000
MAX_ALLOWED_BLOCK_SIZE = 50000
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
                linenum = i.split(",")[0]
            elif re.search(r"^< CREATE.", i):
                newtable = True
                print(i.replace("<", ""))
            elif re.search(r"^< ALTER.", i):
                print(i.replace("<", ""))
            elif re.search(r"^> CREATE TABLE.", i):
                print(
                    " DROP TABLE " + i.replace("> CREATE TABLE ", "").replace(" (", ";")
                )
            elif newtable == True:
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
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS T  , INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE C
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
            if node["sub_name"] == None:
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
        SELECT set_name, string_agg(relname,'   ') as relname FROM spock.tables GROUP BY set_name ORDER BY set_name;
        """
        table_info = util.run_psyco_sql(pg_v, db, sql, cluster_node["ip"])
        diff_spock["rep_set_info"] = []
        prCyan("Tables in RepSets:")
        if table_info == []:
            hints.append("Hint: No tables in database")
        for table in table_info:
            if table["set_name"] == None:
                print(" - Not in a replication set")
                hints.append(
                    "Hint: Tables not in replication set might not have primary keys, or you need to run repset-add-table"
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

    ##print(json.dumps(compare_spock,indent=2))
    return compare_spock


def run_apply_async_multiprocessing(func, argument_list, num_processes):
    pool = Pool(processes=num_processes)

    jobs = [
        pool.apply_async(func=func, args=(*argument,))
        if isinstance(argument, tuple)
        else pool.apply_async(func=func, args=(argument,))
        for argument in argument_list
    ]
    pool.close()
    result_list_tqdm = []
    for job in tqdm(jobs):
        result_list_tqdm.append(job.get())

    return result_list_tqdm


async def run_query(conn_str, query):
    async with await psycopg.AsyncConnection.connect(conn_str) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute(query)
            results = await acur.fetchall()
            return results


def compare_checksums(
    cluster_name,
    node_list,
    table_name,
    cols,
    p_key,
    block_rows,
    offset,
):
    global row_diff_count

    if row_diff_count.value >= MAX_DIFF_ROWS:
        return

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

    # Generate combinations of node pairs from node_list
    # E.g., if node_list = ['n1', 'n2', 'n3'] then generate
    # combinations = [('n1,n2'), ('n1', 'n3'), ('n2', 'n3')]
    node_pairs = combinations(node_list, 2)

    block_result = {}
    block_result["offset"] = offset
    block_result["diffs"] = []

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Read cluster information and connect to the local instance of pgcat
    il, db, pg, count, usr, passwd, os_usr, cert, nodes = cluster.load_json(
        cluster_name
    )

    for node_pair in node_pairs:
        if row_diff_count.value >= MAX_DIFF_ROWS:
            queue.append(block_result)
            return

        try:
            host1 = next(filter(lambda x: x.get("nodename") == node_pair[0], nodes))
            host2 = next(filter(lambda x: x.get("nodename") == node_pair[1], nodes))

            conn_str1 = f"dbname = {db} user={usr} password={passwd} host={host1['ip']} port={host1.get('port', 5432)}"
            conn_str2 = f"dbname = {db} user={usr} password={passwd} host={host2['ip']} port={host2.get('port', 5432)}"

            task1 = loop.create_task(run_query(conn_str1, hash_sql))
            task2 = loop.create_task(run_query(conn_str2, hash_sql))

            loop.run_until_complete(asyncio.gather(task1, task2))

            hash1 = task1.result()[0]
            hash2 = task2.result()[0]
        except Exception as e:
            util.exit_message(
                "Errored while connecting to database. Please check the nodenames you have provided"
            )
            return

        if hash1[0] != hash2[0]:
            task1 = loop.create_task(run_query(conn_str1, block_sql))
            task2 = loop.create_task(run_query(conn_str2, block_sql))

            loop.run_until_complete(asyncio.gather(task1, task2))

            t1_set = OrderedSet(task1.result())
            t2_set = OrderedSet(task2.result())

            t1_diff = t1_set - t2_set
            t2_diff = t2_set - t1_set

            if len(t1_diff) > 0 or len(t2_diff) > 0:
                block_result["diffs"].append(
                    {
                        host1["nodename"]: [dict(zip(cols, row)) for row in t1_diff],
                        host2["nodename"]: [dict(zip(cols, row)) for row in t2_diff],
                    }
                )

            with row_diff_count.get_lock():
                row_diff_count.value += max(len(t1_diff), len(t2_diff))

            if row_diff_count.value >= MAX_DIFF_ROWS:
                result_queue.append(MAX_DIFF_EXCEEDED)
                queue.append(block_result)
                return
            else:
                result_queue.append(BLOCK_MISMATCH)

        else:
            result_queue.append(BLOCK_OK)

    if len(block_result["diffs"]) > 0:
        queue.append(block_result)


def diff_tables(
    cluster_name,
    table_name,
    block_rows=1000,
    max_cpu_ratio=MAX_CPU_RATIO,
    pretty_print=False,
    nodes="all",
):
    """Efficiently compare tables across cluster using optional checksums and blocks of rows."""

    # Capping max block size here to prevent the has function from taking forever
    if block_rows > MAX_ALLOWED_BLOCK_SIZE:
        util.exit_message(f"Desired block row size is > {MAX_ALLOWED_BLOCK_SIZE}")

    bad_br = True
    try:
        b_r = int(block_rows)
        if b_r >= 10:
            bad_br = False
    except:
        pass
    if bad_br:
        util.exit_message(f"block_rows parm '{block_rows}' must be integer >= 10")

    node_list = []

    try:
        if nodes != "all":
            node_list = [s.strip() for s in nodes.split(",")]
    except Exception as e:
        util.exit_message(
            'Nodes should be a comma-separated list of nodenames. E.g., --nodes="n1,n2"'
        )

    if len(node_list) > 3:
        util.exit_message(
            "diff-tables currently supports up to a three-way table comparison"
        )

    util.message(f"\n## Validating cluster {cluster_name} exists")
    util.check_cluster_exists(cluster_name)

    nm_lst = table_name.split(".")
    if len(nm_lst) != 2:
        util.exit_message(f"TableName {table_name} must be of form 'schema.table_name'")
    l_schema = nm_lst[0]
    l_table = nm_lst[1]

    util.message(f"\n## Validating table {table_name} is comparable across nodes")

    il, db, pg, count, usr, passwd, os_usr, cert, cluster_nodes = cluster.load_json(
        cluster_name
    )

    conn_list = []

    util.message(f"\n## Validating connections to each node in cluster")

    try:
        for nd in cluster_nodes:
            if nodes == "all":
                node_list.append(nd["nodename"])

            if (node_list and nd["nodename"] in node_list) or (not node_list):
                util.message(
                    f'### Getting Conection to ({nd["nodename"]}) - {usr}@{nd["ip"]}:{nd.get("port",5432)}/{db}'
                )
                psql_conn = psycopg.connect(
                    dbname=db,
                    user=usr,
                    password=passwd,
                    host=nd["ip"],
                    port=nd.get("port", 5432),
                )
                conn_list.append(psql_conn)
    except Exception as e:
        util.exit_message("Error in diff_tbls() Getting Connections:\n" + str(e), 1)

    cols = None
    key = None

    for conn in conn_list:
        util.message(f"\n## Validating table {table_name} is comparable across nodes")
        curr_cols = get_cols(conn, l_schema, l_table)
        curr_key = get_key(conn, l_schema, l_table)

        if curr_cols and curr_key:
            util.message(f"## con1 cols={curr_cols}  key={curr_key}")
        else:
            if not curr_cols:
                util.exit_message(f"Invalid table name '{table_name}'")
            else:
                util.exit_message(f"No primary key found for '{table_name}'")

        if (not cols) and (not key):
            cols = curr_cols
            key = curr_key
            continue

        if (curr_cols != cols) or (curr_key != key):
            util.exit_message("Table schemas don't match")

        cols = curr_cols
        key = curr_key

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
    procs = max_procs if total_blocks > max_procs else total_blocks

    start_time = datetime.now()
    util.message(f"\n## start_time = {start_time} #################")

    offsets = [x for x in range(0, row_count + 1, block_rows)]
    total_offsets = len(offsets)

    cols_list = cols.split(",")

    arg_list = [
        (cluster_name, node_list, table_name, cols_list, key, block_rows, offset)
        for offset in offsets
    ]

    result_list = run_apply_async_multiprocessing(
        func=compare_checksums, argument_list=arg_list, num_processes=procs
    )

    mismatch = False
    diffs_exceeded = False

    for result in result_queue:
        if result == MAX_DIFF_EXCEEDED:
            diffs_exceeded = True

        if result == BLOCK_MISMATCH or result == MAX_DIFF_EXCEEDED:
            mismatch = True

    # Mismatch is True if there is a block mismatch or if we have
    # estimated that diffs may be greater than max allowed diffs
    if mismatch:
        if diffs_exceeded:
            util.message(
                f"\n\n####### TABLES DO NOT MATCH. DIFFS HAVE EXCEEDED {MAX_DIFF_ROWS} ROWS ########"
            )

        else:
            util.message("\n\n####### TABLES DO NOT MATCH ########\n")
            util.message(
                f"\n####### FOUND {row_diff_count.value} DIFFERENCES ########\n"
            )

        write_diffs_json(cols, block_rows, l_schema, l_table, pretty_print=pretty_print)

    else:
        util.message("\n####### TABLES MATCH OK ##########")

    run_time = datetime.now() - start_time
    util.message(
        f"\n## TOTAL ROWS CHECKED = {total_rows}. RUN TIME = {run_time} ##############################"
    )


def write_diffs_json(cols, block_rows, l_schema, l_table, pretty_print=False):
    output_json = {}

    output_json["total_diffs"] = row_diff_count.value
    output_json["block_size"] = block_rows
    output_json["diffs"] = [cur_entry for cur_entry in queue]

    if pretty_print:
        print(json.dumps(output_json, indent=2, default=str))
    else:
        print(json.dumps(output_json, default=str))


def write_diffs_csv(c1_cols, l_schema, l_table):
    t1_write_path = get_csv_file_name("t1", l_schema, l_table)
    t2_write_path = get_csv_file_name("t2", l_schema, l_table)

    # Elements in the shared queue may be out of order
    # Ordering cannot be guaranteed since primary keys
    # could be of varying types, and even composite keys

    with open(t1_write_path, "w") as f1, open(t2_write_path, "w") as f2:
        t1_writer = csv.writer(f1)
        t2_writer = csv.writer(f2)

        t1_writer.writerow(c1_cols.split(","))
        t2_writer.writerow(c1_cols.split(","))

        for cur_entry in queue:
            offset = cur_entry["offset"]
            t1_rows = cur_entry["t1_rows"]
            t2_rows = cur_entry["t2_rows"]

            for x1 in t1_rows:
                t1_writer.writerow(x1)

            for x2 in t2_rows:
                t2_writer.writerow(x2)

    cmd = f"diff -u {t1_write_path} {t2_write_path} | ydiff > out.diff"
    util.message(f"\n#### Running {cmd} ####")
    diff_s = subprocess.check_output(cmd, shell=True)


if __name__ == "__main__":
    fire.Fire(
        {
            "diff-tables": diff_tables,
            "diff-schemas": diff_schemas,
            "diff-spock": diff_spock,
        }
    )
