from concurrent.futures import ThreadPoolExecutor
from itertools import combinations, zip_longest
import json
from multiprocessing import Manager
from datetime import datetime
import traceback
import os
from typing import Tuple, Any
from dataclasses import dataclass

from mpire import WorkerPool
from mpire.utils import make_single_arguments
from psycopg import sql
from psycopg import IsolationLevel
from psycopg.types.composite import register_composite, CompositeInfo
from tqdm import tqdm

import ace_html_reporter
import util
import ace
import ace_core
import ace_config as config
from ace_data_models import MerkleTreeTask
from ace_exceptions import AceException
from ace_sql import (
    CREATE_BULK_TRIGGER_FUNCTION,
    CREATE_METADATA_TABLE,
    CREATE_XOR_FUNCTION,
    DROP_BULK_TRIGGER_FUNCTION,
    DROP_METADATA_TABLE,
    DROP_XOR_FUNCTION,
    DROP_MTREE_TABLE,
    DROP_MTREE_TRIGGERS,
    ENABLE_ALWAYS,
    ESTIMATE_ROW_COUNT,
    GET_BLOCK_COUNT_COMPOSITE,
    GET_BLOCK_COUNT_SIMPLE,
    GET_BLOCK_SIZE_FROM_METADATA,
    GET_COUNT_COMPOSITE,
    GET_COUNT_SIMPLE,
    GET_MAX_VAL_SIMPLE,
    GET_PKEY_TYPE,
    GET_ROW_COUNT_ESTIMATE,
    GET_MAX_VAL_COMPOSITE,
    GET_SPLIT_POINT_COMPOSITE,
    GET_SPLIT_POINT_SIMPLE,
    UPDATE_LEAF_HASHES,
    UPDATE_MAX_VAL,
    UPDATE_METADATA,
    COMPUTE_LEAF_HASHES,
    BUILD_PARENT_NODES,
    INSERT_BLOCK_RANGES,
    GET_DIRTY_AND_NEW_BLOCKS,
    CLEAR_DIRTY_FLAGS,
    GET_NODE_CHILDREN,
    GET_ROOT_NODE,
    GET_LEAF_RANGES,
    CREATE_GENERIC_TRIGGER,
    INSERT_COMPOSITE_BLOCK_RANGES,
    CREATE_SIMPLE_MTREE_TABLE,
    CREATE_COMPOSITE_MTREE_TABLE,
    DELETE_PARENT_NODES,
    GET_MAX_NODE_POSITION,
    UPDATE_BLOCK_RANGE_END,
    DELETE_BLOCK,
    UPDATE_NODE_POSITIONS_SEQUENTIAL,
    FIND_BLOCKS_TO_SPLIT,
    FIND_BLOCKS_TO_MERGE_COMPOSITE,
    FIND_BLOCKS_TO_MERGE_SIMPLE,
    GET_MAX_NODE_LEVEL,
    COMPARE_BLOCKS_SQL,
    UPDATE_NODE_POSITIONS_TEMP,
)

BERNOULLI_THRESHOLD = 10_000_000


@dataclass
class BlockBoundary:
    """Represents a block boundary for parallel processing"""

    block_id: int
    block_start: Tuple[Any, ...]
    block_end: Tuple[Any, ...]


def safe_min(a, b):
    if a is None and b is None:
        return None
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


def safe_max(a, b):
    if a is None and b is None:
        return None
    if a is None:
        return b
    if b is None:
        return a
    return max(a, b)


def init_hash_conn_pool(worker_id, shared_objects, worker_state):
    """
    Initialise connection pool for hash computation workers

    Args:
        shared_objects: The shared objects from the mpire worker pool manager.
        contains the node and task objects, but might optimise this later.

        worker_state: The empty worker state dictionary for initialisation.
        This function is called once per worker, and populates the worker state
        with the connection and cursor for the worker.
    """
    node = shared_objects["node"]
    task = shared_objects["task"]

    try:
        _, conn = task.connection_pool.connect(node)
        task.connection_pool.drop_privileges(
            conn,
            client_role=(
                task.client_role
                if config.USE_CERT_AUTH or task.invoke_method == "api"
                else None
            ),
        )
        worker_state["conn"] = conn
        worker_state["cur"] = conn.cursor()

    except Exception as e:
        if "conn" in worker_state:
            try:
                worker_state["conn"].close()
            except Exception:
                pass
        raise AceException(f"Error initializing worker connection: {str(e)}")


def close_hash_conn_pool(worker_id, shared_objects, worker_state):
    """
    Close connection pool for hash computation workers

    Args:
        shared_objects: The shared objects from the mpire worker pool manager.
        Not needed here, but retained because mpire requires it.

        worker_state: The worker state after the worker initialisation. Contains
        the connection and cursor for the worker.
    """
    try:
        worker_state["conn"].commit()
        worker_state["cur"].close()
        worker_state["conn"].close()
    except Exception as e:
        raise AceException(f"Error closing worker connection: {str(e)}")


def compute_block_hashes(worker_id, shared_objects, worker_state, args):
    """
    Worker function that computes hashes for a block

    Args:
        shared_objects: The shared objects from the mpire worker pool manager.
        contains the node and task objects.

        worker_state: The worker state after the worker initialisation. Contains
        the connection and cursor for the worker.

        args: The arguments for the worker function. Contains the block boundary
        and the SQL query to compute the hashes.
    """
    block = args
    task = shared_objects["task"]

    try:
        conn = worker_state.get("conn")
        cur = conn.cursor()

        key_columns = task.fields.key.split(",")
        is_composite = len(key_columns) > 1

        if is_composite:
            where_conditions = []

            pkey_cols = sql.SQL(", ").join(sql.Identifier(col) for col in key_columns)
            where_conditions.append(
                sql.SQL("({pkey_cols}) >= ({pkey_values})").format(
                    pkey_cols=pkey_cols,
                    pkey_values=sql.SQL(", ").join(
                        sql.Literal(val) for val in block.block_start
                    ),
                )
            )
            where_conditions.append(
                sql.SQL("({pkey_cols}) <= ({pkey_values})").format(
                    pkey_cols=pkey_cols,
                    pkey_values=sql.SQL(", ").join(
                        sql.Literal(val) for val in block.block_end
                    ),
                )
            )

            # TODO: Double check this
            if not where_conditions:
                where_clause = sql.SQL("TRUE")
            else:
                where_clause = sql.SQL(" AND ").join(where_conditions)

        else:
            where_conditions = []

            where_conditions.append(
                sql.SQL("{pkey_col} >= {pkey_value}").format(
                    pkey_col=sql.Identifier(task.fields.key),
                    pkey_value=sql.Literal(*block.block_start),
                )
            )

            where_conditions.append(
                sql.SQL("{pkey_col} <= {pkey_value}").format(
                    pkey_col=sql.Identifier(task.fields.key),
                    pkey_value=sql.Literal(*block.block_end),
                )
            )

            if not where_conditions:
                where_clause = sql.SQL("TRUE")
            else:
                where_clause = sql.SQL(" AND ").join(where_conditions)

        cur.execute(
            sql.SQL(COMPUTE_LEAF_HASHES).format(
                schema=sql.Identifier(task.fields.l_schema),
                table=sql.Identifier(task.fields.l_table),
                key=sql.SQL(", ").join(sql.Identifier(col) for col in key_columns),
                columns=sql.SQL(", ").join(
                    sql.Identifier(col) for col in task.fields.cols.split(",")
                ),
                where_clause=where_clause,
            )
        )

        leaf_hash = cur.fetchone()[0]

        return {"node_position": block.block_id, "leaf_hash": leaf_hash}

    except Exception as e:
        print(f"Error computing hash for block {block.block_id}: {str(e)}")
        traceback.print_exc()
        return None


def create_mtree_objects(
    conn, schema, table, key, total_rows, block_size, num_blocks, recreate_objects=False
):
    """
    Creates the necessary database objects for Merkle tree implementation

    Args:
        conn: Database connection
        schema: Schema name
        table: Table name
        key: Primary key column(s)
        total_rows: Estimated total number of rows
        num_blocks: Number of blocks to split the table into
        recreate_objects: Whether to drop and recreate all objects
    """
    key_columns = key.split(",")
    is_composite = len(key_columns) > 1

    with conn.cursor() as cur:
        if recreate_objects:
            _mtree_init(conn)

        cur.execute(
            sql.SQL("DROP TABLE IF EXISTS {mtree_table}").format(
                mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
            )
        )

        if is_composite:
            key_type_columns = []
            for col in key_columns:
                cur.execute(
                    sql.SQL(GET_PKEY_TYPE).format(
                        schema=sql.Literal(schema),
                        table=sql.Literal(table),
                        key=sql.Literal(col),
                    )
                )
                col_type = cur.fetchone()[0]
                key_type_columns.append(f"{col} {col_type}")

            cur.execute(
                sql.SQL(CREATE_COMPOSITE_MTREE_TABLE).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                    range_idx=sql.SQL(f"idx_range_{schema}_{table}"),
                    schema=sql.SQL(schema),
                    table=sql.SQL(table),
                    key_type_columns=sql.SQL(", ").join(
                        sql.SQL(col) for col in key_type_columns
                    ),
                )
            )
        else:
            cur.execute(
                sql.SQL(GET_PKEY_TYPE).format(
                    schema=sql.Literal(schema),
                    table=sql.Literal(table),
                    key=sql.Literal(key),
                )
            )
            pkey_type = cur.fetchone()[0]

            cur.execute(
                sql.SQL(CREATE_SIMPLE_MTREE_TABLE).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                    pkey_type=sql.SQL(pkey_type),
                    range_idx=sql.Identifier(f"idx_range_{schema}_{table}"),
                )
            )

        cur.execute(
            sql.SQL(CREATE_GENERIC_TRIGGER).format(
                trigger=sql.SQL(f"trg_mtree_{schema}_{table}"),
                schema=sql.Identifier(schema),
                table=sql.Identifier(table),
                key=sql.Literal(key),
            )
        )

        cur.execute(
            sql.SQL(ENABLE_ALWAYS).format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(table),
                insert_trigger=sql.SQL(f"trg_mtree_{schema}_{table}_insert_stmt"),
                update_trigger=sql.SQL(f"trg_mtree_{schema}_{table}_update_stmt"),
                delete_trigger=sql.SQL(f"trg_mtree_{schema}_{table}_delete_stmt"),
            )
        )

        cur.execute(
            UPDATE_METADATA,
            (schema, table, total_rows, block_size, num_blocks, is_composite),
        )

        conn.commit()


