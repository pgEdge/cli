import ast
import json
import os
from datetime import datetime
from itertools import combinations
from multiprocessing import Lock, Manager, Value, cpu_count

from concurrent.futures import ThreadPoolExecutor

import psycopg
from mpire import WorkerPool
from mpire.utils import make_single_arguments
from ordered_set import OrderedSet
from psycopg import sql
from psycopg.rows import dict_row
from math import ceil

import ace
import ace_db
import cluster
import util
import ace_config as config
from ace_db import TableDiffTask, TableRepairTask
from ace import AceException


# Shared variables needed by multiprocessing
queue = Manager().list()
result_queue = Manager().list()
diff_dict = Manager().dict()
row_diff_count = Value("I", 0)
lock = Lock()


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
                    user={node['db_user']}          \
                    password={node['db_password']}   \
                    host={node['public_ip']}   \
                    port={node.get('port', 5432)}"

        worker_state[node["name"]] = psycopg.connect(conn_str).cursor()


# Accepts list of pkeys and values and generates a where clause that in the form
# `(pkey1name, pkey2name ...) in ( (pkey1val1, pkey2val1 ...),
#                                 (pkey1val2, pkey2val2 ...) ... )`
def generate_where_clause(primary_keys, id_values):
    if len(primary_keys) == 1:
        # Single primary key
        id_values_list = ", ".join(repr(val) for val in id_values)
        query = f"{primary_keys[0]} IN ({id_values_list})"

    else:
        # Composite primary key
        conditions = ", ".join(
            f"({', '.join(repr(val) for val in id_tuple)})" for id_tuple in id_values
        )
        key_columns = ", ".join(primary_keys)
        query = f"({key_columns}) IN ({conditions})"

    return query


