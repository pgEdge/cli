import ast
import json
from math import ceil
import os
from datetime import datetime
from itertools import combinations
from multiprocessing import Manager, cpu_count
from concurrent.futures import ThreadPoolExecutor

import psycopg
from mpire import WorkerPool
from mpire.utils import make_single_arguments
from ordered_set import OrderedSet
from psycopg import sql
from psycopg.rows import dict_row, class_row
from dateutil import parser

import ace
import ace_db
import cluster
import util
import ace_config as config
from ace_data_models import (
    AutoRepairTask,
    RepsetDiffTask,
    SchemaDiffTask,
    SpockDiffTask,
    TableDiffTask,
    TableRepairTask,
)

from ace_exceptions import AceException


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
        params = {
            "dbname": node["db_name"],
            "user": node["db_user"],
            "password": node["db_password"],
            "host": node["public_ip"],
            "port": node.get("port", 5432),
            "options": f"-c statement_timeout={config.STATEMENT_TIMEOUT}",
        }

        worker_state[node["name"]] = psycopg.connect(**params).cursor()


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


def create_result_dict(
    node_pair,
    pkey_range,
    status_code,
    status_message,
    errors=False,
    error_messages=None,
):
    return {
        "node_pair": node_pair,
        "pkey_range": pkey_range,
        "status_code": status_code,
        "status_message": status_message,
        "errors": errors,
        "error_messages": error_messages or [],
    }


def compare_checksums(shared_objects, worker_state, batches):

    result_queue = shared_objects["result_queue"]
    diff_dict = shared_objects["diff_dict"]
    row_diff_count = shared_objects["row_diff_count"]
    lock = shared_objects["lock"]

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
                result_dict = create_result_dict(
                    node_pair,
                    batch,
                    config.MAX_DIFFS_EXCEEDED,
                    "MAX_DIFFS_EXCEEDED",
                    errors=True,
                    error_messages=[
                        f"Diffs have exceeded the maximum allowed number of diffs:"
                        f"{config.MAX_DIFF_ROWS}"
                    ],
                )
                result_queue.append(result_dict)
                return config.MAX_DIFFS_EXCEEDED

            # Run the checksum query on both nodes in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(run_query, worker_state, host1, hash_sql),
                    executor.submit(run_query, worker_state, host2, hash_sql),
                ]
                results = [f.result() for f in futures if not f.exception()]

            errors = [f.exception() for f in futures if f.exception()]

            if errors:
                result_dict = create_result_dict(
                    node_pair,
                    batch,
                    config.BLOCK_ERROR,
                    "BLOCK_ERROR",
                    errors=True,
                    error_messages=[str(error) for error in errors],
                )
                result_queue.append(result_dict)
                return config.BLOCK_ERROR

            hash1, hash2 = results[0][0][0], results[1][0][0]

            if hash1 != hash2:
                # Run the block query on both nodes in parallel
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(run_query, worker_state, host1, block_sql),
                        executor.submit(run_query, worker_state, host2, block_sql),
                    ]
                    results = [f.result() for f in futures if not f.exception()]

                errors = [f.exception() for f in futures if f.exception()]

                if errors:
                    result_dict = create_result_dict(
                        node_pair,
                        batch,
                        config.BLOCK_ERROR,
                        "BLOCK_ERROR",
                        errors=True,
                        error_messages=[str(error) for error in errors],
                    )
                    result_queue.append(result_dict)
                    return config.BLOCK_ERROR

                t1_result, t2_result = results

                # Transform all elements in t1_result and t2_result into strings before
                # consolidating them into a set
                # TODO: Test and add support for different datatypes here
                t1_result = [tuple(str(x) for x in row) for row in t1_result]
                t2_result = [tuple(str(x) for x in row) for row in t2_result]

                # Collect results into OrderedSets for comparison
                t1_set = OrderedSet(t1_result)
                t2_set = OrderedSet(t2_result)

                t1_diff = t1_set - t2_set
                t2_diff = t2_set - t1_set

                node_pair_key = f"{host1}/{host2}"

                if node_pair_key not in diff_dict:
                    diff_dict[node_pair_key] = {}

                with lock:
                    # Update diff_dict with the results of the diff
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

                    # Update row_diff_count with the number of diffs
                    row_diff_count.value += max(len(t1_diff), len(t2_diff))

                if row_diff_count.value >= config.MAX_DIFF_ROWS:
                    result_dict = create_result_dict(
                        node_pair,
                        batch,
                        config.MAX_DIFFS_EXCEEDED,
                        "MAX_DIFFS_EXCEEDED",
                        errors=True,
                        error_messages=[
                            f"Diffs have exceeded the maximum allowed number of diffs:"
                            f"{config.MAX_DIFF_ROWS}"
                        ],
                    )
                    result_queue.append(result_dict)
                    return config.MAX_DIFFS_EXCEEDED
                else:
                    result_dict = create_result_dict(
                        node_pair, batch, config.BLOCK_MISMATCH, "BLOCK_MISMATCH"
                    )
                    result_queue.append(result_dict)
            else:
                result_dict = create_result_dict(
                    node_pair, batch, config.BLOCK_OK, "BLOCK_OK"
                )
                result_queue.append(result_dict)