def get_row_estimate(conn, schema, table, block_size, analyse=False):
    """
    We cannot use a naïve count(*) for merkle tree candidates because the
    table is too large. Instead, we use a multi-step process to get an estimate:

    1. We first check the live_tuples in pg_stat_user_tables.
    2. If 1 is not available, we use the reltuples in pg_class.
    3. If neither is available, we use the pg_relation_size / 8192 * 0.7.
        8192 is the page size used by PostgreSQL in bytes, and 0.7 is the
        approximate fill factor of the page.

    Args:
        conn: The database connection
        schema: The schema of the target table
        table: The target table
        analyse: Whether to analyse the table
    """

    cur = conn.cursor()

    if analyse:
        cur.execute("BEGIN")
        cur.execute("SET parallel_tuple_cost = 0")
        cur.execute("SET parallel_setup_cost = 0")

        print(f"Analysing {schema}.{table} on node {conn.info.host}")
        print("This might take a while...")

        # TODO: This might take a while so need a different strategy here
        cur.execute(
            sql.SQL("ANALYZE {schema}.{table}").format(
                schema=sql.Identifier(schema), table=sql.Identifier(table)
            )
        )

    cur.execute(
        sql.SQL(ESTIMATE_ROW_COUNT).format(
            schema=sql.Literal(schema),
            table=sql.Literal(table),
        ),
    )
    total_rows = cur.fetchone()[0]
    num_blocks = (total_rows - 1) // block_size + 1

    conn.commit()
    return total_rows, num_blocks


def process_block_ranges(offsets: list):

    block_ranges = []

    del offsets[-1]

    if len(offsets) == 2:
        for i, offset in enumerate(offsets):
            # Yes, this needs to be a tuple to maintain consistency
            block_ranges.append((i, (offset[0],), (offset[1],)))
    else:
        for i, offset in enumerate(offsets):
            rng = (
                i,
                tuple([offset[k] for k in range(len(offset)) if k % 2 == 0]),
                tuple([offset[k] for k in range(len(offset)) if k % 2 == 1]),
            )

            block_ranges.append(rng)

    return block_ranges


def build_mtree(mtree_task: MerkleTreeTask) -> None:
    """
    Build a Merkle tree for a table using parallel processing.
    The tree is stored in a separate table for each source table.
    Parent nodes are computed using XOR of child hashes.

    Args:
        cluster_name (str): Name of the cluster
        table_name (str): Name of the table to build tree for
        dbname (str, optional): Database name. Defaults to the first entry
        in the databases array of the cluster json file.
    """

    ace.merkle_tree_checks(mtree_task, skip_validation=True)

    # First we need to get the row estimates and blocks from all nodes
    # before we can compute the block ranges.
    # The block range computation will happen on just one node, and the same
    # ranges will be used for all nodes.
    # This is crucial because otherwise, the leaf node hashes are meaningless
    # if they correspond to different block ranges.

    max_blocks = 0
    ref_node = None
    schema = mtree_task.fields.l_schema
    table = mtree_task.fields.l_table
    key = mtree_task.fields.key
    total_rows = 0
    num_blocks = 0
    block_ranges = mtree_task.ranges

    if not block_ranges:
        for node in mtree_task.fields.cluster_nodes:
            _, conn = mtree_task.connection_pool.get_cluster_node_connection(node)
            try:
                total_rows, num_blocks = get_row_estimate(
                    conn,
                    schema,
                    table,
                    mtree_task.block_size,
                    analyse=mtree_task.analyse,
                )

                if num_blocks > max_blocks:
                    max_blocks = num_blocks
                    ref_node = node
            except Exception as e:
                conn.rollback()
                traceback.print_exc()
                raise AceException(
                    f"Error creating mtree objects on {node['name']}: {str(e)}"
                )

        print(f"Using node {ref_node['name']} as the reference node")

        block_ranges = []

        # Now let's compute the block ranges on the reference node
        msg = (
            f"Calculating block ranges for {max_blocks:,} blocks "
            f"(~{total_rows:,} rows)"
        )
        print(msg)

        # Calculate sample size based on total rows
        # Tablesample may be an efficient workaround for getting the block ranges,
        # but it is still very expensive for large tables.
        # So, here's what we'll do:
        # If total rows > 1B, we'll sample 0.01% of the rows
        # If total rows > 100M, we'll sample 0.1% of the rows
        # Otherwise, we'll sample 1% of the rows
        sample_percent = (
            0.01
            if total_rows > 500_000_000
            else 0.1 if total_rows > 50_000_000 else 1.0
        )

        table_sample_method = (
            "BERNOULLI" if total_rows < BERNOULLI_THRESHOLD else "SYSTEM"
        )

        print(f"Using {table_sample_method} with sample percent {sample_percent}")

        _, conn = mtree_task.connection_pool.get_cluster_node_connection(ref_node)

        offsets_query = ace.generate_pkey_offsets_query(
            schema=schema,
            table=table,
            key_columns=key.split(","),
            table_sample_method=table_sample_method,
            sample_percent=sample_percent,
            ntile_count=max_blocks,
        )

        with conn.cursor() as cur:
            cur.execute(offsets_query)
            offsets = cur.fetchall()
            block_ranges = process_block_ranges(offsets)

    if mtree_task.write_ranges:
        filename = (
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{schema}_{table}_ranges.json"
        )
        with open(filename, "w") as f:
            json.dump(block_ranges, f)

        print(f"\nBlock ranges written to {util.set_colour(filename, 'blue')}")

    # We're ready to build the merkle tree
    schema_table = f"{schema}.{table}"
    print(f"\nBuilding merkle tree for {schema_table}")

    for node in mtree_task.fields.cluster_nodes:
        print(f"\nProcessing node: {node['name']}")
        _, conn = mtree_task.connection_pool.get_cluster_node_connection(node)

        create_mtree_objects(
            conn,
            schema,
            table,
            key,
            total_rows,
            mtree_task.block_size,
            num_blocks,
            recreate_objects=mtree_task.recreate_objects,
        )

        try:
            cur = conn.cursor()

            key_columns = key.split(",")
            is_composite = len(key_columns) > 1

            if is_composite:
                insert_sql = sql.SQL(INSERT_COMPOSITE_BLOCK_RANGES).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                    start_tuple_values=sql.SQL(", ").join(
                        [sql.Placeholder()] * len(key_columns)
                    ),
                    end_tuple_values=sql.SQL(", ").join(
                        [sql.Placeholder()] * len(key_columns)
                    ),
                )

                cur.executemany(
                    insert_sql,
                    [
                        (id, *start_tuple, *end_tuple)
                        for id, start_tuple, end_tuple in block_ranges
                    ],
                )
            else:
                insert_sql = sql.SQL(INSERT_BLOCK_RANGES).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
                )
                cur.executemany(
                    insert_sql, [(id, *start, *end) for id, start, end in block_ranges]
                )

            conn.commit()

            work_items = []
            for block in block_ranges:
                work_items.append(
                    (
                        BlockBoundary(
                            block_id=block[0],
                            block_start=block[1],
                            block_end=block[2],
                        )
                    )
                )

            max_workers = int(os.cpu_count() * mtree_task.max_cpu_ratio * 2)
            n_jobs = min(len(work_items), max_workers)

            shared_objects = {
                "task": mtree_task,
                "node": node,
            }

            results = []

            cur.close()
            conn.close()
            mtree_task.connection_pool.close_all()

            with WorkerPool(
                n_jobs=n_jobs,
                shared_objects=shared_objects,
                use_worker_state=True,
                pass_worker_id=True,
            ) as pool:
                results = list(
                    pool.imap_unordered(
                        compute_block_hashes,
                        make_single_arguments(work_items),
                        iterable_len=len(work_items),
                        worker_init=init_hash_conn_pool,
                        worker_exit=close_hash_conn_pool,
                        progress_bar=True,
                        progress_bar_options={"desc": "Computing hashes"},
                    )
                )

                failed = [r for r in results if not r]
                if failed:
                    raise AceException(
                        f"Failed to compute hashes for {len(failed)} blocks"
                    )

            _, new_conn = mtree_task.connection_pool.get_cluster_node_connection(node)
            parent_cur = new_conn.cursor()

            print("\nUpdating leaf nodes with computed hashes...")

            parent_cur.executemany(
                sql.SQL(UPDATE_LEAF_HASHES).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                ),
                results,
            )

            print("\nBuilding parent nodes...")

            parent_cur.execute(
                sql.SQL(DELETE_PARENT_NODES).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
                )
            )

            level = 0
            while True:
                parent_cur.execute(
                    sql.SQL(BUILD_PARENT_NODES).format(
                        mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                    ),
                    {"node_level": level},
                )

                count = parent_cur.fetchone()[0]
                if count <= 1:
                    break
                level += 1

            new_conn.commit()
            print(
                f"Merkle tree built successfully on {node['name']}"
                f" with {level + 1} levels"
            )

            conn.close()

        except Exception as e:
            conn.rollback()
            traceback.print_exc()
            raise AceException(
                f"Error building Merkle tree on {node['name']}: {str(e)}"
            )

    mtree_task.connection_pool.close_all()


