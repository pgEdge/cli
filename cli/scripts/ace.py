#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

"""ACE is the place of the Anti Chaos Engine"""

import os, sys, itertools, csv, random, time, json, socket, subprocess, re
import util, fire, meta, cluster
from datetime import datetime
from multiprocessing import Manager, Pool, cpu_count, Value, Queue
from tqdm import tqdm

l_dir = "/tmp"

try:
    import psycopg
except ImportError as e:
    util.exit_message("Missing 'psycopg' module from pip", 1)

# Shared variables needed by multiprocessing
queue = Manager().list()
result_queue = Manager().list()
job_queue = Queue()
row_diff_count = Value('I', 0)

PGCAT_HOST = "localhost"
PGCAT_PORT = 5432
PGCAT_DB1 = "db1"
PGCAT_DB2 = "db2"

# Set max number of rows up to which
# diff-tables will work
MAX_DIFF_ROWS = 10000
MAX_ALLOWED_BLOCK_SIZE = 50000
MAX_CPU_RATIO = 0.6


# Return codes for compare_checksums
BLOCK_OK = 0
MAX_DIFF_EXCEEDED = 1
BLOCK_MISMATCH = 2

pbar = tqdm(total=100, leave=False)


def get_pg_connection(pg_v, db, ip, usr):
    dbp = util.get_column("port", pg_v)

    if util.debug_lvl() > 0:
        util.message(
            f"get_pg_connection(): dbname={db}, user={usr}, port={dbp}", "debug"
        )

    try:
        con = psycopg.connect(dbname=db, user=usr, host=ip, port=dbp, autocommit=False)
    except Exception as e:
        util.exit_exception(e)

    return con


def run_psyco_sql(pg_v, db, cmd, ip, usr=None):
    if usr == None:
        usr = util.get_user()

    if util.is_verbose():
        util.message(cmd, "info")

    if util.debug_lvl() > 0:
        util.message(cmd, "debug")

    con = get_pg_connection(pg_v, db, ip, usr)
    if util.debug_lvl() > 0:
        util.message("run_psyco_sql(): " + str(con), "debug")

    try:
        cur = con.cursor(row_factory=psycopg.rows.dict_row)
        cur.execute(cmd)
        con.commit()

        return cur.fetchall()
        try:
            cur.close()
            con.close()
        except Exception as e:
            pass

    except Exception as e:
        util.exit_exception(e)


def prCyan(skk):
    print("\033[96m {}\033[00m".format(skk))


def prRed(skk):
    print("\033[91m {}\033[00m".format(skk))


def get_csv_file_name(p_prfx, p_schm, p_tbl, p_base_dir="/tmp"):
    return p_base_dir + os.sep + p_prfx + "-" + p_schm + "-" + p_tbl + ".csv"


def get_dump_file_name(p_prfx, p_schm, p_base_dir="/tmp"):
    return p_base_dir + os.sep + p_prfx + "-" + p_schm + ".sql"


def write_tbl_csv(
    p_con,
    p_prfx,
    p_schm,
    p_tbl,
    p_cols,
    p_key,
    p_checksums,
    p_blockrows,
    p_base_dir=None,
):
    try:
        out_file = get_csv_file_name(p_prfx, p_schm, p_tbl, p_base_dir)

        sql = (
            "SELECT "
            + p_cols
            + " "
            + "  FROM "
            + p_schm
            + "."
            + p_tbl
            + " "
            + "ORDER BY "
            + p_key
        )

        copy_sql = "COPY (" + sql + ") TO STDOUT WITH DELIMITER ',' CSV HEADER;"

        util.message("\n## COPY table " + p_tbl + " to " + out_file + " #############")
        ##print(f"DEBUG sql={sql}")

        with open(out_file, "wb") as f:
            with cur.copy(copy_sql) as copy:
                for data in copy:
                    f.write(data)

        with open(out_file, "r") as fp:
            lines = len(fp.readlines())

        size_b = os.path.getsize(out_file)
        size_m = round((size_b / 1000000.0), 6)

        util.message(
            "### "
            + str(f"{(lines - 1):,}")
            + " rows  "
            + str(size_m)
            + " MiB "
            + " checksum_use="
            + str(p_checksums)
            + " "
            + " block_rows="
            + str(p_blockrows)
        )
    except Exception as e:
        util.exit_message("Error in write_tbl_csv():\n" + str(e), 1)

    return out_file


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
        node_info = run_psyco_sql(pg_v, db, sql, cluster_node["ip"])
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
        table_info = run_psyco_sql(pg_v, db, sql, cluster_node["ip"])
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

def update_progressbar(res):
    result, offset_size = res[0], res[1]
    if res[0] == MAX_DIFF_EXCEEDED:
        util.exit_message(f"Differences between tables have exceeded {MAX_DIFF_ROWS} rows")
    else:
        progress = 100.0/offset_size
        pbar.update(progress)