def table_diff(td_task: TableDiffTask):
    """Efficiently compare tables across cluster using checksums and blocks of rows"""

    global result_queue, diff_dict, row_diff_count

    simple_primary_key = True
    if len(td_task.fields.key.split(",")) > 1:
        simple_primary_key = False

    row_count = 0
    total_rows = 0
    conn_with_max_rows = None
    table_types = None

    try:
        for params in td_task.fields.conn_params:
            conn = psycopg.connect(**params)
            if not table_types:
                table_types = ace.get_row_types(conn, td_task.fields.l_table)

            rows = ace.get_row_count(
                conn, td_task.fields.l_schema, td_task.fields.l_table
            )
            total_rows += rows
            if rows > row_count:
                row_count = rows
                conn_with_max_rows = conn
    except Exception as e:
        context = {"total_rows": total_rows, "mismatch": False, "errors": [str(e)]}
        ace.handle_task_exception(td_task, context)
        raise e

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
    pkey_offsets = future.result() if not future.exception() else []
    if future.exception():
        context = {
            "total_rows": total_rows,
            "mismatch": False,
            "errors": [str(future.exception())],
        }
        ace.handle_task_exception(td_task, context)
        raise future.exception()

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

    # Shared multiprocessing data structures
    result_queue = Manager().list()
    diff_dict = Manager().dict()
    row_diff_count = Manager().Value("I", 0)
    lock = Manager().Lock()

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
        "result_queue": result_queue,
        "diff_dict": diff_dict,
        "row_diff_count": row_diff_count,
        "lock": lock,
    }

    util.message(
        "Starting jobs to compare tables...\n",
        p_state="info",
        quiet_mode=td_task.quiet_mode,
    )

    batches = [
        pkey_offsets[i : i + td_task.batch_size]
        for i in range(0, len(pkey_offsets), td_task.batch_size)
    ]

    mismatch = False
    diffs_exceeded = False
    errors = False
    error_list = []

    try:
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
    except Exception as e:
        context = {"total_rows": total_rows, "mismatch": mismatch, "errors": [str(e)]}
        ace.handle_task_exception(td_task, context)
        raise e

    for result in result_queue:
        if result["status_code"] == config.BLOCK_MISMATCH:
            mismatch = True
        elif result["status_code"] == config.BLOCK_ERROR:
            errors = True
            error_list.append(result)

    if errors:
        context = {"total_rows": total_rows, "mismatch": mismatch, "errors": error_list}
        ace.handle_task_exception(td_task, context)

        # Even though we've updated the task in the DB, we still need to
        # raise an exception so that a) it comes up in the CLI and b) we
        # have a record of it in the logs
        raise AceException(
            "There were one or more errors while running the table-diff job. \n"
            "Please examine the connection information provided, or the nodes' \n"
            "status before running this script again. Error list: \n"
            f"{error_list}"
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

        try:
            if td_task.output == "json":
                td_task.diff_file_path = ace.write_diffs_json(
                    diff_dict, table_types, quiet_mode=td_task.quiet_mode
                )
            elif td_task.output == "csv":
                ace.write_diffs_csv(diff_dict)
        except Exception as e:
            context = {
                "total_rows": total_rows,
                "mismatch": mismatch,
                "errors": [str(e)],
            }
            ace.handle_task_exception(td_task, context)
            raise e

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
    td_task.scheduler.task_context = {
        "total_rows": total_rows,
        "mismatch": mismatch,
        "errors": [],
    }

    if not td_task.skip_db_update:
        ace_db.update_ace_task(td_task)

    return td_task


def table_repair(tr_task: TableRepairTask):
    """Apply changes from a table-diff source of truth to destination table"""

    start_time = datetime.now()
    conns = {}

    try:
        for params in tr_task.fields.conn_params:
            conns[tr_task.fields.host_map[params["host"] + ":" + params["port"]]] = (
                psycopg.connect(**params)
            )
    except Exception as e:
        context = {"errors": [str(e)]}
        ace.handle_task_exception(tr_task, context)
        raise e

    if tr_task.generate_report:
        report = dict()
        now = datetime.now()
        report["operation_type"] = "table-repair"
        report["mode"] = "LIVE-RUN"
        report["time_stamp"] = (
            now.strftime("%Y-%m-%d %H:%M:%S") + f"{now.microsecond // 1000:03d}"
        )
        report["supplied_args"] = {
            "cluster_name": tr_task.cluster_name,
            "diff_file": tr_task.diff_file_path,
            "source_of_truth": tr_task.source_of_truth,
            "table_name": tr_task._table_name,
            "dbname": tr_task._dbname,
            "dry_run": tr_task.dry_run,
            "quiet": tr_task.quiet_mode,
            "upsert_only": tr_task.upsert_only,
            "generate_report": tr_task.generate_report,
        }
        report["database_credentials_used"] = tr_task.fields.database
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
    except Exception as e:
        context = {"errors": [f"Could not load diff file as JSON: {str(e)}"]}
        ace.handle_task_exception(tr_task, context)
        raise e

    try:
        if any(
            [
                set(list(diff_json[k].keys())) != set(k.split("/"))
                for k in diff_json.keys()
            ]
        ):
            raise AceException("Contents of diff file improperly formatted")

        diff_json = {
            node_pair: {
                node: [{key: str(val) for key, val in row.items()} for row in rows]
                for node, rows in nodes_data.items()
            }
            for node_pair, nodes_data in diff_json.items()
        }
    except Exception as e:
        context = {"errors": [f"Could not read diff file: {str(e)}"]}
        ace.handle_task_exception(tr_task, context)
        raise e

    # Remove metadata columsn "_Spock_CommitTS_" and "_Spock_CommitOrigin_"
    # from cols_list
    cols_list = tr_task.fields.cols.split(",")
    cols_list = [col for col in cols_list if not col.startswith("_Spock_")]

    simple_primary_key = True
    keys_list = []
    if len(tr_task.fields.key.split(",")) > 1:
        simple_primary_key = False
        keys_list = tr_task.fields.key.split(",")
    else:
        simple_primary_key = True
        keys_list = [tr_task.fields.key]

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

    full_rows_to_upsert = dict()
    full_rows_to_delete = dict()
    other_nodes = set()

    for node_pair, node_data in diff_json.items():
        node1, node2 = node_pair.split("/")

        if node1 == tr_task.source_of_truth:
            pass
        elif node2 == tr_task.source_of_truth:
            node2 = node1
            node1 = tr_task.source_of_truth
        else:
            continue

        other_nodes.add(node2)
        main_rows = {
            tuple(row[key] for key in keys_list): row for row in node_data[node1]
        }
        side_rows = {
            tuple(row[key] for key in keys_list): row for row in node_data[node2]
        }

        full_rows_to_upsert[node2] = main_rows
        full_rows_to_delete[node2] = {
            key: val for key, val in side_rows.items() if key not in main_rows
        }

    """
    Format of full_rows_to_upsert = {
        'node2': {
            pkey to upsert: full row of pkey ...
        },
        'node3: {
            pkey to upsert: full row of pkey ...
        },
    }

    Format of full_rows_to_delete = {
        'node2': {
            pkey to delete: full row of pkey ...
        },
        'node3: {
            pkey to delete: full row of pkey ...
        },
    }

    Format of other_nodes = {
        node1,
        node2,
    }
    """

    if tr_task.dry_run:
        dry_run_msg = "######## DRY RUN ########\n\n"
        for node in other_nodes:
            if not tr_task.upsert_only:
                dry_run_msg += (
                    "Repair would have attempted to upsert "
                    + f"{len(full_rows_to_upsert[node])} rows and delete "
                    + f"{len(full_rows_to_delete[node])} rows on { node }\n"
                )
            else:
                dry_run_msg += (
                    "Repair would have attempted to upsert "
                    + f"{len(full_rows_to_upsert[node])} rows on { node }\n"
                )

                if len(full_rows_to_delete[node]) > 0:
                    dry_run_msg += (
                        "There are an additional "
                        + f"{len(full_rows_to_delete[node])} rows on { node }"
                        + f" not present on { tr_task.source_of_truth }\n"
                    )
        dry_run_msg += "\n######## END DRY RUN ########"

        util.message(dry_run_msg, p_state="alert", quiet_mode=tr_task.quiet_mode)
        return

    total_upserted = {}
    total_deleted = {}

    # Gets types of each column in table
    try:
        table_types = ace.get_row_types(
            conns[tr_task.source_of_truth],
            tr_task.fields.l_table,
        )
    except Exception as e:
        context = {"errors": [f"Could not get row types: {str(e)}"]}
        ace.handle_task_exception(tr_task, context)
        raise e

    if tr_task.upsert_only:
        deletes_skipped = dict()

    for divergent_node in other_nodes:

        rows_to_upsert_json = full_rows_to_upsert[divergent_node].values()
        delete_keys = list(full_rows_to_delete[divergent_node].keys())

        """
        Here we are constructing an UPSERT query from true_rows and
        applying it to all nodes
        """

        table_name_sql = f'{tr_task.fields.l_schema}."{tr_task.fields.l_table}"'
        if simple_primary_key:
            update_sql = f"""
            INSERT INTO {table_name_sql}
            VALUES ({','.join(['%s'] * len(cols_list))})
            ON CONFLICT ("{tr_task.fields.key}") DO UPDATE SET
            """
        else:
            update_sql = f"""
            INSERT INTO {table_name_sql}
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
            DELETE FROM {table_name_sql}
            WHERE "{tr_task.fields.key}" = %s;
            """
        else:
            delete_sql = f"""
            DELETE FROM {table_name_sql}
            WHERE
            """

            for k in keys_list:
                delete_sql += f' "{k}" = %s AND'

            delete_sql = delete_sql[:-3] + ";"

        try:
            conn = conns[divergent_node]
            cur = conn.cursor()
            spock_version = ace.get_spock_version(conn)

            # FIXME: Do not use harcoded version numbers
            # Read required version numbers from a config file
            if spock_version >= 4.0:
                cur.execute("SELECT spock.repair_mode(true);")
        except Exception as e:
            context = {"errors": [f"Could not set repair mode: {str(e)}"]}
            ace.handle_task_exception(tr_task, context)
            raise e

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
        try:
            cur.executemany(update_sql, upsert_tuples)
            if tr_task.generate_report:
                report["changes"][divergent_node]["upserted_rows"] = [
                    dict(zip(cols_list, tup)) for tup in upsert_tuples
                ]

            if delete_keys and not tr_task.upsert_only:
                # Performing the deletes
                cur.executemany(delete_sql, delete_keys)
                if tr_task.generate_report:
                    report["changes"][divergent_node]["deleted_rows"] = delete_keys
            elif delete_keys and tr_task.upsert_only:
                deletes_skipped[divergent_node] = delete_keys

            if spock_version >= 4.0:
                cur.execute("SELECT spock.repair_mode(false);")

            conn.commit()
        except Exception as e:
            context = {"errors": [f"Could not perform repairs: {str(e)}"]}
            ace.handle_task_exception(tr_task, context)
            raise e

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
        f"Successfully applied diffs to {tr_task._table_name} in cluster "
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

        try:
            json.dump(report, open(filename, "w"), default=str, indent=2)
        except Exception as e:
            context = {"errors": [f"Could not write report: {str(e)}"]}
            ace.handle_task_exception(tr_task, context)
            raise e

        print(f"Wrote report to {filename}")

    util.message("*** SUMMARY ***\n", p_state="info", quiet_mode=tr_task.quiet_mode)

    for node in other_nodes:
        util.message(
            f"{node} UPSERTED = {len(full_rows_to_upsert[node])} rows",
            p_state="info",
            quiet_mode=tr_task.quiet_mode,
        )

    print()

    for node in other_nodes:
        util.message(
            f"{node} DELETED = {len(full_rows_to_delete[node])} rows",
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

    try:
        for params in td_task.fields.conn_params:
            conn_list.append(psycopg.connect(**params))

        for con in conn_list:
            cur = con.cursor()
            cur.execute(table_qry)
            cur.execute(pkey_qry)
            cur.close()
            con.commit()
    except Exception as e:
        context = {"errors": [f"Could not create temp table: {str(e)}"]}
        ace.handle_task_exception(td_task, context)
        raise e

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
    except Exception as e:
        context = {"errors": [f"Could not run table diff: {str(e)}"]}
        ace.handle_task_exception(td_task, context)
        raise e

    try:
        for con in conn_list:
            cur = con.cursor()
            cur.execute(clean_qry)
            cur.close()
            con.commit()
    except Exception as e:
        context = {"errors": [f"Could not clean up temp table: {str(e)}"]}
        ace.handle_task_exception(td_task, context)
        raise e

    td_task.scheduler.task_status = "COMPLETED"
    td_task.scheduler.finished_at = datetime.now()
    td_task.scheduler.time_taken = diff_task.scheduler.time_taken
    td_task.scheduler.task_context = diff_task.scheduler.task_context
    ace_db.update_ace_task(td_task)


def table_rerun_async(td_task: TableDiffTask) -> None:
    table_types = None

    try:
        for params in td_task.fields.conn_params:
            conn = psycopg.connect(**params)
            if not table_types:
                table_types = ace.get_row_types(conn, td_task.fields.l_table)
    except Exception as e:
        context = {"errors": [f"Could not connect to nodes: {str(e)}"]}
        ace.handle_task_exception(td_task, context)
        raise e

    # load diff data and validate
    try:
        diff_data = json.load(open(td_task.diff_file_path, "r"))
    except Exception as e:
        context = {"errors": [f"Could not read diff file: {str(e)}"]}
        ace.handle_task_exception(td_task, context)
        raise e

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
            [diff_keys[i * block_size : i * block_size + block_size]]
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

    result_queue = Manager().list()
    diff_dict = Manager().dict()
    row_diff_count = Manager().Value("I", 0)
    lock = Manager().Lock()

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
        "result_queue": result_queue,
        "diff_dict": diff_dict,
        "row_diff_count": row_diff_count,
        "lock": lock,
    }

    util.message(
        "Starting jobs to compare tables ...\n",
        p_state="info",
        quiet_mode=td_task.quiet_mode,
    )

    mismatch = False
    diffs_exceeded = False
    errors = False
    errors_list = []

    try:
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
                    errors_list.append(result)
                    break

            if diffs_exceeded:
                util.message(
                    "Prematurely terminated jobs since diffs have"
                    " exceeded MAX_ALLOWED_DIFFS",
                    p_state="warning",
                    quiet_mode=td_task.quiet_mode,
                )
    except Exception as e:
        context = {"errors": [f"Could not spawn multiprocessing workers: {str(e)}"]}
        ace.handle_task_exception(td_task, context)
        raise e

    for result in result_queue:
        if result["status_code"] == config.BLOCK_MISMATCH:
            mismatch = True

    if errors:
        context = {
            "total_rows": total_rows,
            "mismatch": mismatch,
            "errors": errors_list,
        }
        ace.handle_task_exception(td_task, context)
        raise AceException(
            "There were one or more errors while connecting to databases."
            "Please examine the connection information provided, or the nodes"
            "status before running this script again."
            f"Errors: {errors_list}"
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

        try:
            if td_task.output == "json":
                td_task.diff_file_path = ace.write_diffs_json(
                    diff_dict, table_types, quiet_mode=td_task.quiet_mode
                )

            elif td_task.output == "csv":
                ace.write_diffs_csv()
        except Exception as e:
            context = {"errors": [f"Could not write diffs to file: {str(e)}"]}
            ace.handle_task_exception(td_task, context)
            raise e

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


def repset_diff(rd_task: RepsetDiffTask) -> None:
    """Loop thru a replication-sets tables and run table-diff on them"""

    rd_task_context = []
    rd_start_time = datetime.now()
    errors_encountered = False

    for table in rd_task.table_list:

        if table.split(".")[1] in rd_task.skip_tables:
            util.message(
                f"\nSKIPPING TABLE {table}",
                p_state="info",
                quiet_mode=rd_task.quiet_mode,
            )

            continue

        try:
            start_time = datetime.now()
            util.message(
                f"\n\nCHECKING TABLE {table}...\n",
                p_state="info",
                quiet_mode=rd_task.quiet_mode,
            )

            td_task = TableDiffTask(
                cluster_name=rd_task.cluster_name,
                _table_name=table,
                _dbname=rd_task._dbname,
                fields=rd_task.fields,
                quiet_mode=rd_task.quiet_mode,
                block_rows=rd_task.block_rows,
                max_cpu_ratio=rd_task.max_cpu_ratio,
                output=rd_task.output,
                _nodes=rd_task._nodes,
                batch_size=rd_task.batch_size,
                skip_db_update=True,
            )

            td_task = ace.table_diff_checks(td_task)
            td_task = table_diff(td_task)
            run_time = util.round_timedelta(datetime.now() - start_time).total_seconds()
            status = {
                "table": table,
                "status": "COMPLETED",
                "time_taken": run_time,
                "total_rows": td_task.scheduler.task_context["total_rows"],
                "mismatch": td_task.scheduler.task_context["mismatch"],
                "diff_file_path": getattr(td_task, "diff_file_path", None),
            }
        except Exception as e:
            errors_encountered = True
            status = {
                "table": table,
                "status": "FAILED",
                "error": str(e),
            }
            util.message(
                f"Repset-diff failed for table {table} with: {str(e)}",
                p_state="warning",
            )

        rd_task_context.append(status)

    rd_task.scheduler.task_status = "COMPLETED" if not errors_encountered else "FAILED"
    rd_task.scheduler.finished_at = datetime.now()
    rd_task.scheduler.task_context = rd_task_context
    rd_task.scheduler.time_taken = util.round_timedelta(
        datetime.now() - rd_start_time
    ).total_seconds()

    ace_db.update_ace_task(rd_task)


def spock_diff(sd_task: SpockDiffTask) -> None:
    """Compare spock meta data setup on different cluster nodes"""

    conns = {}
    compare_spock = []
    task_context = {}
    sd_start_time = datetime.now()

    print("\n")

    try:
        for params in sd_task.fields.conn_params:
            conns[sd_task.fields.host_map[params["host"] + ":" + params["port"]]] = (
                psycopg.connect(**params, row_factory=dict_row)
            )
    except Exception as e:
        context = {"errors": [f"Could not connect to nodes: {str(e)}"]}
        ace.handle_task_exception(sd_task, context)
        raise e

    try:
        for cluster_node in sd_task.fields.cluster_nodes:
            cur = conns[cluster_node["name"]].cursor()

            if (
                sd_task.fields.node_list
                and cluster_node["name"] not in sd_task.fields.node_list
            ):
                continue

            diff_spock = {}
            hints = []
            print(" Spock - Config " + cluster_node["name"])
            print("~~~~~~~~~~~~~~~~~~~~~~~~~")
            ace.prCyan("Node:")

            sql = """
            SELECT
                n.node_id,
                n.node_name,
                n.location,
                n.country,
                s.sub_id,
                s.sub_name,
                s.sub_enabled,
                s.sub_replication_sets
            FROM spock.node n
            LEFT OUTER JOIN spock.subscription s
            ON s.sub_target = n.node_id
            WHERE s.sub_name IS NOT NULL;
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
                            hints.append(
                                "Hint: No replication sets added to" " subscription"
                            )
                        diff_spock["subscriptions"].append(diff_sub)

            else:
                print(f"  No node replication in {cluster_node['name']}")

            """
            Query gets each table by which rep set they are in, values in each rep
            set are alphabetized
            """
            repset_sql = """
            SELECT
            set_name,
            array_agg(nspname || '.' || relname ORDER BY nspname, relname) as relname
            FROM (
                SELECT
                    set_name,
                    nspname,
                    relname
                FROM spock.tables
                ORDER BY set_name, nspname, relname
            ) subquery
            GROUP BY set_name
            ORDER BY set_name;
            """

            cur.execute(repset_sql)
            table_info = cur.fetchall()
            diff_spock["rep_set_info"] = []
            ace.prCyan("Tables in RepSets:")
            if table_info == []:
                hints.append("Hint: No tables in database")
            for table in table_info:
                if table["set_name"] is None:
                    print(" - Not in a replication set")
                    hints.append(
                        "Hint: Tables not in replication set might not have"
                        "primary keys, or you need to run repset-add-table"
                    )
                else:
                    print(" - " + table["set_name"])

                diff_spock["rep_set_info"].append({table["set_name"]: table["relname"]})
                print("   - ", table["relname"])

            diff_spock["hints"] = hints
            compare_spock.append(diff_spock)

            for hint in hints:
                ace.prRed(hint)
            print("\n")

    except Exception as e:
        context = {"errors": [f"Error while comparing Spock meta data: {str(e)}"]}
        ace.handle_task_exception(sd_task, context)
        raise e

    task_context["spock_config"] = compare_spock
    task_context["diffs"] = {}

    print(" Spock - Diff")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~")

    for n in range(1, len(compare_spock)):
        diff_key = compare_spock[0]["node"] + "/" + compare_spock[n]["node"]
        if compare_spock[0]["rep_set_info"] == compare_spock[n]["rep_set_info"]:
            task_context["diffs"][diff_key] = {
                "mismatch": False,
                "message": "Replication sets are the same between nodes "
                f"{compare_spock[0]['node']} and {compare_spock[n]['node']}",
            }
            util.message(
                f"   Replication Rules are the same for {compare_spock[0]['node']}"
                f" and {compare_spock[n]['node']}",
                p_state="success",
            )
        else:
            task_context["diffs"][diff_key] = {
                "mismatch": True,
                "message": "Replication sets are different in nodes "
                f"{compare_spock[0]['node']} and {compare_spock[n]['node']}",
            }
            ace.prRed(
                f"\u2718   Difference in Replication Rules between"
                f" {compare_spock[0]['node']} and {compare_spock[n]['node']}"
            )

    sd_task.scheduler.task_status = "COMPLETED"
    sd_task.scheduler.finished_at = datetime.now()
    sd_task.scheduler.time_taken = util.round_timedelta(
        datetime.now() - sd_start_time
    ).total_seconds()
    sd_task.scheduler.task_context = task_context
    ace_db.update_ace_task(sd_task)

    return task_context


def schema_diff(sc_task: SchemaDiffTask) -> None:
    """Compare Postgres schemas on different cluster nodes"""

    sql1 = ""
    l_schema = sc_task.schema_name
    file_list = []
    task_context = {}

    sc_task_start_time = datetime.now()

    try:
        for nd in sc_task.fields.cluster_nodes:
            if nd["name"] in sc_task.fields.node_list:
                sql1 = ace.write_pg_dump(
                    nd["public_ip"], nd["db_name"], nd["port"], nd["name"], l_schema
                )
                file_list.append(sql1)
    except Exception as e:
        context = {"errors": [f"Could not connect to nodes: {str(e)}"]}
        ace.handle_task_exception(sc_task, context)
        raise e

    if os.stat(file_list[0]).st_size == 0:
        context = {
            "errors": [
                f"Schema {sc_task.schema_name} does not exist on node "
                f"{sc_task.fields.node_list[0]}"
            ]
        }
        ace.handle_task_exception(sc_task, context)
        raise AceException(
            f"Schema {sc_task.schema_name} does not exist on node "
            f"{sc_task.fields.node_list[0]}"
        )

    try:
        for n in range(1, len(file_list)):
            cmd = "diff " + file_list[0] + "  " + file_list[n] + " > /tmp/diff.txt"
            util.message("\n## Running # " + cmd + "\n")
            rc = os.system(cmd)
            if os.stat(file_list[n]).st_size == 0:
                raise AceException(
                    f"Schema {sc_task.schema_name} does not exist on node "
                    f"{sc_task.fields.node_list[n]}"
                )
            context_key = (
                sc_task.fields.node_list[0] + "/" + sc_task.fields.node_list[n]
            )
            if rc == 0:
                task_context[context_key] = {
                    "mismatch": False,
                    "message": f"Schemas are the same between "
                    f"{sc_task.fields.node_list[0]} and {sc_task.fields.node_list[n]}",
                }
                util.message(
                    f"SCHEMAS ARE THE SAME- between {sc_task.fields.node_list[0]} "
                    f"and {sc_task.fields.node_list[n]} !!",
                    p_state="success",
                )
            else:
                task_context[context_key] = {
                    "mismatch": True,
                    "message": f"Schemas are different between "
                    f"{sc_task.fields.node_list[0]} and {sc_task.fields.node_list[n]}",
                }
                ace.prRed(
                    f"\u2718   SCHEMAS ARE NOT THE SAME- between "
                    f"{sc_task.fields.node_list[0]}"
                    f" and {sc_task.fields.node_list[n]}!!"
                )
    except Exception as e:
        context = {"errors": [f"Error while comparing schemas: {str(e)}"]}
        ace.handle_task_exception(sc_task, context)
        raise e

    sc_task.scheduler.task_status = "COMPLETED"
    sc_task.scheduler.finished_at = datetime.now()
    sc_task.scheduler.time_taken = util.round_timedelta(
        datetime.now() - sc_task_start_time
    ).total_seconds()
    sc_task.scheduler.task_context = {"diffs": task_context}

    ace_db.update_ace_task(sc_task)


def update_spock_exception(entry: dict, conn: psycopg.Connection) -> None:

    remote_origin = entry.get("remote_origin", None)
    remote_commit_ts = entry.get("remote_commit_ts", None)
    remote_xid = entry.get("remote_xid", None)
    status = entry.get("status", None)
    resolution_details = entry.get("resolution_details", None)
    command_counter = entry.get("command_counter", None)

    try:
        if not command_counter:
            """
            If the command_counter is not specified, we are not only updating the
            exception status in spock.exception_status, but also all exceptions
            that belong to this trio of (remote_origin, remote_commit_ts, remote_xid)
            """

            # We will first update spock.exception_status here
            update_sql = """
            UPDATE spock.exception_status
            SET status = %s,
                resolution_details = %s,
                resolved_at = %s
            WHERE remote_origin = %s
                AND remote_commit_ts = %s
                AND remote_xid = %s;
            """

            params = (
                status,
                json.dumps(resolution_details),
                datetime.now(),
                remote_origin,
                remote_commit_ts,
                remote_xid,
            )

            cur = conn.cursor()
            cur.execute(update_sql, params)

            # Now we will update all exceptions that belong to this trio
            update_sql = """
            UPDATE spock.exception_status_detail
            SET status = %s,
                resolution_details = %s,
                resolved_at = %s
            WHERE remote_origin = %s
                AND remote_commit_ts = %s
                AND remote_xid = %s;
            """

            cur.execute(update_sql, params)
            conn.commit()

        else:
            """
            If the command_counter is specified, we are only updating the
            exception status in spock.exception_status_detail
            """

            update_sql = """
            UPDATE spock.exception_status_detail
            SET status = %s,
                resolution_details = %s,
                resolved_at = %s
            WHERE command_counter = %s
                AND remote_origin = %s
                AND remote_commit_ts = %s
                AND remote_xid = %s;
            """

            params = (
                status,
                json.dumps(resolution_details),
                datetime.now(),
                command_counter,
                remote_origin,
                remote_commit_ts,
                remote_xid,
            )

            cur = conn.cursor()
            cur.execute(update_sql, params)
            conn.commit()

    except Exception as e:
        raise AceException(f"Error while updating exception status: {str(e)}")


# TODO:
# - Simple and composite primary keys
# - Datatypes
# - Quoted column names
# - Quoted table names
def auto_repair():
    """
    This is the core function that orchestrates the auto-repair process. The
    auto-repair feature periodically polls the exception_log table, runs a
    table-diff against the remote_origin node, and attempts to repair the
    exception by making a decision on which node to use as the source of truth.
    We only need the cluster_name here, since we need to query each node for the
    exception_log and take action depending on it.

    The tricky part here is deciding which node to use as the source of truth. It
    is worth noting here that this decision, for now (the ACE 2.0 release), will
    only happen for INSERT/UPDATE/DELETE exceptions. Why? Handling auto-ddl and
    other exception types is far more complex, and will be implemented in a
    future release.

    Let us now look at the INSERT/UPDATE/DELETE scenarios:

        INSERT:
        An insert operation can error out on a subscriber if the row with the
        same primary key or unique constraint already exists on the subscriber.
        In such a scenario, the subscriber node could either be ahead or behind
        the origin node. Since we cannot make this distinction, we need to adopt
        a different strategy for choosing the source of truth.

        UPDATE:
        An update transaction coming from a remote_origin can error out on a
        subscriber if the original row to be updated is not yet available, or no
        longer exists. If it is not yet available, we can simply use the
        remote_origin node as the source of truth during repair. However, if it
        is no longer available, we can't know if the subscriber node is ahead or
        behind the origin node. Not only is this an issue, determining if the row
        is as yet unavailable, or if it is no longer available (because of a
        local or a remote delete), is non-trivial.

        DELETE:
        It's the same case for deletes. We can't ascertain if the row is as yet
        unavailable, or if it is no longer available (because of a local or a
        remote delete), or if the row was locally inserted and not yet committed.
        However, a saving grace here is that we do not need to make this
        distinction. Why? Because in the current version of Spock (4.0.1), there
        is no global ordering of transactions. It is possible for a delete
        transaction that happened after an insert/update transaction (on the
        cluster level) to be processed before the insert/update transaction, thus
        resulting in an incorrect end state for the cluster. That is why, we can
        avoid making this distinction.

    So, how do we tackle this? In all three cases above, we have uncertainties
    that prevent us from definitively determining the source of truth. However,
    we have certain functions that can help us make this decision. Specifically,
    it's the spock.xact_commit_timestamp_origin() function. This function returns
    the commit timestamp, as well as the origin node of a transaction. With this,
    here's a strategy we can employ:

        INSERT:
        We can use the spock.xact_commit_timestamp_origin() function to get the
        commit timestamp of the transaction. With this, we simply need compare
        the local commit timestamp with the origin commit timestamp to determine
        the source of truth.

        UPDATE/DELETE:
        TBD
    """

    cluster_name = config.auto_repair_config["cluster_name"]
    dbname = config.auto_repair_config["dbname"]

    # We have already run the necessary checks, so we can proceed here.
    db, pg, node_info = cluster.load_json(cluster_name)

    cluster_nodes = []
    combined_json = {}
    database = next(
        (db_entry for db_entry in db if db_entry["db_name"] == dbname), None
    )

    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    get_exception_sql = """
    SELECT
        el.remote_origin,
        el.remote_commit_ts,
        el.command_counter,
        el.remote_xid,
        el.local_origin,
        el.local_commit_ts,
        el.table_schema,
        el.table_name,
        el.operation,
        el.local_tup,
        el.remote_old_tup,
        el.remote_new_tup,
        el.ddl_statement,
        el.ddl_user,
        el.error_message,
        el.retry_errored_at
    FROM
        spock.exception_log el
    INNER JOIN
        spock.exception_status_detail esd
    ON
        el.remote_origin = esd.remote_origin
        AND el.remote_commit_ts = esd.remote_commit_ts
        AND el.remote_xid = esd.remote_xid
        AND esd.status = 'PENDING';
    """

    commit_timestamp_sql = """
    SELECT
    spock.xact_commit_timestamp_origin(%s::xid)
    """

    oid_sql = """
    SELECT
        node_id,
        node_name
    FROM
        spock.node;
    """

    # We will construct a dictionary to map OIDs to node names
    oid_to_node_name = {}
    conn_map = {}

    for node in cluster_nodes:
        params = {
            "dbname": node["db_name"],
            "host": node["public_ip"],
            "port": node["port"],
            "user": node["db_user"],
            "password": node["db_password"],
            "options": f"-c statement_timeout={config.STATEMENT_TIMEOUT}",
        }
        try:
            conn_map[node["name"]] = psycopg.connect(**params)
            cur = conn_map[node["name"]].cursor(row_factory=dict_row)
            cur.execute(oid_sql)
            oid_to_node_name = {
                row["node_id"]: row["node_name"] for row in cur.fetchall()
            }
        except Exception as e:
            raise AceException(f"Error while getting OIDs: {str(e)}")

    for node in cluster_nodes:
        try:
            conn = conn_map[node["name"]]
            cur = conn.cursor(row_factory=class_row(AutoRepairTask))
            cur.execute(get_exception_sql)
            exceptions = cur.fetchall()
        except Exception as e:
            raise AceException(f"Error while getting exceptions: {str(e)}")

        for exception in exceptions:
            pkey = ace.get_key(conn, exception.table_schema, exception.table_name)
            # We handle only INSERT exceptions for now
            if exception.operation != "INSERT":
                continue

            # We will first get the local commit timestamp of the transaction
            # that created the record and eventually caused the exception.

            xmin_sql = f"""
            SELECT
                xmin
            FROM
                {exception.table_schema}.{exception.table_name}
            WHERE
                {pkey} = {next((tup['value'] 
                                for tup in exception.remote_new_tup
                                if tup['attname'] == pkey), None)}
            """

            local_commit_ts = None

            try:
                cur = conn.cursor()
                cur.execute(xmin_sql)
                xmin = cur.fetchone()[0]
                print(f"XMIN: {xmin}")
                cur.execute(commit_timestamp_sql, (str(xmin),))
                local_commit_ts = parser.parse(cur.fetchone()[0][0])
                print(f"Local commit timestamp: {local_commit_ts}")
            except Exception as e:
                raise AceException(
                    f"Error while getting local commit timestamp: {str(e)}"
                )

            # Now, we can compare local_commit_ts and remote_commit_ts
            if local_commit_ts < exception.remote_commit_ts:
                # The local node is behind the origin node
                # We will use the origin node as the source of truth

                # The remote_new_tup will have
                # {"value": ..., "attname": ..., "atttype": ...}
                # We need to convert this to a tuple that can be used to update
                # the local row

                # XXX: Handle composite primary keys and quoted stuff!
                update_sql = f"""
                UPDATE {exception.table_schema}.{exception.table_name}
                SET {", ".join([f"{tup['attname']} = {tup['value']}"
                                for tup in exception.remote_new_tup])}
                WHERE {pkey} = {next((tup['value'] 
                                for tup in exception.remote_new_tup
                                if tup['attname'] == pkey), None)}
                """

                try:
                    cur = conn.cursor()
                    cur.execute(update_sql)
                    conn.commit()
                except Exception as e:
                    raise AceException(f"Error while updating local table: {str(e)}")

                # Now, we need to update the exception status to "RESOLVED"
                update_exception_status_sql = """
                UPDATE spock.exception_status_detail
                SET status = 'RESOLVED'
                WHERE remote_origin = %s
                    AND remote_commit_ts = %s
                    AND remote_xid = %s;
                """

                try:
                    cur = conn.cursor()
                    cur.execute(
                        update_exception_status_sql,
                        (
                            exception.remote_origin,
                            exception.remote_commit_ts,
                            exception.remote_xid,
                        ),
                    )
                    conn.commit()
                except Exception as e:
                    raise AceException(
                        f"Error while updating exception status: {str(e)}"
                    )