def split_blocks(conn, schema, table, key, blocks, block_size):
    """
    Split blocks if they are too large.
    Returns a list of block positions that were modified.
    """
    try:
        cur = conn.cursor()
        modified_positions = set()
        target_size = block_size

        # First delete all parent nodes since we'll be modifying the tree structure
        # This is not expensive at all since computing parent hashes is significantly
        # cheaper than computing leaf hashes.
        cur.execute(
            sql.SQL(
                """
                DELETE FROM {mtree_table}
                WHERE node_level > 0
                """
            ).format(mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"))
        )

        key_columns = key.split(",")
        is_composite = len(key_columns) > 1

        if is_composite:
            key_types = []
            for col in key_columns:
                cur.execute(
                    sql.SQL(GET_PKEY_TYPE).format(
                        schema=sql.Literal(schema),
                        table=sql.Literal(table),
                        key=sql.Literal(col),
                    ),
                )
                key_types.append(cur.fetchone()[0])
        else:
            cur.execute(
                sql.SQL(GET_PKEY_TYPE).format(
                    schema=sql.Literal(schema),
                    table=sql.Literal(table),
                    key=sql.Literal(key),
                )
            )
            pkey_type = cur.fetchone()[0]

        blocks = sorted(blocks, key=lambda x: x[0])
        i = 0
    except Exception as e:
        conn.rollback()
        raise AceException(f"Error splitting blocks on {schema}.{table}: {str(e)}")

    pbar = tqdm(total=len(blocks), desc="Processing blocks", leave=False)

    while i < len(blocks):
        pos, start, end = blocks[i]
        pbar.update(1)

        # When inserts happen after the range_end of the last block, we mark that
        # block as dirty and set the range_end to null. So, if we're attempting
        # to add new blocks at the end, we need to find the actual max value.
        if i == len(blocks) - 1 and end is None:
            if is_composite:
                pkey_cols = sql.SQL(", ").join(
                    sql.Identifier(col) for col in key_columns
                )
                pkey_values = sql.SQL(", ").join(sql.Literal(val) for val in start)

                cur.execute(
                    sql.SQL(GET_MAX_VAL_COMPOSITE).format(
                        schema=sql.Identifier(schema),
                        table=sql.Identifier(table),
                        pkey_cols=pkey_cols,
                        pkey_values=pkey_values,
                    )
                )
                max_vals = cur.fetchone()
                if max_vals is not None:
                    end = max_vals
                    cur.execute(
                        sql.SQL(UPDATE_MAX_VAL).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                        ),
                        (end, pos),
                    )
            else:
                cur.execute(
                    sql.SQL(GET_MAX_VAL_SIMPLE).format(
                        schema=sql.Identifier(schema),
                        table=sql.Identifier(table),
                        key=sql.Identifier(key),
                    ),
                    (start,),
                )
                max_val = cur.fetchone()[0]
                if max_val is not None:
                    end = max_val
                    cur.execute(
                        sql.SQL(UPDATE_MAX_VAL).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                        ),
                        (end, pos),
                    )

        # Get actual row count for this block
        if is_composite:
            where_conditions = []
            pkey_cols = sql.SQL(", ").join(sql.Identifier(col) for col in key_columns)

            where_conditions.append(
                sql.SQL("({pkey_cols}) >= ({pkey_values})").format(
                    pkey_cols=pkey_cols,
                    pkey_values=sql.SQL(", ").join(sql.Literal(val) for val in start),
                )
            )

            if end is not None:
                where_conditions.append(
                    sql.SQL("({pkey_cols}) <= ({pkey_values})").format(
                        pkey_cols=pkey_cols,
                        pkey_values=sql.SQL(", ").join(sql.Literal(val) for val in end),
                    )
                )

            where_clause = sql.SQL(" AND ").join(where_conditions)

            cur.execute(
                sql.SQL(GET_COUNT_COMPOSITE).format(
                    schema=sql.Identifier(schema),
                    table=sql.Identifier(table),
                    where_clause=where_clause,
                )
            )
        else:
            cur.execute(
                sql.SQL(GET_COUNT_SIMPLE).format(
                    schema=sql.Identifier(schema),
                    table=sql.Identifier(table),
                    key=sql.Identifier(key),
                    pkey_type=sql.SQL(pkey_type),
                ),
                (start, end, end),
            )

        count = cur.fetchone()[0]

        if count > target_size * 2:
            # Find the split point at the midpoint of the block
            if is_composite:
                pkey_cols = sql.SQL(", ").join(
                    sql.Identifier(col) for col in key_columns
                )
                order_cols = sql.SQL("({pkey_cols})").format(pkey_cols=pkey_cols)
                where_conditions = []

                where_conditions.append(
                    sql.SQL("({pkey_cols}) >= ({pkey_values})").format(
                        pkey_cols=pkey_cols,
                        pkey_values=sql.SQL(", ").join(
                            sql.Literal(val) for val in start
                        ),
                    )
                )

                if end is not None:
                    where_conditions.append(
                        sql.SQL("({pkey_cols}) <= ({pkey_values})").format(
                            pkey_cols=pkey_cols,
                            pkey_values=sql.SQL(", ").join(
                                sql.Literal(val) for val in end
                            ),
                        )
                    )

                where_clause = sql.SQL(" AND ").join(where_conditions)

                cur.execute(
                    sql.SQL(GET_SPLIT_POINT_COMPOSITE).format(
                        schema=sql.Identifier(schema),
                        table=sql.Identifier(table),
                        pkey_cols=pkey_cols,
                        where_clause=where_clause,
                        order_cols=order_cols,
                    ),
                    (count // 2,),  # Split at midpoint
                )
            else:
                cur.execute(
                    sql.SQL(GET_SPLIT_POINT_SIMPLE).format(
                        schema=sql.Identifier(schema),
                        table=sql.Identifier(table),
                        key=sql.Identifier(key),
                        pkey_type=sql.SQL(pkey_type),
                    ),
                    (start, end, end, count // 2),  # Split at midpoint
                )

            split_point = cur.fetchone()[0]

            """
            We're going to be inserting the new block at the end to avoid disrupting
            the existing parent hashes. Why? Consider this example:

            0: 1-100: x1
            1: 101-500: x2
            2: 501-600: x3
            3: 601-700: x4
            4: 701-1000: x5

            It's ascii tree would look like this:

                       p6
                      / \
                     /   \
                    /     \
                   p4     p5
                  /  \      \
                 /    \      \
                /      \      \
               p1      p2     p3
              /  \    /  \      \
             x1   x2 x3   x4    x5


            Let's assume our initial blocks are all ~100 rows in size.
            Now, say many inserts happen in block 101-500, and we need to split it.
            If we split block 1, and insert the new block right after it, we get:

            0: 1-100: x1
            1: 101-300: m
            2: 301-500: n
            3: 501-600: x3
            4: 601-700: x4
            5: 701-1000: x5

            The new tree would look like this:
            m & n indicate new hashes, and primes (') indicate changed hashes

                        p6'
                       /  \
                      /    \
                     /      \
                    /        \
                   p4'       p5'
                  /  \         \
                 /    \         \
                /      \         \
               p1'     p2'       p3'
              /  \    /  \      /  \
             x1   m  n   x3   x4    x5

            While doing a table-diff, we'd have to go all the way down to the leaf
            nodes to detect which blocks don't match anymore. In other words,
            even though just 2 leaf blocks' hashes changed, all their parent hashes
            changed unnecessarily. This is would defeat the purpose of having
            merkle trees in the first place.

            Instead, if we insert the new block at the end, we retain the
            parent-child relationships of existing leaf nodes, and only modify them
            where the split happened.

            With this logic, our new tree would look like this:

            0: 1-100: x1
            1: 101-300: m
            2: 501-600: x3
            3: 601-700: x4
            4: 701-1000: x5
            5: 301-500: n

                        p6'
                       / \
                      /   \
                     /     \
                    /       \
                   p4'      p5'
                  /  \        \
                 /    \        \
                /      \        \
               p1'     p2       p3'
              /  \    /  \     /  \
             x1   m  x3  x4   x5   n

             In our example, p2 remained unchanged, but in a larger tree, several
             parent nodes could potentially remain unchanged, thereby speeding-up
             our diff logic.
            """

            # Get the next available position at the end
            cur.execute(
                sql.SQL(GET_MAX_NODE_POSITION).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
                )
            )
            new_pos = cur.fetchone()[0]

            # Create new block at the end
            if is_composite:
                insert_sql = sql.SQL(INSERT_COMPOSITE_BLOCK_RANGES).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                    start_tuple_values=sql.SQL(", ").join(
                        [sql.Placeholder()] * len(key_columns)
                    ),
                    end_tuple_values=sql.SQL(", ").join(
                        [sql.Placeholder()] * len(key_columns)
                    ),
                )
                cur.execute(
                    insert_sql,
                    (new_pos, *split_point, *end),
                )
            else:
                cur.execute(
                    sql.SQL(INSERT_BLOCK_RANGES).format(
                        mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                    ),
                    (new_pos, split_point, end),
                )

            cur.execute(
                sql.SQL(UPDATE_BLOCK_RANGE_END).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
                ),
                (split_point, pos),
            )

            modified_positions.add(pos)
            modified_positions.add(new_pos)

            blocks[i] = (pos, start, split_point)
            blocks.insert(i + 1, (new_pos, split_point, end))
            i += 1
            continue

        i += 1

    conn.commit()
    pbar.close()
    return list(modified_positions)