def compare_checksums(cluster_name, table_name, p_key, block_rows, offset, total_offsets):

    global row_diff_count

    hash1 = ""
    hash2 = ""

    # Read cluster information and connect to the local instance of pgcat
    il, db, pg, count, usr, passwd, os_usr, cert, nodes = cluster.load_json(
        cluster_name
    )
    con1 = psycopg.connect(
        dbname=PGCAT_DB1, user=usr, password=passwd, host=PGCAT_HOST, port=PGCAT_PORT, prepare_threshold=1
    )
    con2 = psycopg.connect(
        dbname=PGCAT_DB2, user=usr, password=passwd, host=PGCAT_HOST, port=PGCAT_PORT, prepare_threshold=1
    )

    with con1.cursor() as cur1, con2.cursor() as cur2:
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


        # Get the hash of the block from both tables we are
        # currently looking at.
        #start = time.time()
        cur1.execute(hash_sql)
        hash1 = cur1.fetchone()[0]

        cur2.execute(hash_sql)
        hash2 = cur2.fetchone()[0]

        if hash1 != hash2:
            # Get mismatching blocks from both tables
            cur1.execute(block_sql)
            t1_result = cur1.fetchall()
            cur2.execute(block_sql)
            t2_result = cur2.fetchall()

            t1_tuples = []

            for tup in t1_result:
                str_tup = tuple(str(elem) for elem in tup)
                t1_tuples.append(str_tup)

            t2_tuples = []

            for tup in t2_result:
                str_tup = tuple(str(elem) for elem in tup)
                t2_tuples.append(str_tup)

            t1_set = set(t1_result)
            t2_set = set(t2_result)

            t1_diff = t1_set.difference(t2_set)
            t2_diff = t2_set.difference(t1_set)

            block_result = {
                "offset": offset,
                "t1_rows": t1_diff,
                "t2_rows": t2_diff,
            }

            if len(t1_diff) > 0 or len(t2_diff) > 0:
                util.message(f"\nFound block mismatch at offset: {offset}")
                queue.append(block_result)

            with row_diff_count.get_lock():
                row_diff_count.value += len(t1_diff) + len(t2_diff)

            # We can only estimate how many diffs we may have.
            # The actuall diff calc is done later by ydiff.
            # So, even if there is just one row mismatch, and
            # we hit this condition, we will still need
            # to return early here.
            # TODO: Figure out how to exit early here
            if row_diff_count.value >= MAX_DIFF_ROWS:
                result_queue.append(MAX_DIFF_EXCEEDED)
                return MAX_DIFF_EXCEEDED, total_offsets
            else:
                result_queue.append(BLOCK_MISMATCH)
                return BLOCK_MISMATCH, total_offsets

        else:
            result_queue.append(BLOCK_OK)
            return BLOCK_OK, total_offsets


# TODO: Add feature to allow users to specify offset and limit

