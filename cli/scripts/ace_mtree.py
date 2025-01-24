from mpire import WorkerPool
from mpire.utils import make_single_arguments
import os
from typing import Tuple, Any
from dataclasses import dataclass

import ace
import ace_config as config
from ace_data_models import TableDiffTask
from ace_exceptions import AceException
from ace_sql import (
    CREATE_METADATA_TABLE,
    CREATE_MTREE_TABLE,
    CREATE_BLOCK_ID_FUNCTION,
    CREATE_TRIGGER_FUNCTION,
    CREATE_TRIGGER,
    CREATE_XOR_FUNCTION,
    ESTIMATE_ROW_COUNT,
    GET_PKEY_TYPE,
    UPDATE_METADATA,
    CALCULATE_BLOCK_RANGES,
    COMPUTE_LEAF_HASHES,
    GET_BLOCK_RANGES,
    BUILD_PARENT_NODES,
)


@dataclass
class BlockBoundary:
    """Represents a block boundary for parallel processing"""

    block_id: int
    block_start: Tuple[Any, ...]
    block_end: Tuple[Any, ...]


def init_hash_conn_pool(shared_objects, worker_state):
    """Initialize connection pool for hash computation workers"""
    node = shared_objects["node"]
    conn_pool = shared_objects["conn_pool"]

    try:
        # TODO: Investigate why conn_pool.connect() fails here
        params, conn = conn_pool.get_cluster_node_connection(node)
        worker_state["conn"] = conn
        worker_state["cur"] = conn.cursor()

    except Exception as e:
        if "conn" in worker_state:
            try:
                worker_state["conn"].close()
            except Exception:
                pass
        raise AceException(f"Error initializing worker connection: {str(e)}")


def close_hash_conn_pool(shared_objects, worker_state):
    """Close connection pool for hash computation workers"""
    try:
        if "cur" in worker_state:
            worker_state["cur"].close()
        if "conn" in worker_state:
            worker_state["conn"].close()
    except Exception as e:
        raise AceException(f"Error closing worker connection: {str(e)}")


def compute_block_hashes(shared_objects, worker_state, args):
    """Worker function to compute hashes for a range of blocks"""
    block_boundary, sql = args

    try:
        cur = worker_state["cur"]
        conn = worker_state["conn"]

        conn.rollback()

        cur.execute("SELECT 1")
        cur.fetchone()

        params = {
            "node_position": block_boundary.block_id,
            "range_start": block_boundary.block_start,
            "range_end": block_boundary.block_end,
        }

        cur.execute(sql, params)
        results = cur.fetchall()

        if not results:
            msg = (
                f"No hash computed for block {block_boundary.block_id} "
                f"(range: {block_boundary.block_start} "
                f"to {block_boundary.block_end})"
            )
            raise AceException(msg)

        conn.commit()
        return results

    except Exception as e:
        conn.rollback()

        msg = (
            f"Error computing hash for block {block_boundary.block_id} "
            f"(start: {block_boundary.block_start}, "
            f"end: {block_boundary.block_end}): {str(e)}"
        )
        raise AceException(msg)