def merge_blocks(conn, schema, table, key, blocks, block_size):
    """
    Merge blocks if they are too small.
    Returns a list of block positions that were modified.
    """
    cur = conn.cursor()
    modified_positions = set()
    target_size = block_size

    # We will trigger a merge if the actual block size is less than 25% of the
    # target size
    MERGE_THRESHOLD = 0.25

    # Whenever there is a merge, the node_positions of leaf nodes
    # become invalid. Now, we cannot simply do a node_position = node_position - 1
    # since there might be other leaf nodes at that location.
    # So we move all leaf nodes to a temporary position and then update the
    # node_positions of the leaf nodes after the rebalancing is done
    # This temp offset is large enough for the foreseeable future.
    #
    # Napkin math: For a conflict to happen with a 10^6 temp offset, and a
    # block size of say 10^5, we would need 10^11 rows or 100 billion rows in the
    # table, which is a lot.
    #
    # NOTE: This operation is disruptive. It *will* change parent-child relationships,
    # thereby potentially slowing down table-diff. Use --rebalance=true infrequently,
    # or during maintenance windows.
    TEMP_OFFSET = 1_000_000

    # First delete all parent nodes since we'll be modifying the tree structure
    # This is not expensive at all since computing parent hashes is significantly
    # cheaper than computing leaf hashes.
    cur.execute(
        sql.SQL(DELETE_PARENT_NODES).format(
            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
        )
    )

    key_columns = key.split(",")
    is_composite = len(key_columns) > 1

    if is_composite:
        key_types = []
        for col in key_columns:
            cur.execute(
                sql.SQL(GET_PKEY_TYPE).format(
                    schema=sql.Literal(schema),
                    table=sql.Literal(table),
                    key=sql.Literal(col),
                ),
            )
            key_types.append(cur.fetchone()[0])
    else:
        cur.execute(
            sql.SQL(GET_PKEY_TYPE).format(
                schema=sql.Literal(schema),
                table=sql.Literal(table),
                key=sql.Literal(key),
            ),
        )
        pkey_type = cur.fetchone()[0]

    blocks = sorted(blocks, key=lambda x: x[0])
    i = 0

    pbar = tqdm(total=len(blocks), desc="Processing blocks")

    while i < len(blocks):
        pos, start, end = blocks[i]
        pbar.update(1)

        # When inserts happen after the range_end of the last block, we mark that
        # block as dirty and set the range_end to null. So, if we're attempting
        # to add new blocks at the end, we need to find the actual max value.
        if i == len(blocks) - 1 and end is None:
            if is_composite:
                pkey_cols = sql.SQL(", ").join(
                    sql.Identifier(col) for col in key_columns
                )
                pkey_values = sql.SQL(", ").join(sql.Literal(val) for val in start)

                cur.execute(
                    sql.SQL(GET_MAX_VAL_COMPOSITE).format(
                        schema=sql.Identifier(schema),
                        table=sql.Identifier(table),
                        pkey_cols=pkey_cols,
                        pkey_values=pkey_values,
                    )
                )
                max_vals = cur.fetchone()
                if max_vals is not None:
                    end = max_vals
                    cur.execute(
                        sql.SQL(UPDATE_MAX_VAL).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                        ),
                        (end, pos),
                    )
            else:
                cur.execute(
                    sql.SQL(GET_MAX_VAL_SIMPLE).format(
                        schema=sql.Identifier(schema),
                        table=sql.Identifier(table),
                        key=sql.Identifier(key),
                    ),
                    (start,),
                )
                max_val = cur.fetchone()[0]
                if max_val is not None:
                    end = max_val
                    cur.execute(
                        sql.SQL(UPDATE_MAX_VAL).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                        ),
                        (end, pos),
                    )

        # Get actual row count for this block
        if is_composite:
            where_conditions = []
            pkey_cols = sql.SQL(", ").join(sql.Identifier(col) for col in key_columns)

            where_conditions.append(
                sql.SQL("({pkey_cols}) >= ({pkey_values})").format(
                    pkey_cols=pkey_cols,
                    pkey_values=sql.SQL(", ").join(sql.Literal(val) for val in start),
                )
            )

            if end is not None:
                where_conditions.append(
                    sql.SQL("({pkey_cols}) <= ({pkey_values})").format(
                        pkey_cols=pkey_cols,
                        pkey_values=sql.SQL(", ").join(sql.Literal(val) for val in end),
                    )
                )

            where_clause = sql.SQL(" AND ").join(where_conditions)

            cur.execute(
                sql.SQL(GET_COUNT_COMPOSITE).format(
                    schema=sql.Identifier(schema),
                    table=sql.Identifier(table),
                    where_clause=where_clause,
                )
            )
        else:
            cur.execute(
                sql.SQL(GET_COUNT_SIMPLE).format(
                    schema=sql.Identifier(schema),
                    table=sql.Identifier(table),
                    key=sql.Identifier(key),
                    pkey_type=sql.SQL(pkey_type),
                ),
                (start, end, end),
            )

        count = cur.fetchone()[0]

        # If block is nearly empty, try to merge with either neighbour
        if count < target_size * MERGE_THRESHOLD:
            # First check if we can merge with previous block
            if pos > 0:
                if is_composite:
                    cur.execute(
                        sql.SQL(GET_BLOCK_COUNT_COMPOSITE).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                            schema=sql.Identifier(schema),
                            table=sql.Identifier(table),
                            pkey_cols=sql.SQL(", ").join(
                                sql.Identifier(col) for col in key_columns
                            ),
                        ),
                        (pos - 1,),
                    )
                else:
                    cur.execute(
                        sql.SQL(GET_BLOCK_COUNT_SIMPLE).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                            schema=sql.Identifier(schema),
                            table=sql.Identifier(table),
                            key=sql.Identifier(key),
                        ),
                        (pos - 1,),
                    )

                prev_block = cur.fetchone()
                if prev_block:
                    prev_pos, prev_start, prev_end, prev_count = prev_block
                    if (count + prev_count) <= target_size * 2:
                        # Move blocks to temp positions
                        cur.execute(
                            sql.SQL(UPDATE_NODE_POSITIONS_TEMP).format(
                                mtree_table=sql.Identifier(
                                    f"ace_mtree_{schema}_{table}"
                                ),
                            ),
                            (TEMP_OFFSET, prev_pos),
                        )

                        # Merge with previous block - keep full range
                        cur.execute(
                            sql.SQL(UPDATE_BLOCK_RANGE_END).format(
                                mtree_table=sql.Identifier(
                                    f"ace_mtree_{schema}_{table}"
                                ),
                            ),
                            (end, prev_pos),
                        )

                        # Delete current block at its temporary position
                        cur.execute(
                            sql.SQL(DELETE_BLOCK).format(
                                mtree_table=sql.Identifier(
                                    f"ace_mtree_{schema}_{table}"
                                ),
                            ),
                            (pos + TEMP_OFFSET,),
                        )

                        # Move remaining blocks back in sequential order
                        cur.execute(
                            sql.SQL(UPDATE_NODE_POSITIONS_SEQUENTIAL).format(
                                mtree_table=sql.Identifier(
                                    f"ace_mtree_{schema}_{table}"
                                ),
                            ),
                            (prev_pos, prev_pos + TEMP_OFFSET),
                        )

                        modified_positions.add(prev_pos)

                        blocks = [
                            (p - 1 if p > pos else p, s, e)
                            for p, s, e in blocks
                            if p != pos
                        ]
                        if not blocks:
                            break

                        if i > 0:
                            i -= 1

                        continue

            # If we couldn't merge with the previous block, try the next block
            if is_composite:
                cur.execute(
                    sql.SQL(GET_BLOCK_COUNT_COMPOSITE).format(
                        mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                        schema=sql.Identifier(schema),
                        table=sql.Identifier(table),
                        pkey_cols=sql.SQL(", ").join(
                            sql.Identifier(col) for col in key_columns
                        ),
                    ),
                    (pos + 1,),
                )
            else:
                cur.execute(
                    sql.SQL(GET_BLOCK_COUNT_SIMPLE).format(
                        mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                        schema=sql.Identifier(schema),
                        table=sql.Identifier(table),
                        key=sql.Identifier(key),
                    ),
                    (pos + 1,),
                )

            next_block = cur.fetchone()
            if next_block:
                next_pos, next_start, next_end, next_count = next_block
                if (count + next_count) <= target_size * 2:
                    # Move blocks to temp positions
                    cur.execute(
                        sql.SQL(UPDATE_NODE_POSITIONS_TEMP).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                        ),
                        (TEMP_OFFSET, pos),
                    )

                    # Merge with next block - keep full range
                    cur.execute(
                        sql.SQL(UPDATE_BLOCK_RANGE_END).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
                        ),
                        (next_end, pos),
                    )

                    # Delete next block at its temporary position
                    cur.execute(
                        sql.SQL(DELETE_BLOCK).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
                        ),
                        (next_pos + TEMP_OFFSET,),
                    )

                    # Move remaining blocks back in sequential order
                    cur.execute(
                        sql.SQL(UPDATE_NODE_POSITIONS_SEQUENTIAL).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
                        ),
                        (pos, pos + TEMP_OFFSET),
                    )

                    modified_positions.add(pos)
                    blocks = [
                        (p - 1 if p > next_pos else p, s, e)
                        for p, s, e in blocks
                        if p != next_pos
                    ]

                    if not blocks:
                        break

                    if i < len(blocks):
                        i += 1
                    continue

        i += 1
        if i >= len(blocks):
            break

    conn.commit()
    pbar.close()
    return list(modified_positions)