def diff_tables(
    cluster_name,
    table_name,
    checksum_use=False,
    block_rows=1,
    max_cpu_ratio=MAX_CPU_RATIO,
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

    if str(checksum_use) == "True" or str(checksum_use) == "False":
        pass
    else:
        util.exit_message(
            f"checksum_use parm '{checksum_use}' must be 'True' or 'False'"
        )

    util.message(f"\n## Validating cluster {cluster_name} exists")
    util.check_cluster_exists(cluster_name)

    nm_lst = table_name.split(".")
    if len(nm_lst) != 2:
        util.exit_message(f"TableName {table_name} must be of form 'schema.table_name'")
    l_schema = nm_lst[0]
    l_table = nm_lst[1]

    util.message(f"\n## Validating table {table_name} is comparable across nodes")

    il, db, pg, count, usr, passwd, os_usr, cert, nodes = cluster.load_json(
        cluster_name
    )
    con1 = None
    con2 = None
    util.message(f"\n## Validating connections to each node in cluster")

    # Get two connections to pgcat.
    # TODO: Need to specify which two nodes to connect to.
    try:
        n = 0
        for nd in nodes:
            n = n + 1
            if n == 1:
                util.message(
                    f'### Getting Conection to Node1 ({nd["nodename"]}) - {usr}@{PGCAT_HOST}:{PGCAT_PORT}/{PGCAT_DB1}'
                )
                con1 = psycopg.connect(
                    dbname=PGCAT_DB1,
                    user=usr,
                    password=passwd,
                    host=PGCAT_HOST,
                    port=PGCAT_PORT,
                )
            elif n == 2:
                util.message(
                    f'### Getting Conection to Node2 ({nd["nodename"]}) - {usr}@{PGCAT_HOST}:{PGCAT_PORT}/{PGCAT_DB2}'
                )
                con2 = psycopg.connect(
                    dbname=PGCAT_DB2,
                    user=usr,
                    password=passwd,
                    host=PGCAT_HOST,
                    port=PGCAT_PORT,
                )
            else:
                util.message(
                    f"### WARNING!! Node {n} ignored.  Only supports first two nodes for the moment."
                )
    except Exception as e:
        util.exit_message("Error in diff_tbls() Getting Connections:\n" + str(e), 1)

    util.message(f"\n## Validating table {table_name} is comparable across nodes")
    c1_cols = get_cols(con1, l_schema, l_table)
    c1_key = get_key(con1, l_schema, l_table)

    if c1_cols and c1_key:
        util.message(f"## con1 cols={c1_cols}  key={c1_key}")
    else:
        if not c1_cols:
            util.exit_message(f"Invalid table name '{table_name}'")
        else:
            util.exit_message(f"No primary key found for '{table_name}'")

    c2_cols = get_cols(con2, l_schema, l_table)
    c2_key = get_key(con2, l_schema, l_table)

    if c2_cols and c2_key:
        util.message(f"## con2 cols={c2_cols}  key={c2_key}")
    else:
        if not c2_cols:
            util.exit_message(f"Invalid table name '{table_name}'")
        else:
            util.exit_message(f"No primary key found for '{table_name}'")

    if (c1_cols != c2_cols) or (c1_key != c2_key):
        util.exit_message("Tables don't match in con1 & con2")

    t1_rows = get_row_count(con1, l_schema, l_table)
    t2_rows = get_row_count(con2, l_schema, l_table)

    row_count = max(t1_rows, t2_rows)

    total_blocks = row_count // block_rows
    total_blocks = total_blocks if total_blocks > 0 else 1
    cpus = cpu_count()
    max_procs = int(cpus * max_cpu_ratio * 2) if cpus > 1 else 1
    procs = max_procs if total_blocks > max_procs else total_blocks

    # Check if we have enough procs to cover all rows in the table
    # Suppose that block size = 100, cpus = 2, total_rows = 1000
    # Needed minimum block size to cover all rows = 1000/2 = 500
    # But, specified block size = 100, which is not sufficient to
    # cover all rows.
    # Therefore, we need a check to see if the specified block size
    # is at least = needed_block_size

    #needed_block_size = (row_count // procs) + 1

    #if block_rows < needed_block_size:
    #    block_rows = needed_block_size

    # Once we reinit block_rows, check against MAX_ALLOWED_BLOCK_SIZE again
    #if block_rows > MAX_ALLOWED_BLOCK_SIZE:
    #    util.exit_message(f"Needed block rows are > {MAX_ALLOWED_BLOCK_SIZE}")

    start_time = datetime.now()
    util.message(f"\n## start_time = {start_time} #################")

    offsets = [x for x in range(0, row_count + 1, block_rows)]
    total_offsets = len(offsets)

    with Pool(procs) as pool:
        results = [pool.apply_async(compare_checksums, args=(cluster_name, table_name, c1_key, block_rows, offset, total_offsets,), callback=update_progressbar) for offset in offsets]
        pool.close()
        pool.join()

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
            util.message("\n\n####### TABLES DO NOT MATCH ########")

        write_diffs(c1_cols, row_count, l_schema, l_table)
        util.message("\n###### Diff written to out.diff ######")
    else:
        util.message("\n####### TABLES MATCH OK ##########")

    run_time = datetime.now() - start_time
    util.message(f"\n## run_time = {run_time} ##############################")


def write_diffs(cols, row_count, l_schema, l_table):
    t1_write_path = get_csv_file_name("t1", l_schema, l_table)
    t2_write_path = get_csv_file_name("t2", l_schema, l_table)

    num_cols = len(cols.split(","))

    # Elements in the shared queue may be out of order
    # In order to run the diff, mismatching blocks from
    # both tables need to be written in order int their
    # respective files for ydiff to work
    # The way we do this -- currently in a not so efficient way --
    # is by creating two empty lists both equal to the sizes
    # of row count. Then, we consume from the queue and insert into
    # the list at the index = offset of the block.
    # Finally, we consume from the list and write to the respective files.
    # Now, we simply run ydiff on these files and log the output to
    # out.diff
    #t1_list, t2_list = [""] * row_count, [""] * row_count

    with open(t1_write_path, "w") as f1, open(t2_write_path, "w") as f2:
        for cur_entry in queue:
            offset = cur_entry["offset"]
            t1_rows = cur_entry["t1_rows"]
            t2_rows = cur_entry["t2_rows"]

            # Write rows to the in-memory list at the offset
            #
            # TODO: This might get expensive wrt time and space
            #       if we increase max_blocks. Ideal way would be
            #       to write directly to file at offset, trim empty lines,
            #       and then use ydiff

            #insert_index = offset

            #for t1_row in t1_rows:
            #    t1_list.insert(insert_index, t1_row)
            #    insert_index+=1

            #insert_index = offset

            #for t2_row in t2_rows:
            #    t2_list.insert(insert_index, t2_row)
            #    insert_index+=1

            #for t1_row, t2_row in itertools.zip_longest(t1_rows, t2_rows):
            #    t1_list.insert(insert_index, t1_row)
            #    t2_list.insert(insert_index, t2_row)
            #    insert_index += 1

            t1_writer = csv.writer(f1)
            t2_writer = csv.writer(f2)

            for x1 in t1_rows:
                t1_writer.writerow(x1)

            for x2 in t2_rows:
                t2_writer.writerow(x2)

            #for x1, x2 in itertools.zip_longest(t1_list, t2_list):
            #    if x1 == None and x2 == None:
            #        continue
            #    if x1:
            #        t1_writer.writerow(x1)
            #    if x2:
            #        t2_writer.writerow(x2)

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