def build_mtree(cluster_name: str, table_name: str, dbname: str = None) -> None:
    """
    Build a Merkle tree for a table using parallel processing.
    The tree is stored in a separate table for each source table.
    Parent nodes are computed using XOR of child hashes.

    Args:
        cluster_name (str): Name of the cluster
        table_name (str): Name of the table to build tree for
        dbname (str, optional): Database name. Defaults to None.
    """

    td_task = TableDiffTask(
        cluster_name=cluster_name,
        _table_name=table_name,
        _dbname=dbname,
        block_rows=config.MTREE_BLOCK_SIZE,
        max_cpu_ratio=config.MAX_CPU_RATIO_DEFAULT,
        output="json",
        _nodes="all",
        batch_size=config.BATCH_SIZE_DEFAULT,
        quiet_mode=False,
        table_filter=None,
        invoke_method="cli",
    )

    ace.table_diff_checks(td_task)

    schema_table = f"{td_task.fields.l_schema}.{td_task.fields.l_table}"
    print(f"\nBuilding merkle tree for {schema_table}")

    for node in td_task.fields.cluster_nodes:
        print(f"\nProcessing node: {node['name']}")
        params, conn = td_task.connection_pool.get_cluster_node_connection(node)

        try:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

                # We're defining an XOR operator here for building parent hashes
                # This is the optimisation Riak uses:
                # See: https://www.youtube.com/watch?v=TCiHqF_XTmE
                cur.execute(CREATE_XOR_FUNCTION)
                cur.execute(CREATE_METADATA_TABLE)

                cur.execute(
                    GET_PKEY_TYPE,
                    (
                        td_task.fields.l_schema,
                        td_task.fields.l_table,
                        td_task.fields.key,
                    ),
                )
                pkey_type = cur.fetchone()[0]

                cur.execute(
                    "DROP TABLE IF EXISTS ace_mtree_{schema}_{table}".format(
                        schema=td_task.fields.l_schema,
                        table=td_task.fields.l_table,
                    )
                )

                cur.execute(
                    CREATE_MTREE_TABLE.format(
                        schema=td_task.fields.l_schema,
                        table=td_task.fields.l_table,
                        pkey_type=pkey_type,
                    )
                )

                cur.execute(
                    ESTIMATE_ROW_COUNT,
                    (td_task.fields.l_schema, td_task.fields.l_table),
                )
                total_rows = cur.fetchone()[0]
                num_blocks = (total_rows - 1) // config.MTREE_BLOCK_SIZE + 1

                cur.execute(
                    UPDATE_METADATA,
                    (
                        td_task.fields.l_schema,
                        td_task.fields.l_table,
                        total_rows,
                        num_blocks,
                    ),
                )

                cur.execute(
                    CREATE_BLOCK_ID_FUNCTION.format(
                        schema=td_task.fields.l_schema,
                        table=td_task.fields.l_table,
                        pkey_name=td_task.fields.key,
                        pkey_type=pkey_type,
                    )
                )

                cur.execute(
                    CREATE_TRIGGER_FUNCTION.format(
                        schema=td_task.fields.l_schema,
                        table=td_task.fields.l_table,
                        pkey=td_task.fields.key,
                    )
                )
                cur.execute(
                    CREATE_TRIGGER.format(
                        schema=td_task.fields.l_schema,
                        table=td_task.fields.l_table,
                    )
                )

                msg = (
                    f"Calculating block ranges for {num_blocks:,} blocks "
                    f"(~{total_rows:,} rows)"
                )
                print(msg)

                cur.execute(
                    CALCULATE_BLOCK_RANGES.format(
                        schema=td_task.fields.l_schema,
                        table=td_task.fields.l_table,
                        key=td_task.fields.key,
                        num_blocks=num_blocks,
                    ),
                )

                print("Computing leaf node hashes...")

                cur.execute(
                    GET_BLOCK_RANGES.format(
                        schema=td_task.fields.l_schema,
                        table=td_task.fields.l_table,
                    )
                )
                blocks = cur.fetchall()

                work_items = []
                for block in blocks:
                    column_list = []
                    for col in td_task.fields.cols.split(","):
                        column_list.append(
                            f"CASE WHEN {col} IS NULL THEN 'NULL' "
                            f"WHEN {col}::text = '' THEN 'EMPTY' "
                            f"ELSE {col}::text END"
                        )
                    column_expr = ",\n        ".join(column_list)

                    sql = COMPUTE_LEAF_HASHES.format(
                        schema=td_task.fields.l_schema,
                        table=td_task.fields.l_table,
                        key=td_task.fields.key,
                        columns=column_expr,
                    )
                    work_items.append(
                        (
                            BlockBoundary(
                                block_id=block[0],
                                block_start=block[1],
                                block_end=block[2],
                            ),
                            sql,
                        )
                    )

                print(f"Computing hashes for {len(blocks)} blocks...")
                max_workers = int(config.MAX_CPU_RATIO_DEFAULT * os.cpu_count())
                n_jobs = min(len(work_items), max_workers)

                shared_objects = {
                    "node": node,
                    "conn_pool": td_task.connection_pool,
                }

                with WorkerPool(
                    n_jobs=n_jobs,
                    shared_objects=shared_objects,
                    use_worker_state=True,
                ) as pool:
                    results = list(
                        pool.imap_unordered(
                            compute_block_hashes,
                            make_single_arguments(work_items),
                            iterable_len=len(work_items),
                            worker_init=init_hash_conn_pool,
                            progress_bar=True,
                        )
                    )

                    failed = [r for r in results if not r]
                    if failed:
                        raise AceException(
                            f"Failed to compute hashes for {len(failed)} blocks"
                        )

                print("\nBuilding parent nodes...")

                # Let's just use a new conn here to be safe
                _, new_conn = td_task.connection_pool.get_cluster_node_connection(node)
                new_cur = new_conn.cursor()

                new_cur.execute(
                    """
                    DELETE FROM ace_mtree_{schema}_{table}
                    WHERE node_level > 0
                    """.format(
                        schema=td_task.fields.l_schema,
                        table=td_task.fields.l_table,
                    )
                )

                level = 0
                while True:
                    new_cur.execute(
                        BUILD_PARENT_NODES.format(
                            schema=td_task.fields.l_schema,
                            table=td_task.fields.l_table,
                        ),
                        {"node_level": level},
                    )

                    count = new_cur.fetchone()[0]
                    if count <= 1:
                        break
                    level += 1

                new_conn.commit()
                print(f"Merkle tree built successfully with {level + 1} levels")

            conn.close()
        except Exception as e:
            conn.rollback()
            raise AceException(
                f"Error building Merkle tree on {node['name']}: {str(e)}"
            )

    td_task.connection_pool.close_all()