def update_mtree(mtree_task: MerkleTreeTask, skip_all_checks=False) -> None:
    """
    Update a Merkle tree by recomputing hashes for dirty leaf nodes and new blocks.
    Also processes any pending block rebalancing operations.
    Uses repeatable read isolation to ensure consistency during the update.

    Args:
        cluster_name (str): Name of the cluster
        table_name (str): Name of the table to update tree for
        dbname (str, optional): Database name. Defaults to None.
    """

    if not skip_all_checks:
        ace.merkle_tree_checks(mtree_task, skip_validation=True)

    schema = mtree_task.fields.l_schema
    table = mtree_task.fields.l_table
    key = mtree_task.fields.key
    key_columns = key.split(",")
    is_composite = len(key_columns) > 1

    # we need to first read the metadata to figure out what the
    # block size the tree was built with
    try:
        _, conn = mtree_task.connection_pool.get_connection(
            mtree_task.fields.cluster_nodes[0]
        )
        cur = conn.cursor()
        cur.execute(
            sql.SQL(GET_BLOCK_SIZE_FROM_METADATA).format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(table),
            )
        )
        block_size = cur.fetchone()[0]
    except Exception as e:
        raise AceException(f"Error getting block size from metadata: {str(e)}")

    if not block_size:
        raise AceException(f"Block size not found for {schema}.{table}")

    mtree_task.block_size = block_size

    SPLIT_THRESHOLD = block_size // 2
    # If the number of deletes in a block exceeds 75% of the block size, then we
    # merge it
    MERGE_THRESHOLD = 0.75

    for node in mtree_task.fields.cluster_nodes:

        _, conn = mtree_task.connection_pool.connect(node)
        conn.set_isolation_level(IsolationLevel.REPEATABLE_READ)

        print(f"\nUpdating Merkle tree on node: {node['name']}")

        composite_info = CompositeInfo.fetch(conn, f"{schema}_{table}_key_type")
        register_composite(composite_info, conn, factory=lambda *args: tuple(args))

        try:
            # Start transaction with repeatable read isolation
            with conn.cursor() as cur:
                # Get all dirty and new blocks that need updating
                cur.execute(
                    sql.SQL(GET_DIRTY_AND_NEW_BLOCKS).format(
                        mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                    )
                )
                blocks_to_update = cur.fetchall()

                if not blocks_to_update:
                    print(f"No updates needed for {node['name']}")
                    conn.commit()
                    continue

                # First identify blocks that might need splitting based on insert count
                cur.execute(
                    sql.SQL(FIND_BLOCKS_TO_SPLIT).format(
                        mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
                    ),
                    [SPLIT_THRESHOLD, [b[0] for b in blocks_to_update]],
                )
                blocks_to_split = cur.fetchall()

                if blocks_to_split:
                    print(
                        f"Found {len(blocks_to_split)} blocks that may need splitting"
                    )
                    split_blocks(
                        conn,
                        schema,
                        table,
                        key,
                        blocks_to_split,
                        block_size,
                    )

                if mtree_task.rebalance:
                    mtree_table_id = sql.Identifier(f"ace_mtree_{schema}_{table}")

                    if is_composite:
                        cur.execute(
                            sql.SQL(FIND_BLOCKS_TO_MERGE_COMPOSITE).format(
                                mtree_table=mtree_table_id,
                                schema=sql.Identifier(schema),
                                table=sql.Identifier(table),
                                key_columns=sql.SQL(", ").join(
                                    [sql.Identifier(col) for col in key_columns]
                                ),
                                merge_threshold=MERGE_THRESHOLD,
                            ),
                            [
                                [b[0] for b in blocks_to_update],
                            ],
                        )
                    else:
                        cur.execute(
                            sql.SQL(FIND_BLOCKS_TO_MERGE_SIMPLE).format(
                                mtree_table=mtree_table_id,
                                schema=sql.Identifier(schema),
                                table=sql.Identifier(table),
                                key=sql.Identifier(key),
                                merge_threshold=MERGE_THRESHOLD,
                            ),
                            [
                                [b[0] for b in blocks_to_update],
                            ],
                        )
                    blocks_to_merge = cur.fetchall()

                    if blocks_to_merge:
                        print(
                            f"Found {len(blocks_to_merge)} blocks that may need merging"
                        )
                        merge_blocks(
                            conn,
                            schema,
                            table,
                            key,
                            blocks_to_merge,
                            block_size,
                        )

                # Get final list of blocks to update (including newly modified ones)
                cur.execute(
                    sql.SQL(GET_DIRTY_AND_NEW_BLOCKS).format(
                        mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                    )
                )
                blocks_to_update = cur.fetchall()

                if not blocks_to_update:
                    print(f"No updates needed for {node['name']}")
                    conn.commit()
                    continue

                print(f"Found {len(blocks_to_update)} blocks to update")

                affected_positions = []
                for block in tqdm(blocks_to_update, desc="Recomputing leaf hashes"):
                    node_position = block[0]
                    range_start = block[1]
                    range_end = block[2]

                    if is_composite:
                        where_conditions = []

                        pkey_cols = sql.SQL(", ").join(
                            sql.Identifier(col) for col in key_columns
                        )
                        where_conditions.append(
                            sql.SQL("({pkey_cols}) >= ({pkey_values})").format(
                                pkey_cols=pkey_cols,
                                pkey_values=sql.SQL(", ").join(
                                    sql.Literal(val) for val in range_start
                                ),
                            )
                        )
                        if range_end is not None:
                            where_conditions.append(
                                sql.SQL("({pkey_cols}) <= ({pkey_values})").format(
                                    pkey_cols=pkey_cols,
                                    pkey_values=sql.SQL(", ").join(
                                        sql.Literal(val) for val in range_end
                                    ),
                                )
                            )

                        if not where_conditions:
                            where_clause = sql.SQL("TRUE")
                        else:
                            where_clause = sql.SQL(" AND ").join(where_conditions)
                    else:
                        where_conditions = []

                        if range_start is not None:
                            where_conditions.append(
                                sql.SQL("{pkey_col} >= {pkey_value}").format(
                                    pkey_col=sql.Identifier(key),
                                    pkey_value=sql.Literal(range_start),
                                )
                            )

                        if range_end is not None:
                            where_conditions.append(
                                sql.SQL("{pkey_col} <= {pkey_value}").format(
                                    pkey_col=sql.Identifier(key),
                                    pkey_value=sql.Literal(range_end),
                                )
                            )

                        if not where_conditions:
                            where_clause = sql.SQL("TRUE")
                        else:
                            where_clause = sql.SQL(" AND ").join(where_conditions)

                    # Hitting this case would mean that the last block was updated,
                    # but splitting wasn't necessary. In this case, we need to update
                    # the range_end to the maximum value of the key.
                    if range_end is None and range_start is not None:
                        if is_composite:
                            pkey_cols = sql.SQL(", ").join(
                                sql.Identifier(col) for col in key_columns
                            )
                            pkey_values = sql.SQL(", ").join(
                                sql.Literal(val) for val in range_start
                            )

                            cur.execute(
                                sql.SQL(GET_MAX_VAL_COMPOSITE).format(
                                    schema=sql.Identifier(schema),
                                    table=sql.Identifier(table),
                                    pkey_cols=pkey_cols,
                                    pkey_values=pkey_values,
                                )
                            )
                            max_vals = cur.fetchone()
                            if max_vals is not None:
                                end = max_vals
                                cur.execute(
                                    sql.SQL(UPDATE_MAX_VAL).format(
                                        mtree_table=sql.Identifier(
                                            f"ace_mtree_{schema}_{table}"
                                        ),
                                    ),
                                    (end, node_position),
                                )
                        else:
                            cur.execute(
                                sql.SQL(GET_MAX_VAL_SIMPLE).format(
                                    schema=sql.Identifier(schema),
                                    table=sql.Identifier(table),
                                    key=sql.Identifier(key),
                                ),
                                (range_start,),
                            )
                            max_val = cur.fetchone()[0]
                            if max_val is not None:
                                end = max_val
                                cur.execute(
                                    sql.SQL(UPDATE_MAX_VAL).format(
                                        mtree_table=sql.Identifier(
                                            f"ace_mtree_{schema}_{table}"
                                        ),
                                    ),
                                    (end, node_position),
                                )

                    cur.execute(
                        sql.SQL(COMPUTE_LEAF_HASHES).format(
                            schema=sql.Identifier(schema),
                            table=sql.Identifier(table),
                            where_clause=where_clause,
                            columns=sql.SQL(", ").join(
                                [
                                    sql.Identifier(col)
                                    for col in mtree_task.fields.cols.split(",")
                                ]
                            ),
                            key=sql.SQL(", ").join(
                                [sql.Identifier(col) for col in key_columns]
                            ),
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                        )
                    )
                    result = cur.fetchone()[0]
                    args = {
                        "leaf_hash": result,
                        "node_position": node_position,
                    }
                    cur.execute(
                        sql.SQL(UPDATE_LEAF_HASHES).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                        ),
                        args,
                    )
                    affected_positions.append(node_position)

                if affected_positions:
                    cur.execute(
                        sql.SQL(DELETE_PARENT_NODES).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
                        )
                    )

                    level = 0

                    pbar = tqdm(
                        desc="Building parent nodes",
                        total=len(affected_positions),
                        leave=False,
                    )

                    while True:
                        cur.execute(
                            sql.SQL(BUILD_PARENT_NODES).format(
                                mtree_table=sql.Identifier(
                                    f"ace_mtree_{schema}_{table}"
                                ),
                            ),
                            {"node_level": level},
                        )

                        count = cur.fetchone()[0]
                        if count <= 1:
                            break
                        level += 1
                        pbar.update(count)

                    cur.execute(
                        sql.SQL(CLEAR_DIRTY_FLAGS).format(
                            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                        ),
                        {"node_positions": affected_positions},
                    )

                conn.commit()
                print(
                    f"Successfully updated {len(affected_positions)} "
                    "blocks and their parent nodes"
                )

        except Exception as e:
            conn.rollback()
            traceback.print_exc()
            raise AceException(
                f"Error updating Merkle tree on {node['name']}: {str(e)}"
            )

    mtree_task.connection_pool.close_all()