def compare_checksums(shared_objects, worker_state, batches):
    global row_diff_count

    if row_diff_count.value >= config.MAX_DIFF_ROWS:
        return

    p_key = shared_objects["p_key"]
    schema_name = shared_objects["schema_name"]
    table_name = shared_objects["table_name"]
    node_list = shared_objects["node_list"]
    cols = shared_objects["cols_list"]
    simple_primary_key = shared_objects["simple_primary_key"]
    mode = shared_objects["mode"]

    for batch in batches:
        where_clause = str()
        where_clause_temp = list()

        if mode == "diff":
            pkey1, pkey2 = batch
            if simple_primary_key:
                if pkey1 is not None:
                    where_clause_temp.append(
                        sql.SQL("{p_key} >= {pkey1}").format(
                            p_key=sql.Identifier(p_key), pkey1=sql.Literal(pkey1)
                        )
                    )
                if pkey2 is not None:
                    where_clause_temp.append(
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
                    where_clause_temp.append(
                        sql.SQL("({p_key}) >= ({pkey1})").format(
                            p_key=sql.SQL(", ").join(
                                [
                                    sql.Identifier(col.strip())
                                    for col in p_key.split(",")
                                ]
                            ),
                            pkey1=sql.SQL(", ").join(
                                [sql.Literal(val) for val in pkey1]
                            ),
                        )
                    )

                if pkey2 is not None:
                    where_clause_temp.append(
                        sql.SQL("({p_key}) < ({pkey2})").format(
                            p_key=sql.SQL(", ").join(
                                [
                                    sql.Identifier(col.strip())
                                    for col in p_key.split(",")
                                ]
                            ),
                            pkey2=sql.SQL(", ").join(
                                [sql.Literal(val) for val in pkey2]
                            ),
                        )
                    )

            where_clause = sql.SQL(" AND ").join(where_clause_temp)

        elif mode == "rerun":
            keys = p_key.split(",")
            where_clause = sql.SQL(generate_where_clause(keys, batch))

        else:
            raise Exception(f"Mode {mode} not recognized in compare_checksums")

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
                where_clause=where_clause,
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
                where_clause=where_clause,
            )

        block_sql = sql.SQL("SELECT * FROM {table_name} WHERE {where_clause}").format(
            table_name=sql.SQL("{}.{}").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
            ),
            where_clause=where_clause,
        )

        for node_pair in combinations(node_list, 2):
            host1 = node_pair[0]
            host2 = node_pair[1]

            # Return early if we have already exceeded the max number of diffs
            if row_diff_count.value >= config.MAX_DIFF_ROWS:
                return config.MAX_DIFFS_EXCEEDED

            try:
                # Run the checksum query on both nodes in parallel
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(run_query, worker_state, host1, hash_sql),
                        executor.submit(run_query, worker_state, host2, hash_sql),
                    ]
                    hash1, hash2 = [f.result()[0][0] for f in futures]
            except Exception as e:
                result_queue.append(e)
                return config.BLOCK_ERROR

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
                    result_queue.append(e)
                    return config.BLOCK_ERROR

                # Transform all elements in t1_result and t2_result into strings before
                # consolidating them into a set
                # TODO: Test and add support for different datatypes here
                t1_result = [
                    tuple(
                        str(x) if not isinstance(x, list) else str(sorted(x))
                        for x in row
                    )
                    for row in t1_result
                ]
                t2_result = [
                    tuple(
                        str(x) if not isinstance(x, list) else str(sorted(x))
                        for x in row
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

                if row_diff_count.value >= config.MAX_DIFF_ROWS:
                    return config.MAX_DIFFS_EXCEEDED
                else:
                    result_queue.append(config.BLOCK_MISMATCH)
            else:
                result_queue.append(config.BLOCK_OK)


def table_diff(td_task: TableDiffTask):
    """Efficiently compare tables across cluster using checksums and blocks of rows"""

    simple_primary_key = True
    if len(td_task.fields.key.split(",")) > 1:
        simple_primary_key = False

    row_count = 0
    total_rows = 0
    conn_with_max_rows = None
    table_types = None

    for params in td_task.fields.conn_params:
        conn = psycopg.connect(**params)
        if not table_types:
            table_types = ace.get_row_types(conn, td_task.fields.l_table)

        rows = ace.get_row_count(conn, td_task.fields.l_schema, td_task.fields.l_table)
        total_rows += rows
        if rows > row_count:
            row_count = rows
            conn_with_max_rows = conn

    pkey_offsets = []

    if not conn_with_max_rows:
        util.message(
            "ALL TABLES ARE EMPTY",
            p_state="warning",
            quiet_mode=td_task.quiet_mode,
        )
        return

    # Use conn_with_max_rows to get the first and last primary key values
    # of every block row. Repeat until we no longer have any more rows.
    # Store results in pkey_offsets.

    if simple_primary_key:
        pkey_sql = sql.SQL("SELECT {key} FROM {table_name} ORDER BY {key}").format(
            key=sql.Identifier(td_task.fields.key),
            table_name=sql.SQL("{}.{}").format(
                sql.Identifier(td_task.fields.l_schema),
                sql.Identifier(td_task.fields.l_table),
            ),
        )
    else:
        pkey_sql = sql.SQL("SELECT {key} FROM {table_name} ORDER BY {key}").format(
            key=sql.SQL(", ").join(
                [sql.Identifier(col) for col in td_task.fields.key.split(",")]
            ),
            table_name=sql.SQL("{}.{}").format(
                sql.Identifier(td_task.fields.l_schema),
                sql.Identifier(td_task.fields.l_table),
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

    util.message(
        "Getting primary key offsets for table...",
        p_state="info",
        quiet_mode=td_task.quiet_mode,
    )
    future = ThreadPoolExecutor().submit(
        get_pkey_offsets, conn_with_max_rows, pkey_sql, td_task.block_rows
    )
    pkey_offsets = future.result()

    total_blocks = row_count // td_task.block_rows
    total_blocks = total_blocks if total_blocks > 0 else 1
    cpus = cpu_count()
    max_procs = int(cpus * td_task.max_cpu_ratio) if cpus > 1 else 1

    # If we don't have enough blocks to keep all CPUs busy, use fewer processes
    procs = max_procs if total_blocks > max_procs else total_blocks

    start_time = datetime.now()

    """
    Generate offsets for each process to work on.
    We go up to the max rows among all nodes because we want our set difference logic
    to capture diffs even if rows are absent in one node
    """

    cols_list = td_task.fields.cols.split(",")
    cols_list = [col for col in cols_list if not col.startswith("_Spock_")]

    # Shared variables needed by all workers
    shared_objects = {
        "cluster_name": td_task.cluster_name,
        "database": td_task.fields.database,
        "node_list": td_task.fields.node_list,
        "schema_name": td_task.fields.l_schema,
        "table_name": td_task.fields.l_table,
        "cols_list": cols_list,
        "p_key": td_task.fields.key,
        "block_rows": td_task.block_rows,
        "simple_primary_key": simple_primary_key,
        "mode": "diff",
    }

    util.message(
        "Starting jobs to compare tables...\n",
        p_state="info",
        quiet_mode=td_task.quiet_mode,
    )

    batches = [
        pkey_offsets[i: i + td_task.batch_size]
        for i in range(0, len(pkey_offsets), td_task.batch_size)
    ]

    mismatch = False
    diffs_exceeded = False
    errors = False

    with WorkerPool(
        n_jobs=procs,
        shared_objects=shared_objects,
        use_worker_state=True,
    ) as pool:
        for result in pool.imap_unordered(
            compare_checksums,
            make_single_arguments(batches),
            worker_init=init_db_connection,
            progress_bar=True if not td_task.quiet_mode else False,
            iterable_len=len(batches),
            progress_bar_style="rich",
        ):
            if result == config.MAX_DIFFS_EXCEEDED:
                diffs_exceeded = True
                mismatch = True
                break
            elif result == config.BLOCK_ERROR:
                errors = True
                break

        if diffs_exceeded:
            util.message(
                "Prematurely terminated jobs since diffs have"
                " exceeded MAX_ALLOWED_DIFFS",
                p_state="warning",
                quiet_mode=td_task.quiet_mode,
            )

    for result in result_queue:
        if result == config.BLOCK_MISMATCH:
            mismatch = True

    if errors:
        raise AceException(
            "There were one or more errors while connecting to databases.\n \
                Please examine the connection information provided, or the nodes' \
                    status before running this script again."
        )

    # Mismatch is True if there is a block mismatch or if we have
    # estimated that diffs may be greater than max allowed diffs
    if mismatch:
        if diffs_exceeded:
            util.message(
                f"TABLES DO NOT MATCH. DIFFS HAVE EXCEEDED {config.MAX_DIFF_ROWS} ROWS",
                p_state="warning",
                quiet_mode=td_task.quiet_mode,
            )

        else:
            util.message(
                "TABLES DO NOT MATCH", p_state="warning", quiet_mode=td_task.quiet_mode
            )

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
                quiet_mode=td_task.quiet_mode,
            )

        if td_task.output == "json":
            td_task.diff_file_path = ace.write_diffs_json(
                diff_dict, table_types, quiet_mode=td_task.quiet_mode
            )

        elif td_task.output == "csv":
            ace.write_diffs_csv()

    else:
        util.message(
            "TABLES MATCH OK\n", p_state="success", quiet_mode=td_task.quiet_mode
        )

    run_time = util.round_timedelta(datetime.now() - start_time).total_seconds()
    run_time_str = f"{run_time:.2f}"

    util.message(
        f"TOTAL ROWS CHECKED = {total_rows}\nRUN TIME = {run_time_str} seconds",
        p_state="info",
        quiet_mode=td_task.quiet_mode,
    )

    td_task.scheduler.task_status = "COMPLETED"
    td_task.scheduler.finished_at = datetime.now()
    td_task.scheduler.time_taken = run_time
    td_task.scheduler.task_context = {"total_rows": total_rows, "mismatch": mismatch}
    ace_db.update_ace_task(td_task)


def table_repair(tr_task: TableRepairTask):
    """Apply changes from a table-diff source of truth to destination table"""
    import pandas as pd

    start_time = datetime.now()
    conns = {}

    for params in tr_task.fields.conn_params:
        conns[tr_task.fields.host_map[params["host"] + params["port"]]] = (
            psycopg.connect(**params)
        )

    if tr_task.generate_report:
        report = dict()
        report["time_stamp"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        report["arguments"] = {
            "cluster_name": tr_task.cluster_name,
            "diff_file": tr_task.diff_file,
            "source_of_truth": tr_task.source_of_truth,
            "table_name": tr_task._table_name,
            "dbname": tr_task._dbname,
            "dry_run": tr_task.dry_run,
            "quiet": tr_task.quiet_mode,
            "upsert_only": tr_task.upsert_only,
            "generate_report": tr_task.generate_report,
        }
        report["database"] = tr_task.fields.database
        report["changes"] = dict()

    """
    If the diff-file is not a valid json, then we throw an error message and exit.
    However, if the diff-file is a valid json, it's a slightly trickier case.
    Our diff-file is a json of the form:
    {
        "node1/node2": {
            "node1": [{"col1": "val1", "col2": "val2", ...}, ...],
            "node2": [{"col1": "val1", "col2": "val2", ...}, ...]
        },
        "node1/node3": {
            "node1": [{"col1": "val1", "col2": "val2", ...}, ...],
            "node3": [{"col1": "val1", "col2": "val2", ...}, ...]
        }
    }

    We need to make sure that the root-level keys are of the form "node1/node2" and
    that the inner keys have the corresponding node names. E.g., if the root-level key
    is "node1/node2", then the inner keys should be "node1" and "node2".

    A simple way we achieve this is by iterating over the root keys and checking if the
    inner keys are contained in the list when the root key is split by "/". If not, we
    throw an error message and exit.

    TODO: It might be possible that the diff file has different cols compared to the
    target table. We need to handle this case.
    """
    try:
        diff_json = json.loads(open(tr_task.diff_file_path, "r").read())
    except Exception:
        util.exit_message("Could not load diff file as JSON")

    try:
        if any(
            [
                set(list(diff_json[k].keys())) != set(k.split("/"))
                for k in diff_json.keys()
            ]
        ):
            util.exit_message("Contents of diff file improperly formatted")

        diff_json = {
            node_pair: {
                node: [{key: str(val) for key, val in row.items()} for row in rows]
                for node, rows in nodes_data.items()
            }
            for node_pair, nodes_data in diff_json.items()
        }
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
        for entry in diff_json[node_pair].get(tr_task.source_of_truth, [])
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
        [
            nd["name"]
            for nd in tr_task.fields.cluster_nodes
            if nd["name"] != tr_task.source_of_truth
        ]
    )
    dry_run_msg = (
        "######## DRY RUN ########\n\n"
        f"Repair would have attempted to upsert {len(true_rows)} rows on "
        f"{nodes_to_repair}\n\n"
        "######## END DRY RUN ########"
    )
    if tr_task.dry_run:
        util.message(dry_run_msg, p_state="alert", quiet_mode=tr_task.quiet_mode)
        return

    cols_list = tr_task.fields.cols.split(",")
    # Remove metadata columsn "_Spock_CommitTS_" and "_Spock_CommitOrigin_"
    # from cols_list
    cols_list = [col for col in cols_list if not col.startswith("_Spock_")]
    simple_primary_key = True
    keys_list = []

    if len(tr_task.fields.key.split(",")) > 1:
        simple_primary_key = False
        keys_list = tr_task.fields.key.split(",")

    total_upserted = {}
    total_deleted = {}

    # Gets types of each column in table
    table_types = ace.get_row_types(
        conns[tr_task.source_of_truth], tr_task.fields.l_table
    )

    if tr_task.upsert_only:
        deletes_skipped = dict()

    for node_pair in diff_json.keys():
        node1, node2 = node_pair.split("/")

        true_rows = (
            [
                tuple(str(x) for x in entry.values())
                for entry in diff_json[node_pair][tr_task.source_of_truth]
            ]
            if tr_task.source_of_truth in [node1, node2]
            else true_rows
        )

        divergent_rows = []
        divergent_node = None

        if node1 == tr_task.source_of_truth:
            divergent_rows = [
                tuple(str(x) for x in row.values())
                for row in diff_json[node_pair][node2]
            ]
            divergent_node = node2
        elif node2 == tr_task.source_of_truth:
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
                upsert_lookup[row[tr_task.fields.key]] = 1
            else:
                upsert_lookup[tuple(row[col] for col in keys_list)] = 1

        for entry in rows_to_delete_json:
            if simple_primary_key:
                if entry[tr_task.fields.key] in upsert_lookup:
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
                delete_keys = tuple(
                    (row[tr_task.fields.key],) for row in filtered_rows_to_delete
                )
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
            INSERT INTO {tr_task._table_name}
            VALUES ({','.join(['%s'] * len(cols_list))})
            ON CONFLICT ("{tr_task.fields.key}") DO UPDATE SET
            """
        else:
            update_sql = f"""
            INSERT INTO {tr_task.table_name}
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
            DELETE FROM {tr_task._table_name}
            WHERE "{tr_task.fields.key}" = %s;
            """
        else:
            delete_sql = f"""
            DELETE FROM {tr_task.table_name}
            WHERE
            """

            for k in keys_list:
                delete_sql += f' "{k}" = %s AND'

            delete_sql = delete_sql[:-3] + ";"

        conn = conns[divergent_node]
        cur = conn.cursor()
        spock_version = ace.get_spock_version(conn)

        # FIXME: Do not use harcoded version numbers
        # Read required version numbers from a config file
        if spock_version >= 4.0:
            cur.execute("SELECT spock.repair_mode(true);")

        if tr_task.generate_report:
            report["changes"][divergent_node] = dict()

        """
        We had previously converted all rows to strings for computing set differences.
        We now need to convert them back to their original types before upserting.
        psycopg3 will internally handle type conversions from lists/arrays to their
        respective types in Postgres.

        So, if an element in a row is a list or a json that is represented as:
        '{"key1": "val1", "key2": "val2"}' or '[1, 2, 3]', we need to use the
        abstract syntax tree module to convert them back to their original types.
        ast.literal_eval() will give us {'key1': 'val1', 'key2': 'val2'} and
        [1, 2, 3] respectively.
        """
        upsert_tuples = []
        if rows_to_upsert:
            for row in rows_to_upsert_json:
                modified_row = tuple()
                for col_name in cols_list:
                    col_type = table_types[col_name]
                    elem = row[col_name]
                    try:
                        if any([s in col_type for s in ["char", "text", "vector"]]):
                            modified_row += (elem,)
                        else:
                            item = ast.literal_eval(elem)
                            if col_type == "jsonb":
                                item = json.dumps(item)
                            modified_row += (item,)

                    except (ValueError, SyntaxError):
                        modified_row += (elem,)

                upsert_tuples.append(modified_row)

            # Performing the upsert
            cur.executemany(update_sql, upsert_tuples)
            if tr_task.generate_report:
                report["changes"][divergent_node]["upserted_rows"] = [
                    dict(zip(cols_list, tup)) for tup in upsert_tuples
                ]

        if delete_keys and not tr_task.upsert_only:
            # Performing the deletes
            if len(delete_keys) > 0:
                cur.executemany(delete_sql, delete_keys)
                if tr_task.generate_report:
                    report["changes"][divergent_node]["deleted_rows"] = delete_keys
        elif delete_keys and tr_task.upsert_only:
            deletes_skipped[divergent_node] = filtered_rows_to_delete

        if spock_version >= 4.0:
            cur.execute("SELECT spock.repair_mode(false);")

        conn.commit()

    if tr_task.upsert_only:

        def compare_values(val1: dict, val2: dict) -> bool:
            if val1.keys() != val2.keys():
                return False
            if any([val1[key] != val2[key] for key in val1.keys()]):
                return False
            return True

        upsert_dict = dict()
        for nd_name, values in deletes_skipped.items():
            for value in values:
                if simple_primary_key:
                    full_key = value[tr_task.key]
                else:
                    full_key = tuple(value[pkey_part] for pkey_part in keys_list)

                if full_key not in upsert_dict:
                    upsert_dict[full_key] = value, {nd_name}

                elif not compare_values(value, upsert_dict[full_key][0]):
                    upsert_dict[full_key][1].add(nd_name)
                else:
                    upsert_dict[full_key][1].add(nd_name)

        # format of upsert dict will now be
        # {
        #     "pkey1" : ({key: val to upsert to pkey1}, {nodes that have pkey1})
        #     "pkey2" : ({key: val to upsert to pkey2}, {nodes that have pkey2})
        # }
        # example when n1 is s.o.t.
        # {
        #     '2': ({'id': '2', 'num': '2'}, {'n2'}),
        #     '4': ({'id': '4', 'num': '4'}, {'n3', 'n2'}),
        #     '5': ({'id': '5', 'num': '4'}, {'n3', 'n2'}),
        #     '3': ({'id': '3', 'num': '3'}, {'n3'})
        # }
        # so `2`, `3`, `4`, `5` need to be inserted into n1, `2` in n3, and `3` into n2

        if tr_task.generate_report:
            report["changes"][tr_task.source_of_truth] = dict()
            report["changes"][tr_task.source_of_truth]["upserted_rows"] = []
            report["changes"][tr_task.source_of_truth]["deleted_rows"] = []
            report["changes"][tr_task.source_of_truth]["missing_rows"] = [
                {"row": values, "present_in": list(nodes)}
                for values, nodes in upsert_dict.values()
            ]

    run_time = util.round_timedelta(datetime.now() - start_time).total_seconds()
    run_time_str = f"{run_time:.2f}"

    util.message(
        f"Successfully applied diffs to {tr_task._table_name} in cluster"
        f"{tr_task.cluster_name}\n",
        p_state="success",
        quiet_mode=tr_task.quiet_mode,
    )

    if tr_task.generate_report:
        now = datetime.now()
        report_folder = "reports"
        report["run_time"] = run_time

        if not os.path.exists(report_folder):
            os.mkdir(report_folder)

        dirname = now.strftime("%Y-%m-%d")
        diff_file_suffix = now.strftime("%H%M%S") + f"{now.microsecond // 1000:03d}"
        diff_filename = "report_" + diff_file_suffix + ".json"

        dirname = os.path.join(report_folder, dirname)

        if not os.path.exists(dirname):
            os.mkdir(dirname)

        filename = os.path.join(dirname, diff_filename)
        json.dump(report, open(filename, "w"), default=str, indent=2)
        print(f"Wrote report to {filename}")

    util.message("*** SUMMARY ***\n", p_state="info", quiet_mode=tr_task.quiet_mode)

    for node in total_upserted.keys():
        util.message(
            f"{node} UPSERTED = {total_upserted[node]} rows",
            p_state="info",
            quiet_mode=tr_task.quiet_mode,
        )

    print()

    for node in total_deleted.keys():
        util.message(
            f"{node} DELETED = {total_deleted[node]} rows",
            p_state="info",
            quiet_mode=tr_task.quiet_mode,
        )

    util.message(
        f"RUN TIME = {run_time_str} seconds",
        p_state="info",
        quiet_mode=tr_task.quiet_mode,
    )

    if spock_version < 4.0:
        util.message(
            "WARNING: Unable to pause/resume replication during repair due to"
            "an older spock version. Please do a manual check as repair may"
            "have caused further divergence",
            p_state="warning",
            quiet_mode=tr_task.quiet_mode,
        )

    tr_task.scheduler.task_status = "COMPLETED"
    tr_task.scheduler.finished_at = datetime.now()
    tr_task.scheduler.time_taken = run_time
    tr_task.scheduler.task_context = {
        "source_of_truth": tr_task.source_of_truth,
        "upserted": total_upserted,
        "deleted": total_deleted,
    }
    ace_db.update_ace_task(tr_task)


def table_rerun_temptable(td_task: TableDiffTask) -> None:

    # load diff data and validate
    diff_data = json.load(open(td_task.diff_file_path, "r"))
    diff_keys = set()
    key = td_task.fields.key.split(",")

    # Simple pkey
    if len(key) == 1:
        for node_pair in diff_data.keys():
            nd1, nd2 = node_pair.split("/")

            for row in diff_data[node_pair][nd1] + diff_data[node_pair][nd2]:
                diff_keys.add(row[key[0]])

    # Comp pkey
    else:
        for node_pair in diff_data.keys():
            nd1, nd2 = node_pair.split("/")

            for row in diff_data[node_pair][nd1] + diff_data[node_pair][nd2]:
                diff_keys.add(tuple(row[key_component] for key_component in key))

    temp_table_name = f"temp_{td_task.scheduler.task_id.lower()}_rerun"
    table_qry = f"create table {temp_table_name} as "
    table_qry += f"SELECT * FROM {td_task._table_name} WHERE " + generate_where_clause(
        key, diff_keys
    )
    clean_qry = f"drop table {temp_table_name}"

    if len(key) == 1:
        pkey_qry = f"ALTER TABLE {temp_table_name} ADD PRIMARY KEY ({key[0]});"
    else:
        pkey_columns = ", ".join(key)
        pkey_qry = f"ALTER TABLE {temp_table_name} ADD PRIMARY KEY ({pkey_columns});"

    conn_list = []
    for params in td_task.fields.conn_params:
        conn_list.append(psycopg.connect(**params))

    for con in conn_list:
        cur = con.cursor()
        cur.execute(table_qry)
        cur.execute(pkey_qry)
        cur.close()
        con.commit()

    task_id = ace_db.generate_task_id()

    try:
        diff_args = TableDiffTask(
            cluster_name=td_task.cluster_name,
            _table_name=f"public.{temp_table_name}",
            _dbname=td_task._dbname,
            block_rows=td_task.block_rows,
            max_cpu_ratio=td_task.max_cpu_ratio,
            output=td_task.output,
            _nodes=td_task._nodes,
            batch_size=td_task.batch_size,
            quiet_mode=td_task.quiet_mode,
        )
        diff_args.scheduler.task_id = task_id
        diff_task = ace.table_diff_checks(diff_args)
        ace_db.create_ace_task(task=diff_task)
        table_diff(diff_task)
    except AceException as e:
        util.exit_message(str(e))

    for con in conn_list:
        cur = con.cursor()
        cur.execute(clean_qry)
        cur.close()
        con.commit()

    td_task.scheduler.task_status = "COMPLETED"
    td_task.scheduler.finished_at = datetime.now()
    td_task.scheduler.time_taken = diff_task.scheduler.time_taken
    td_task.scheduler.task_context = diff_task.scheduler.task_context
    ace_db.update_ace_task(td_task)


def table_rerun_async(td_task: TableDiffTask) -> None:
    table_types = None

    for params in td_task.fields.conn_params:
        conn = psycopg.connect(**params)
        if not table_types:
            table_types = ace.get_row_types(conn, td_task.fields.l_table)

    # load diff data and validate
    diff_data = json.load(open(td_task.diff_file_path, "r"))
    diff_kset = set()
    diff_keys = list()
    key = td_task.fields.key.split(",")
    simple_primary_key = len(key) == 1

    # Simple pkey
    if simple_primary_key == 1:
        for node_pair in diff_data.keys():
            nd1, nd2 = node_pair.split("/")

            for row in diff_data[node_pair][nd1] + diff_data[node_pair][nd2]:
                if row[key[0]] not in diff_kset:
                    diff_kset.add(row[key[0]])
                    diff_keys.append(row[key[0]])

    # Comp pkey
    else:
        for node_pair in diff_data.keys():
            nd1, nd2 = node_pair.split("/")

            for row in diff_data[node_pair][nd1] + diff_data[node_pair][nd2]:
                element = tuple(row[key_component] for key_component in key)
                if element not in diff_kset:
                    diff_kset.add(element)
                    diff_keys.append(element)

    # create blocks
    total_rows = len(diff_kset) * len(td_task.fields.node_list)
    total_diff = len(diff_keys)

    if total_diff > 100:
        block_size = min(500, total_diff // 10)
        block_nums = ceil(total_diff / block_size)

        blocks = [
            [diff_keys[i * block_size: i * block_size + block_size]]
            for i in range(block_nums)
        ]
    else:
        blocks = [[diff_keys]]

    total_blocks = len(blocks)

    # If we don't have enough blocks to keep all CPUs busy, use fewer processes
    cpus = cpu_count()
    max_procs = int(cpus * td_task.max_cpu_ratio) if cpus > 1 else 1
    procs = max_procs if total_blocks > max_procs else total_blocks

    start_time = datetime.now()

    """
    Generate offsets for each process to work on.
    We go up to the max rows among all nodes because we want our set difference logic
    to capture diffs even if rows are absent in one node
    """

    cols_list = td_task.fields.cols.split(",")
    cols_list = [col for col in cols_list if not col.startswith("_Spock_")]

    # Shared variables needed by all workers
    shared_objects = {
        "cluster_name": td_task.cluster_name,
        "database": td_task.fields.database,
        "node_list": td_task.fields.node_list,
        "schema_name": td_task.fields.l_schema,
        "table_name": td_task.fields.l_table,
        "cols_list": cols_list,
        "p_key": td_task.fields.key,
        "block_rows": td_task.block_rows,
        "simple_primary_key": simple_primary_key,
        "mode": "rerun",
    }

    util.message(
        "Starting jobs to compare tables ...\n",
        p_state="info",
        quiet_mode=td_task.quiet_mode,
    )

    mismatch = False
    diffs_exceeded = False
    errors = False

    with WorkerPool(
        n_jobs=procs,
        shared_objects=shared_objects,
        use_worker_state=True,
        use_dill=True,
    ) as pool:
        for result in pool.imap_unordered(
            compare_checksums,
            make_single_arguments(blocks),
            worker_init=init_db_connection,
            progress_bar=True if not td_task.quiet_mode else False,
            iterable_len=len(blocks),
            progress_bar_style="rich",
        ):
            if result == config.MAX_DIFFS_EXCEEDED:
                diffs_exceeded = True
                mismatch = True
                break
            elif result == config.BLOCK_ERROR:
                errors = True
                break

        if diffs_exceeded:
            util.message(
                "Prematurely terminated jobs since diffs have"
                " exceeded MAX_ALLOWED_DIFFS",
                p_state="warning",
                quiet_mode=td_task.quiet_mode,
            )

    for result in result_queue:
        if result == config.BLOCK_MISMATCH:
            mismatch = True

    if errors:
        raise AceException(
            "There were one or more errors while connecting to databases.\n \
                Please examine the connection information provided, or the nodes' \
                    status before running this script again."
        )

    # Mismatch is True if there is a block mismatch or if we have
    # estimated that diffs may be greater than max allowed diffs
    if mismatch:
        if diffs_exceeded:
            util.message(
                f"TABLES DO NOT MATCH. DIFFS HAVE EXCEEDED {config.MAX_DIFF_ROWS} ROWS",
                p_state="warning",
                quiet_mode=td_task.quiet_mode,
            )

        else:
            util.message(
                "TABLES DO NOT MATCH", p_state="warning", quiet_mode=td_task.quiet_mode
            )

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
                quiet_mode=td_task.quiet_mode,
            )

        if td_task.output == "json":
            td_task.diff_file_path = ace.write_diffs_json(
                diff_dict, table_types, quiet_mode=td_task.quiet_mode
            )

        elif td_task.output == "csv":
            ace.write_diffs_csv()

    else:
        util.message(
            "TABLES MATCH OK\n", p_state="success", quiet_mode=td_task.quiet_mode
        )

    run_time = util.round_timedelta(datetime.now() - start_time).total_seconds()
    run_time_str = f"{run_time:.2f}"

    util.message(
        f"TOTAL ROWS CHECKED = {total_rows}\nRUN TIME = {run_time_str} seconds",
        p_state="info",
        quiet_mode=td_task.quiet_mode,
    )

    td_task.scheduler.task_status = "COMPLETED"
    td_task.scheduler.finished_at = datetime.now()
    td_task.scheduler.time_taken = run_time
    td_task.scheduler.task_context = json.dumps(
        {"total_rows": total_rows, "mismatch": mismatch}
    )
    ace_db.update_ace_task(td_task)


def repset_diff(
    cluster_name,
    repset_name,
    dbname=None,
    block_rows=config.BLOCK_ROWS_DEFAULT,
    max_cpu_ratio=config.MAX_CPU_RATIO_DEFAULT,
    output="json",
    nodes="all",
    quiet=False,
):
    """Loop thru a replication-sets tables and run table-diff on them"""

    quiet_mode = quiet

    if type(block_rows) is str:
        try:
            block_rows = int(block_rows)
        except Exception:
            util.exit_message("Invalid values for ACE_BLOCK_ROWS or --block_rows")
    elif type(block_rows) is not int:
        util.exit_message("Invalid value type for ACE_BLOCK_ROWS or --block_rows")

    # Capping max block size here to prevent the hash function from taking forever
    if block_rows > config.MAX_ALLOWED_BLOCK_SIZE:
        util.exit_message(
            f"Block row size should be <= {config.MAX_ALLOWED_BLOCK_SIZE}"
        )
    if block_rows < config.MIN_ALLOWED_BLOCK_SIZE:
        util.exit_message(
            f"Block row size should be >= {config.MIN_ALLOWED_BLOCK_SIZE}"
        )

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
        util.exit_message(
            "Invalid value range for ACE_MAX_CPU_RATIO or --max_cpu_ratio"
        )

    if output not in ["csv", "json"]:
        util.exit_message(
            "Diff-tables currently supports only csv and json output formats"
        )

    node_list = []
    try:
        node_list = ace.parse_nodes(nodes)
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
    util.message(
        f"Cluster {cluster_name} exists", p_state="success", quiet_mode=quiet_mode
    )

    db, pg, node_info = cluster.load_json(cluster_name)

    cluster_nodes = []
    database = {}

    if dbname:
        for db_entry in db:
            if db_entry["db_name"] == dbname:
                database = db_entry
                break
    else:
        database = db[0]

    if not database:
        util.exit_message(f"Database '{dbname}' not found in cluster '{cluster_name}'")

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
                    user=nd["db_user"],
                    password=nd["db_password"],
                    host=nd["public_ip"],
                    port=nd.get("port", 5432),
                )
                conn_list.append(psql_conn)

    except Exception as e:
        util.exit_message("Error in diff_tbls() Getting Connections:" + str(e), 1)

    util.message(
        "Connections successful to nodes in cluster",
        p_state="success",
        quiet_mode=quiet_mode,
    )

    # Connecting to any one of the nodes in the cluster should suffice
    conn = conn_list[0]
    cur = conn.cursor()

    # Check if repset exists
    sql = "select set_name from spock.replication_set;"
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
            quiet_mode=quiet_mode,
        )

    # Convert fetched rows into a list of strings
    tables = [table[0] for table in tables]

    for table in tables:
        util.message(
            f"\n\nCHECKING TABLE {table}...\n", p_state="info", quiet_mode=quiet_mode
        )
        table_diff(cluster_name, table, quiet=quiet_mode)


def spock_diff(cluster_name, nodes):
    """Compare spock meta data setup on different cluster nodes"""
    node_list = []
    try:
        node_list = ace.parse_nodes(nodes)
    except ValueError as e:
        util.exit_message(
            f'Nodes should be a comma-separated list of nodenames. \
                E.g., --nodes="n1,n2". Error: {e}'
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
                user=nd["db_user"],
                password=nd["db_password"],
                host=nd["public_ip"],
                port=nd.get("port", 5432),
                row_factory=dict_row,
            )
            conn_list[nd["name"]] = psql_conn

    except Exception as e:
        util.exit_message("Error in spock_diff() Getting Connections:" + str(e), 1)

    if len(node_list) > 3:
        util.exit_message(
            "spock-diff currently supports up to a three-way table comparison"
        )

    for nd in node_list:
        if nd not in conn_list.keys():
            util.exit_message(f'Specified nodename "{nd}" not present in cluster', 1)

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
        ace.prCyan("Node:")
        sql = """
        SELECT n.node_id, n.node_name, n.location, n.country,
           s.sub_id, s.sub_name, s.sub_enabled, s.sub_replication_sets
           FROM spock.node n LEFT OUTER JOIN spock.subscription s
           ON s.sub_target=n.node_id WHERE s.sub_name IS NOT NULL;
        """

        cur.execute(sql)
        node_info = cur.fetchall()

        if node_info:
            print("  " + node_info[0]["node_name"])
            diff_spock["node"] = node_info[0]["node_name"]

            ace.prCyan("  Subscriptions:")

            diff_spock["subscriptions"] = []
            for node in node_info:
                diff_sub = {}
                if node["sub_name"] is None:
                    hints.append(
                        "Hint: No subscriptions have been created on this node"
                    )
                else:
                    print("    " + node["sub_name"])
                    diff_sub["sub_name"] = node["sub_name"]
                    diff_sub["sub_enabled"] = node["sub_enabled"]
                    ace.prCyan("    RepSets:")
                    diff_sub["replication_sets"] = node["sub_replication_sets"]
                    print("      " + json.dumps(node["sub_replication_sets"]))
                    if node["sub_replication_sets"] == []:
                        hints.append("Hint: No replication sets added to subscription")
                    diff_spock["subscriptions"].append(diff_sub)

        else:
            print(f"  No node replication in {cluster_node['name']}")

        """
        Query gets each table by which rep set they are in, values in each rep
        set are alphabetized
        """
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
        ace.prCyan("Tables in RepSets:")
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
            ace.prRed(hint)
        print("\n")

    print(" Spock - Diff")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~")
    for n in range(1, len(compare_spock)):
        if compare_spock[0]["rep_set_info"] == compare_spock[n]["rep_set_info"]:
            util.message(
                f"   Replication Rules are the same for {node_list[0]}"
                " and {node_list[n]}!!",
                p_state="success",
            )
        else:
            ace.prRed(
                f"\u2718   Difference in Replication Rules between {node_list[0]}"
                " and {node_list[n]}"
            )


def schema_diff(cluster_name, nodes, schema_name):
    """Compare Postgres schemas on different cluster nodes"""

    util.message(f"## Validating cluster {cluster_name} exists")
    node_list = []
    try:
        node_list = ace.parse_nodes(nodes)
    except ValueError as e:
        util.exit_message(
            f'Nodes should be a comma-separated list of nodenames. \
                E.g., --nodes="n1,n2". Error: {e}'
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

    # Combine db and cluster_nodes into a single json
    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    cluster_node_names = [nd["name"] for nd in cluster_nodes]
    if nodes == "all":
        for nd in cluster_node_names:
            node_list.append(nd)

    if len(node_list) > 3:
        util.exit_message(
            "schema-diff currently supports up to a three-way table comparison"
        )

    for nd in node_list:
        if nd not in cluster_node_names:
            util.exit_message(f'Specified nodename "{nd}" not present in cluster', 1)

    sql1 = ""
    l_schema = schema_name
    file_list = []

    for nd in cluster_nodes:
        if nd["name"] in node_list:
            sql1 = ace.write_pg_dump(
                nd["public_ip"], nd["db_name"], nd["port"], nd["name"], l_schema
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
            ace.prRed(
                f"\u2718   SCHEMAS ARE NOT THE SAME- between {node_list[0]}"
                " and {node_list[n]}!!"
            )