def find_mismatched_leaves(
    conn1, conn2, schema, table, parent_level, parent_position, pbar=None
):
    """
    Recursively traverse the merkle tree to find mismatched leaf nodes.
    Returns a list of leaf node positions that have different hashes.
    """
    mismatched_leaves = set()

    # Get children of this parent node from both nodes
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()

    params = {"parent_level": parent_level, "parent_position": parent_position}

    cur1.execute(
        sql.SQL(GET_NODE_CHILDREN).format(
            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
        ),
        params,
    )
    node1_children = cur1.fetchall()

    cur2.execute(
        sql.SQL(GET_NODE_CHILDREN).format(
            mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
        ),
        params,
    )
    node2_children = cur2.fetchall()

    if pbar is not None:
        pbar.update(len(node1_children))

    #  This was a bit tricky to get right:
    #  1. It's possible that the there is a mismatch in the tree size between the
    #     two nides. This could happen if one of the nodes had a flurry of inserts
    #     or deletes that did not get replicated.
    #  2. In such cases, not only do we need to add mismatched leaves to the
    #     mismatched set, but we need to add all leaves that don't have peers
    #     on the other nodes.
    #
    #     E.g., consider t1 and t2:
    #
    #          p0                           p2
    #          /\                          / \
    #         /  \                        /   \
    #        a    b                      /     \
    #                                   p1      p0'
    #                                  /       / \
    #                                 /       /   \
    #                                c       a'    b
    #
    #     --------------              ------------------
    #          t1                            t2
    #
    #   Now, say that the leaf node 'a' is different between t1 and t2. While
    #   recursing down the tree, if at any point, we find a leaf node that does not
    #   have a peer on the other tree, we need to add it to the mismatched set.
    #   In the above example, there is no peer for leaf node 'c'. Node 'a' will
    #   anyway get added since its hashes don't match.

    for child1, child2 in zip_longest(node1_children, node2_children, fillvalue=None):
        level1, pos1, hash1 = child1 if child1 else (None, None, None)
        level2, pos2, hash2 = child2 if child2 else (None, None, None)

        if hash1 is None or hash2 is None:
            if (level1 == 0) or (level2 == 0):
                mismatched_leaves.add(pos1 if level1 is not None else pos2)
            else:
                # Recurse down this branch to find mismatched leaves
                child_mismatches = find_mismatched_leaves(
                    conn1,
                    conn2,
                    schema,
                    table,
                    level1 if level1 is not None else level2,
                    pos1 if pos1 is not None else pos2,
                    pbar,
                )
                mismatched_leaves.update(child_mismatches)
        elif hash1 != hash2:
            if level1 == 0:
                mismatched_leaves.add(pos1)
            else:
                # Recurse down this branch to find mismatched leaves
                child1_mismatches = find_mismatched_leaves(
                    conn1, conn2, schema, table, level1, pos1, pbar
                )
                mismatched_leaves.update(child1_mismatches)

    return mismatched_leaves


def get_pkey_batches(node1_conn, node2_conn, schema, table, mismatched_positions):
    """
    Get range_start and range_end values for mismatched leaf nodes
    and format them into batches for parallel processing.

    This is vastly different from the get_pkey_offsets used in regular table-diff.
    Here, we first combine all ranges from both nodes, sort them, and then build
    the batches. Here's how it works:

    We will use a problemmatic case that previously led to a significant number of
    duplicates to illustrate how this algorithm works.

    Consider the following ranges:
    Node 1: [
        ([1], [207]),
        ([207], [786]),
        ...
        ([9676], [10000]),
        ([10000], [None])
    ]


    Node 2 (because it's missing rows 1-8000) [
        ([1], [8079]),
        ([8079], [8479]),
        ...
        ([9676], [10000]),
        ([10000], [None])
    ]

    Previously, we would have gotten:
    batches = [
        ([1], [8079]),
        ([207], [8479]),
        ([786], [8809]),
        ([1460], [9165]),
        ([1988], [9676]),
        ([2599], [10000]),
        ([3127], [3344]),
        ([3344], [3803]),
        ([3803], [4610]),
        ...
        ([10000], [None])
    ]

    Which is clearly wrong, since we have several overlapping ranges that lead to
    duplicates in the diff report.

    The correct way is to first combine all ranges, sort them, and then test
    the membership of inidividual ranges in the union of all ranges.

    So, after combining and sorting our example ranges, we get:

    batches  = [
        ([1], [207]),
        ([207], [786]),
        ([786], [1460]),
        ...
        ([9676], [10000]),
        ([10000], [None])
    ]

    Testing the membership of computed ranges in the union of all intervals is
    important because if both nodes are missing, say, rows 2000-3500, then, even
    though we might have computed a range that falls in this interval, it is invalid
    because that range does not intersect with any of the [s, e) intervals of the
    union of all ranges.
    """

    node1_composite_info = CompositeInfo.fetch(node1_conn, f"{schema}_{table}_key_type")
    node2_composite_info = CompositeInfo.fetch(node2_conn, f"{schema}_{table}_key_type")

    register_composite(
        node1_composite_info, node1_conn, factory=lambda *args: tuple(args)
    )
    register_composite(
        node2_composite_info, node2_conn, factory=lambda *args: tuple(args)
    )

    with node1_conn.cursor() as cur1, node2_conn.cursor() as cur2:
        cur1.execute(
            sql.SQL(GET_LEAF_RANGES).format(
                mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
            ),
            {"node_positions": mismatched_positions},
        )
        leaf_ranges1 = cur1.fetchall()

        cur2.execute(
            sql.SQL(GET_LEAF_RANGES).format(
                mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
            ),
            {"node_positions": mismatched_positions},
        )
        leaf_ranges2 = cur2.fetchall()

    all_ranges = leaf_ranges1 + leaf_ranges2
    boundaries = []
    for start, end in all_ranges:
        if start is not None:
            boundaries.append(start)
        if end is not None:
            boundaries.append(end)

    boundaries = sorted(set(boundaries))

    slices = []
    for i in range(len(boundaries) - 1):
        s = boundaries[i]
        e = boundaries[i + 1]

        # We'll form the half-open interval [s, e)
        # but only keep it if it intersects any mismatch.
        if interval_in_union(s, e, all_ranges):
            slices.append((s, e))

    # TODO: Fix this!
    # # We always need the last boundary to be (max_key, None), otherwise,
    # # we risk missing diffs.
    # last_boundary = boundaries[-1] if boundaries else None

    # if last_boundary is not None:
    #     slices.append((last_boundary, None))

    batches = []
    for start, end in slices:
        batches.append(([start], [end]))

    return batches


def interval_in_union(s, e, intervals):
    """
    Returns True if the half-open [s, e) intersects with
    the union of all intervals in 'intervals'.
    """
    for start, end in intervals:
        start = start if start is not None else float("-inf")
        end = end if end is not None else float("inf")

        # If [s,e) intersects [start,end)
        if not (e <= start or s >= end):
            return True
    return False


def compare_ranges(worker_id, shared_objects, worker_state, work_item):
    p_key = shared_objects["p_key"]
    schema_name = shared_objects["schema_name"]
    table_name = shared_objects["table_name"]
    cols = shared_objects["cols_list"]
    simple_primary_key = shared_objects["simple_primary_key"]
    stop_event = shared_objects["stop_event"]

    node_pair_key, batch = work_item
    host1, host2 = node_pair_key.split("/")

    worker_diffs = {}
    total_diffs = 0

    if stop_event.is_set():
        return

    # Process all batches at once if possible
    if len(batch) == 1:
        pkey1, pkey2 = batch[0]

        where_clause_parts = []

        if simple_primary_key:
            if pkey1[0] is not None:
                where_clause_parts.append(
                    sql.SQL("{p_key} >= {pkey1}").format(
                        p_key=sql.Identifier(p_key), pkey1=sql.Literal(pkey1[0])
                    )
                )
            if pkey2[0] is not None:
                where_clause_parts.append(
                    sql.SQL("{p_key} <= {pkey2}").format(
                        p_key=sql.Identifier(p_key), pkey2=sql.Literal(pkey2[0])
                    )
                )
        else:
            if pkey1[0] is not None:
                where_clause_parts.append(
                    sql.SQL("({p_key}) >= ({pkey1})").format(
                        p_key=sql.SQL(", ").join(
                            [sql.Identifier(col.strip()) for col in p_key.split(",")]
                        ),
                        pkey1=sql.SQL(", ").join(
                            [sql.Literal(val) for val in pkey1[0]]
                        ),
                    )
                )
            if pkey2[0] is not None:
                where_clause_parts.append(
                    sql.SQL("({p_key}) <= ({pkey2})").format(
                        p_key=sql.SQL(", ").join(
                            [sql.Identifier(col.strip()) for col in p_key.split(",")]
                        ),
                        pkey2=sql.SQL(", ").join(
                            [sql.Literal(val) for val in pkey2[0]]
                        ),
                    )
                )

        where_clause = (
            sql.SQL(" AND ").join(where_clause_parts)
            if where_clause_parts
            else sql.SQL("TRUE")
        )

    else:
        # Multiple batches - use IN or BETWEEN for better performance
        if simple_primary_key:
            # For simple keys, we can use a more efficient approach
            # with a single query. Find the min and max values across all batches
            min_key = min(
                b[0][0] if b[0] is not None else None for b in batch if b[0] is not None
            )
            max_key = max(
                b[1][0] if b[1] is not None else None for b in batch if b[1] is not None
            )

            where_clause_parts = []
            if min_key is not None:
                where_clause_parts.append(
                    sql.SQL("{p_key} >= {min_key}").format(
                        p_key=sql.Identifier(p_key), min_key=sql.Literal(min_key)
                    )
                )
            if max_key is not None:
                where_clause_parts.append(
                    sql.SQL("{p_key} <= {max_key}").format(
                        p_key=sql.Identifier(p_key), max_key=sql.Literal(max_key)
                    )
                )

            where_clause = (
                sql.SQL(" AND ").join(where_clause_parts)
                if where_clause_parts
                else sql.SQL("TRUE")
            )
        else:
            # For composite keys, we need to handle each batch separately
            # But we can still combine them with OR for a single query
            or_clauses = []

            for pkey1, pkey2 in batch:
                and_clauses = []

                if pkey1 is not None:
                    and_clauses.append(
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
                    and_clauses.append(
                        sql.SQL("({p_key}) <= ({pkey2})").format(
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

                if and_clauses:
                    or_clauses.append(
                        sql.SQL("(") + sql.SQL(" AND ").join(and_clauses) + sql.SQL(")")
                    )

            where_clause = (
                sql.SQL(" OR ").join(or_clauses) if or_clauses else sql.SQL("TRUE")
            )

    block_sql = sql.SQL(COMPARE_BLOCKS_SQL).format(
        table_name=sql.SQL("{}.{}").format(
            sql.Identifier(schema_name),
            sql.Identifier(table_name),
        ),
        where_clause=where_clause,
    )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(ace_core.run_query, worker_state, host1, block_sql),
            executor.submit(ace_core.run_query, worker_state, host2, block_sql),
        ]
        results = [f.result() for f in futures if not f.exception()]

    errors = [f.exception() for f in futures if f.exception()]

    if errors:
        return {
            "status": config.BLOCK_ERROR,
            "errors": [str(error) for error in errors],
            "batch": batch,
            "node_pair": node_pair_key,
        }

    if len(results) < 2:
        return {
            "status": config.BLOCK_ERROR,
            "errors": ["Failed to get results from both nodes"],
            "batch": batch,
            "node_pair": node_pair_key,
        }

    t1_result, t2_result = results

    # Use a more efficient approach for comparison
    # Create dictionaries keyed by row values for faster lookups
    # This avoids the expensive string conversion for every value, and the
    # set difference using ordered_set
    t1_dict = {}
    t2_dict = {}

    for row in t1_result:
        row_key = tuple(x.hex() if isinstance(x, bytes) else x for x in row)
        t1_dict[row_key] = row

    t2_only = []
    for row in t2_result:
        row_key = tuple(x.hex() if isinstance(x, bytes) else x for x in row)
        t2_dict[row_key] = row

        if row_key not in t1_dict:
            t2_only.append(row_key)

    t1_only = [key for key in t1_dict.keys() if key not in t2_dict]

    # It is possible that the hash mismatch is a false negative.
    # E.g., if there are extraneous spaces in the JSONB column.
    # In this case, we can still consider the block to be OK.
    if not t1_only and not t2_only:
        return {
            "status": config.BLOCK_OK,
            "diffs": {},
            "total_diffs": 0,
            "batch": batch,
            "node_pair": node_pair_key,
        }

    if node_pair_key not in worker_diffs:
        worker_diffs[node_pair_key] = {host1: [], host2: []}

    for row_key in t1_only:
        worker_diffs[node_pair_key][host1].append(
            dict(zip(cols, (str(x) for x in row_key)))
        )

    for row_key in t2_only:
        worker_diffs[node_pair_key][host2].append(
            dict(zip(cols, (str(x) for x in row_key)))
        )

    total_diffs = max(len(t1_only), len(t2_only))

    return {
        "status": config.BLOCK_MISMATCH,
        "diffs": worker_diffs,
        "total_diffs": total_diffs,
        "batch": batch,
        "node_pair": node_pair_key,
    }


def merkle_tree_diff(mtree_task: MerkleTreeTask) -> None:
    """
    Compare merkle trees between nodes and perform table diff on mismatched blocks.
    """
    ace.merkle_tree_checks(mtree_task, skip_validation=True)

    # It is imperative that we call update_mtree before calling merkle_tree_diff.
    # Otherwise, we're comparing stale data.
    update_mtree(mtree_task, skip_all_checks=True)

    schema = mtree_task.fields.l_schema
    table = mtree_task.fields.l_table
    key = mtree_task.fields.key
    simple_primary_key = len(key.split(",")) == 1

    diff_dict = {}
    lookup_dict = {}
    errors = False
    mismatch = False
    total_diffs = 0
    diffs_exceeded = False
    error_list = []

    total_rows = 0

    start_time = datetime.now()

    node_pairs = list(combinations(mtree_task.fields.cluster_nodes, 2))

    all_node_pair_batches = []

    for node1, node2 in node_pairs:
        print(f"\nComparing merkle trees between {node1['name']} and {node2['name']}")

        _, conn1 = mtree_task.connection_pool.get_cluster_node_connection(node1)
        _, conn2 = mtree_task.connection_pool.get_cluster_node_connection(node2)

        try:
            cur1 = conn1.cursor()
            cur2 = conn2.cursor()

            if not total_rows:
                cur1.execute(
                    sql.SQL(GET_ROW_COUNT_ESTIMATE).format(
                        schema=sql.Literal(schema),
                        table=sql.Literal(table),
                    )
                )
                row_count = cur1.fetchone()[0]
                if row_count:
                    total_rows = row_count * len(mtree_task.fields.node_list)

            cur1.execute(
                sql.SQL(GET_ROOT_NODE).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                )
            )
            root1 = cur1.fetchone()

            cur2.execute(
                sql.SQL(GET_ROOT_NODE).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}"),
                )
            )
            root2 = cur2.fetchone()

            if not root1 or not root2:
                print(f"No merkle tree found for {schema}.{table}")
                continue

            root1_pos, root1_hash = root1
            root2_pos, root2_hash = root2

            # Get the root level
            cur1.execute(
                sql.SQL(GET_MAX_NODE_LEVEL).format(
                    mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
                )
            )
            root_level = cur1.fetchone()[0]

            # If root hashes match, trees are identical
            if root1_hash == root2_hash:
                print("Merkle trees are identical")
                continue

            # Get an estimate of the total number of nodes to traverse
            # This is a rough estimate based on the tree structure
            # For a binary tree with L levels, the max number of nodes is 2^(L+1) - 1
            # This is not really necessary, but when the nodes are far apart
            # (network-wise), or the tree is huge, find_mismatched_leaves() can
            # take time. So, we need to show some progress while it's running,
            # lest the user should think the script has frozen.
            estimated_nodes = 2 ** (root_level + 1) - 1

            print("Trees differ - traversing to find mismatched leaf nodes...")

            with tqdm(total=estimated_nodes, desc="Traversing merkle tree") as pbar:
                mismatched_leaves = list(
                    find_mismatched_leaves(
                        conn1,
                        conn2,
                        schema,
                        table,
                        parent_level=root_level,
                        parent_position=root1_pos,
                        pbar=pbar,
                    )
                )
                pbar.n = estimated_nodes
                pbar.refresh()

            if not mismatched_leaves:
                print("No mismatched leaf nodes found")
                continue

            pkey_batches = get_pkey_batches(
                conn1, conn2, schema, table, mismatched_leaves
            )
            print(f"Found {len(pkey_batches)} mismatched blocks")

            node_pair_key = f"{node1['name']}/{node2['name']}"
            for batch in pkey_batches:
                all_node_pair_batches.append((node_pair_key, (node1, node2), batch))

        except Exception as e:
            conn1.rollback()
            conn2.rollback()
            raise AceException(f"Error comparing merkle trees: {str(e)}")

        finally:
            conn1.close()
            conn2.close()

    if all_node_pair_batches:
        batches_by_pair = {}
        for node_pair_key, node_pair, batch in all_node_pair_batches:
            if node_pair_key not in batches_by_pair:
                batches_by_pair[node_pair_key] = {"node_pair": node_pair, "batches": []}
            batches_by_pair[node_pair_key]["batches"].append(batch)

        work_items = []
        for node_pair_key, pair_data in batches_by_pair.items():
            node_pair = pair_data["node_pair"]

            for i in range(0, len(pair_data["batches"]), mtree_task.batch_size):
                batch_chunk = pair_data["batches"][i : i + mtree_task.batch_size]
                work_items.append((node_pair_key, batch_chunk))

        print(f"\nProcessing {len(work_items)} batch chunks across all node pairs")

        mtree_task.connection_pool.close_all()

        max_workers = int(os.cpu_count() * mtree_task.max_cpu_ratio)
        n_jobs = min(len(work_items), max_workers)
        stop_event = Manager().Event()

        shared_objects = {
            "p_key": key,
            "schema_name": schema,
            "table_name": table,
            "cols_list": mtree_task.fields.cols.split(","),
            "simple_primary_key": simple_primary_key,
            "stop_event": stop_event,
            "task": mtree_task,
        }

        with WorkerPool(
            n_jobs=n_jobs,
            shared_objects=shared_objects,
            use_worker_state=True,
            pass_worker_id=True,
        ) as pool:
            for result in pool.imap_unordered(
                compare_ranges,
                make_single_arguments(work_items),
                iterable_len=len(work_items),
                worker_init=ace_core.init_conn_pool,
                worker_exit=ace_core.close_conn_pool,
                progress_bar=True,
            ):
                if result["status"] == config.BLOCK_ERROR:
                    errors = True
                    error_list.append(
                        {
                            "node_pair": result["node_pair"],
                            "batch": result["batch"],
                            "errors": result["errors"],
                        }
                    )
                    stop_event.set()
                    break

                if result["status"] == config.BLOCK_MISMATCH:
                    mismatch = True
                    for node_pair, node_diffs in result["diffs"].items():
                        if node_pair not in diff_dict:
                            diff_dict[node_pair] = {}

                        if node_pair not in lookup_dict:
                            lookup_dict[node_pair] = {}

                        for node, diffs in node_diffs.items():
                            if node not in diff_dict[node_pair]:
                                diff_dict[node_pair][node] = []

                            if node not in lookup_dict[node_pair]:
                                lookup_dict[node_pair][node] = set()

                            if simple_primary_key:
                                diff_dict[node_pair][node].extend(
                                    diff
                                    for diff in diffs
                                    if diff[key] not in lookup_dict[node_pair][node]
                                )
                            else:
                                diff_dict[node_pair][node].extend(
                                    diff
                                    for diff in diffs
                                    if tuple(diff[key] for key in key.split(","))
                                    not in lookup_dict[node_pair][node]
                                )

                            if simple_primary_key:
                                lookup_dict[node_pair][node].update(
                                    diff[key] for diff in diffs
                                )
                            else:
                                lookup_dict[node_pair][node].update(
                                    tuple(diff[key] for key in key.split(","))
                                    for diff in diffs
                                )

                    total_diffs += result["total_diffs"]
                    if total_diffs >= config.MAX_DIFF_ROWS:
                        diffs_exceeded = True
                        stop_event.set()
                        break

            if diffs_exceeded:
                util.message(
                    "Prematurely terminated jobs since diffs have"
                    " exceeded MAX_ALLOWED_DIFFS",
                    p_state="warning",
                    quiet_mode=mtree_task.quiet_mode,
                )

    run_time = util.round_timedelta(datetime.now() - start_time).total_seconds()
    run_time_str = f"{run_time:.2f}"

    mtree_task.scheduler.task_status = "COMPLETED"
    mtree_task.scheduler.finished_at = datetime.now()
    mtree_task.scheduler.time_taken = run_time
    mtree_task.scheduler.task_context = {
        "total_rows": total_rows,
        "mismatch": mismatch,
        "diffs_summary": mtree_task.diff_summary if mismatch else {},
        "errors": [],
    }

    print()

    if errors:
        context = {"total_rows": total_rows, "mismatch": mismatch, "errors": error_list}
        ace.handle_task_exception(mtree_task, context)

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
                quiet_mode=mtree_task.quiet_mode,
            )

        else:
            util.message(
                "TABLES DO NOT MATCH",
                p_state="warning",
                quiet_mode=mtree_task.quiet_mode,
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
            mtree_task.diff_summary[node_pair] = diff_count
            util.message(
                f"FOUND {diff_count} DIFFS BETWEEN {node1} AND {node2}",
                p_state="warning",
                quiet_mode=mtree_task.quiet_mode,
            )

        try:
            if mtree_task.output == "json" or mtree_task.output == "html":
                mtree_task.diff_file_path = ace.write_diffs_json(
                    mtree_task,
                    diff_dict,
                    mtree_task.fields.col_types,
                    quiet_mode=mtree_task.quiet_mode,
                )

                if mtree_task.output == "html":
                    ace_html_reporter.generate_html(
                        mtree_task.diff_file_path, mtree_task.fields.key.split(",")
                    )
            elif mtree_task.output == "csv":
                ace.write_diffs_csv(diff_dict)
        except Exception as e:
            context = {
                "total_rows": total_rows,
                "mismatch": mismatch,
                "errors": [str(e)],
            }
            ace.handle_task_exception(mtree_task, context)
            raise e

    else:
        util.message(
            "TABLES MATCH OK\n", p_state="success", quiet_mode=mtree_task.quiet_mode
        )

    util.message(
        f"TOTAL ROWS CHECKED = {total_rows}\nRUN TIME = {run_time_str} seconds",
        p_state="info",
        quiet_mode=mtree_task.quiet_mode,
    )

    mtree_task.scheduler.task_status = "COMPLETED"
    mtree_task.scheduler.finished_at = datetime.now()
    mtree_task.scheduler.time_taken = run_time
    mtree_task.scheduler.task_context = {
        "total_rows": total_rows,
        "mismatch": mismatch,
        "diffs_summary": mtree_task.diff_summary if mismatch else {},
        "errors": [],
    }

    mtree_task.connection_pool.close_all()


def _mtree_init(conn) -> None:
    """
    Initialise the database with generic functions needed for Merkle trees.
    This only needs to be run once per database.

    Args:
        conn: Database connection
    """
    cur = conn.cursor()

    # We need pgcrypto for sha256
    cur.execute(sql.SQL("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))

    # We're defining an XOR operator here for building parent hashes
    # This is the optimisation Riak uses:
    # See: https://www.youtube.com/watch?v=TCiHqF_XTmE
    cur.execute(sql.SQL(CREATE_XOR_FUNCTION))

    # Metadata table where we keep track of tables, their approx. row counts,
    # and when the tree was last updated.
    cur.execute(sql.SQL("DROP TABLE IF EXISTS ace_mtree_metadata"))
    cur.execute(sql.SQL(CREATE_METADATA_TABLE))

    # Create generic functions for block identification and tracking
    cur.execute(sql.SQL(CREATE_BULK_TRIGGER_FUNCTION))

    conn.commit()
    print(f"Merkle tree objects initialised successfully on {conn.info.host}")


def mtree_init_helper(mtree_task: MerkleTreeTask) -> None:
    """
    CLI helper function to initialise the database with Merkle tree objects
    """

    for node in mtree_task.fields.cluster_nodes:
        try:
            _, conn = mtree_task.connection_pool.get_cluster_node_connection(node)
            _mtree_init(conn)
            conn.close()
        except Exception as e:
            raise AceException(
                f"Error initialising merkle tree objects on {node}: {str(e)}"
            )


def _mtree_table_teardown(conn, schema, table) -> None:
    """
    Teardown table-specific merkle tree objects
    """

    try:
        cur = conn.cursor()
        print(
            f"Dropping trigger trg_mtree_{schema}_{table}_insert_stmt"
            f" on {schema}.{table}"
        )
        print(
            f"Dropping trigger trg_mtree_{schema}_{table}_update_stmt"
            f" on {schema}.{table}"
        )
        print(
            f"Dropping trigger trg_mtree_{schema}_{table}_delete_stmt"
            f" on {schema}.{table}"
        )
        cur.execute(
            sql.SQL(DROP_MTREE_TRIGGERS).format(
                trigger=sql.SQL(f"trg_mtree_{schema}_{table}"),
                schema=sql.Identifier(schema),
                table=sql.Identifier(table),
            )
        )

        print(f"Dropping table ace_mtree_{schema}_{table}")

        cur.execute(
            sql.SQL(DROP_MTREE_TABLE).format(
                mtree_table=sql.Identifier(f"ace_mtree_{schema}_{table}")
            )
        )

        conn.commit()
        print(
            f"Dropped table-specific merkle tree objects on {conn.info.host}"
            f" for {schema}.{table}"
        )

    except Exception as e:
        raise AceException(
            f"Error tearing down table-specific merkle tree objects: {str(e)}"
        )


def _mtree_generic_teardown(conn) -> None:
    """
    Teardown generic merkle tree objects
    """

    try:
        cur = conn.cursor()
        print("Dropping XOR function")
        cur.execute(sql.SQL(DROP_XOR_FUNCTION))

        print("Dropping bulk trigger function")
        cur.execute(sql.SQL(DROP_BULK_TRIGGER_FUNCTION))

        print("Dropping metadata table")
        cur.execute(sql.SQL(DROP_METADATA_TABLE))

        conn.commit()
        print(f"Dropped generic merkle tree objects on {conn.info.host}")
    except Exception as e:
        raise AceException(f"Error tearing down generic merkle tree objects: {str(e)}")


def _mtree_teardown(conn, schema=None, table=None) -> None:
    """
    Core function to teardown generic merkle tree objects and/or table-specific objects
    """

    try:
        if schema and table:
            _mtree_table_teardown(conn, schema, table)
        else:
            _mtree_generic_teardown(conn)

        conn.commit()
    except Exception as e:
        raise AceException(f"Error tearing down merkle tree objects: {str(e)}")


def mtree_teardown_helper(mtree_task: MerkleTreeTask) -> None:
    """
    Teardown generic merkle tree objects and/or table-specific objects
    """

    for node in mtree_task.fields.cluster_nodes:
        try:
            _, conn = mtree_task.connection_pool.get_cluster_node_connection(node)
            print("=" * 20, f"Node: {node['name']}", "=" * 20)
            _mtree_teardown(
                conn,
                mtree_task.fields.l_schema if mtree_task.fields.l_schema else None,
                mtree_task.fields.l_table if mtree_task.fields.l_table else None,
            )
            print()
            conn.close()
        except Exception as e:
            raise AceException(
                f"Error tearing down merkle tree objects on {node['name']}: {str(e)}"
            )
