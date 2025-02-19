import datetime
from itertools import combinations
from multiprocessing import Manager
import traceback
import os
from typing import Tuple, Any
from dataclasses import dataclass

from mpire import WorkerPool
from mpire.utils import make_single_arguments

import ace_html_reporter
import util
import ace
import ace_db
import ace_core
import ace_config as config
from ace_data_models import MerkleTreeTask
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
    INSERT_BLOCK_RANGES,
    GET_DIRTY_AND_NEW_BLOCKS,
    CLEAR_DIRTY_FLAGS,
    GET_NODE_CHILDREN,
    GET_ROOT_NODE,
    GET_LEAF_RANGES,
)

BERNOULLI_THRESHOLD = 10_000_000


@dataclass
class BlockBoundary:
    """Represents a block boundary for parallel processing"""

    block_id: int
    block_start: Tuple[Any, ...]
    block_end: Tuple[Any, ...]


def init_hash_conn_pool(worker_id, shared_objects, worker_state):
    """Initialize connection pool for hash computation workers"""
    node = shared_objects["node"]
    conn_pool = shared_objects["conn_pool"]

    try:
        # TODO: Investigate why conn_pool.connect() fails here
        _, conn = conn_pool.get_cluster_node_connection(node)
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
    """Close connection pool for hash computation workers"""
    try:
        worker_state["conn"].commit()
        worker_state["cur"].close()
        worker_state["conn"].close()
    except Exception as e:
        raise AceException(f"Error closing worker connection: {str(e)}")


def compute_block_hashes(worker_id, shared_objects, worker_state, args):
    """Worker function to compute hashes for a range of blocks"""
    block_boundary, sql = args

    try:
        cur = worker_state["cur"]
        conn = worker_state["conn"]

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


def create_mtree_objects(conn, schema, table, key, total_rows, num_blocks):
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # We're defining an XOR operator here for building parent hashes
    # This is the optimisation Riak uses:
    # See: https://www.youtube.com/watch?v=TCiHqF_XTmE
    cur.execute(CREATE_XOR_FUNCTION)
    cur.execute(CREATE_METADATA_TABLE)

    cur.execute(
        GET_PKEY_TYPE,
        (
            schema,
            table,
            key,
        ),
    )
    pkey_type = cur.fetchone()[0]

    cur.execute(
        "DROP TABLE IF EXISTS ace_mtree_{schema}_{table}".format(
            schema=schema,
            table=table,
        )
    )

    cur.execute(
        CREATE_MTREE_TABLE.format(
            schema=schema,
            table=table,
            pkey_type=pkey_type,
        )
    )

    cur.execute(
        CREATE_BLOCK_ID_FUNCTION.format(
            schema=schema,
            table=table,
            pkey_name=key,
            pkey_type=pkey_type,
        )
    )

    cur.execute(
        UPDATE_METADATA,
        (
            schema,
            table,
            total_rows,
            num_blocks,
        ),
    )

    cur.execute(
        CREATE_TRIGGER_FUNCTION.format(
            schema=schema,
            table=table,
            pkey=key,
            pkey_type=pkey_type,
            block_size=config.MTREE_BLOCK_SIZE,
        )
    )
    cur.execute(
        CREATE_TRIGGER.format(
            schema=schema,
            table=table,
        )
    )

    conn.commit()


def get_row_estimate(conn, schema, table, analyse=False):

    cur = conn.cursor()

    if analyse:
        cur.execute("BEGIN")
        cur.execute("SET parallel_tuple_cost = 0")
        cur.execute("SET parallel_setup_cost = 0")

        print(f"Analyzing {schema}.{table} on node {conn.info.host}")
        print("This might take a while...")

        # TODO: This might take a while so need a different strategy here
        cur.execute("ANALYZE {schema}.{table}".format(schema=schema, table=table))

    cur.execute(
        ESTIMATE_ROW_COUNT,
        (schema, table),
    )
    total_rows = cur.fetchone()[0]
    num_blocks = (total_rows - 1) // config.MTREE_BLOCK_SIZE + 1

    conn.commit()
    return total_rows, num_blocks


def build_mtree(mtree_task: MerkleTreeTask) -> None:
    """
    Build a Merkle tree for a table using parallel processing.
    The tree is stored in a separate table for each source table.
    Parent nodes are computed using XOR of child hashes.

    Args:
        cluster_name (str): Name of the cluster
        table_name (str): Name of the table to build tree for
        dbname (str, optional): Database name. Defaults to None.
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

    for node in mtree_task.fields.cluster_nodes:
        _, conn = mtree_task.connection_pool.get_cluster_node_connection(node)
        try:
            total_rows, num_blocks = get_row_estimate(
                conn, schema, table, analyse=mtree_task.analyse
            )

            create_mtree_objects(
                conn,
                schema,
                table,
                key,
                total_rows,
                num_blocks,
            )

            if num_blocks > max_blocks:
                max_blocks = num_blocks
                ref_node = node
        except Exception as e:
            conn.rollback()
            raise AceException(
                f"Error creating mtree objects on {node['name']}: {str(e)}"
            )

    print(f"Using node {ref_node['name']} as the reference node")

    # Now let's compute the block ranges on the reference node
    leaf_blocks = []
    msg = (
        f"Calculating block ranges for {max_blocks:,} blocks " f"(~{total_rows:,} rows)"
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
        0.01 if total_rows > 500_000_000 else 0.1 if total_rows > 50_000_000 else 1.0
    )

    table_sample_method = "BERNOULLI" if total_rows < BERNOULLI_THRESHOLD else "SYSTEM"

    print(f"Using {table_sample_method} with sample percent {sample_percent}")

    _, conn = mtree_task.connection_pool.get_cluster_node_connection(ref_node)

    with conn.cursor() as cur:
        cur.execute(
            CALCULATE_BLOCK_RANGES.format(
                schema=schema,
                table=table,
                key=key,
                num_blocks=max_blocks,
                table_sample_method=table_sample_method,
                sample_percent=sample_percent,
            )
        )
        cur.execute(
            GET_BLOCK_RANGES.format(
                schema=schema,
                table=table,
            )
        )
        leaf_blocks = cur.fetchall()
        conn.commit()

    # We're ready to build the merkle tree
    schema_table = f"{schema}.{table}"
    print(f"\nBuilding merkle tree for {schema_table}")

    for node in mtree_task.fields.cluster_nodes:
        print(f"\nProcessing node: {node['name']}")
        _, conn = mtree_task.connection_pool.get_cluster_node_connection(node)

        try:
            with conn.cursor() as cur:
                if node != ref_node:
                    for block in leaf_blocks:
                        cur.execute(
                            INSERT_BLOCK_RANGES.format(
                                schema=schema,
                                table=table,
                            ),
                            (block[0], block[1], block[2]),
                        )
                # Committing is necessary here since the workers use their own
                # connections and cursors
                conn.commit()

            # Now compute hashes
            work_items = []
            for block in leaf_blocks:
                column_list = []
                for col in mtree_task.fields.cols.split(","):
                    column_list.append(
                        f"CASE WHEN {col} IS NULL THEN 'NULL' "
                        f"WHEN {col}::text = '' THEN 'EMPTY' "
                        f"ELSE {col}::text END"
                    )
                column_expr = ",\n        ".join(column_list)

                sql = COMPUTE_LEAF_HASHES.format(
                    schema=schema,
                    table=table,
                    key=key,
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

            print(f"Computing hashes for {len(leaf_blocks)} blocks...")
            # TODO: Use MAX_CPU_RATIO here
            max_workers = int(os.cpu_count())
            n_jobs = min(len(work_items), max_workers)

            shared_objects = {
                "node": node,
                "conn_pool": mtree_task.connection_pool,
            }

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
                    )
                )

                failed = [r for r in results if not r]
                if failed:
                    raise AceException(
                        f"Failed to compute hashes for {len(failed)} blocks"
                    )

            print("\nBuilding parent nodes...")

            # Let's just use a new conn here to be safe
            _, new_conn = mtree_task.connection_pool.get_cluster_node_connection(node)
            parent_cur = new_conn.cursor()

            parent_cur.execute(
                """
                DELETE FROM ace_mtree_{schema}_{table}
                WHERE node_level > 0
                """.format(
                    schema=schema,
                    table=table,
                )
            )

            level = 0
            while True:
                parent_cur.execute(
                    BUILD_PARENT_NODES.format(
                        schema=schema,
                        table=table,
                    ),
                    {"node_level": level},
                )

                count = parent_cur.fetchone()[0]
                if count <= 1:
                    break
                level += 1

            new_conn.commit()
            print(f"Merkle tree built successfully with {level + 1} levels")

            conn.close()
        except Exception as e:
            conn.rollback()
            new_conn.rollback()
            raise AceException(
                f"Error building Merkle tree on {node['name']}: {str(e)}"
            )

    mtree_task.connection_pool.close_all()


def split_blocks(conn, schema, table, key, blocks):
    """
    Split blocks if they are too large.
    Returns a list of block positions that were modified.
    """
    try:
        cur = conn.cursor()
        modified_positions = set()
        target_size = config.MTREE_BLOCK_SIZE

        # First delete all parent nodes since we'll be modifying the tree structure
        # This is not expensive at all since computing parent hashes is significantly
        # cheaper than computing leaf hashes.
        cur.execute(
            f"""
            DELETE FROM ace_mtree_{schema}_{table}
            WHERE node_level > 0
            """
        )

        cur.execute(
            GET_PKEY_TYPE,
            (
                schema,
                table,
                key,
            ),
        )
        pkey_type = cur.fetchone()[0]

        blocks = sorted(blocks, key=lambda x: x[0])
        i = 0

        print(blocks)
    except Exception as e:
        conn.rollback()
        raise AceException(f"Error splitting blocks on {schema}.{table}: {str(e)}")

    while i < len(blocks):
        pos, start, end = blocks[i]
        print(f"Processing block {pos} with range {start} to {end}")

        # When inserts happen after the range_end of the last block, we mark that
        # block as dirty and set the range_end to null. So, if we're attempting
        # to add new blocks at the end, we need to find the actual max value.
        if i == len(blocks) - 1 and end is None:
            cur.execute(
                f"""
                SELECT max({key})
                FROM {schema}.{table}
                WHERE {key} >= %s
                """,
                (start,),
            )
            max_val = cur.fetchone()[0]
            if max_val is not None:
                end = max_val
                cur.execute(
                    f"""
                    UPDATE ace_mtree_{schema}_{table}
                    SET range_end = %s
                    WHERE node_level = 0
                    AND node_position = %s
                    """,
                    (end, pos),
                )

        # Get actual row count for this block
        cur.execute(
            f"""
            SELECT count(*)
            FROM {schema}.{table}
            WHERE {key} >= %s
            AND ({key} < %s OR %s::{pkey_type} IS NULL)
        """,
            (start, end, end),
        )
        count = cur.fetchone()[0]

        if count > target_size * 2:
            # The split point is simply the midpoint of the block
            cur.execute(
                f"""
                SELECT {key}
                FROM {schema}.{table}
                WHERE {key} >= %s
                AND ({key} < %s OR %s::{pkey_type} IS NULL)
                ORDER BY {key}
                OFFSET %s
                LIMIT 1
            """,
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
                f"""
                SELECT MAX(node_position) + 1
                FROM ace_mtree_{schema}_{table}
                WHERE node_level = 0
                """
            )
            new_pos = cur.fetchone()[0]

            # Create new block at the end
            cur.execute(
                INSERT_BLOCK_RANGES.format(
                    schema=schema,
                    table=table,
                ),
                (new_pos, split_point, end),
            )

            # Update original block
            cur.execute(
                f"""
                UPDATE ace_mtree_{schema}_{table}
                SET range_end = %s,
                    dirty = true,
                    last_modified = current_timestamp
                WHERE node_level = 0
                AND node_position = %s
            """,
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
    return list(modified_positions)


def merge_blocks(conn, schema, table, key, blocks):
    """
    Merge blocks if they are too small.
    Returns a list of block positions that were modified.
    """
    cur = conn.cursor()
    modified_positions = set()
    target_size = config.MTREE_BLOCK_SIZE

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
        f"""
        DELETE FROM ace_mtree_{schema}_{table}
        WHERE node_level > 0
        """
    )

    cur.execute(
        GET_PKEY_TYPE,
        (
            schema,
            table,
            key,
        ),
    )
    pkey_type = cur.fetchone()[0]

    blocks = sorted(blocks, key=lambda x: x[0])
    i = 0

    print(blocks)

    while i < len(blocks):
        pos, start, end = blocks[i]
        print(f"Processing block {pos} with range {start} to {end}")

        # When inserts happen after the range_end of the last block, we mark that
        # block as dirty and set the range_end to null. So, if we're attempting
        # to add new blocks at the end, we need to find the actual max value.
        if i == len(blocks) - 1 and end is None:
            cur.execute(
                f"""
                SELECT max({key})
                FROM {schema}.{table}
                WHERE {key} >= %s
                """,
                (start,),
            )
            max_val = cur.fetchone()[0]
            if max_val is not None:
                end = max_val
                cur.execute(
                    f"""
                    UPDATE ace_mtree_{schema}_{table}
                    SET range_end = %s
                    WHERE node_level = 0
                    AND node_position = %s
                    """,
                    (end, pos),
                )

        # Get actual row count for this block
        cur.execute(
            f"""
            SELECT count(*)
            FROM {schema}.{table}
            WHERE {key} >= %s
            AND ({key} < %s OR %s::{pkey_type} IS NULL)
        """,
            (start, end, end),
        )
        count = cur.fetchone()[0]

        # If block is nearly empty, try to merge with either neighbor
        if count < target_size * MERGE_THRESHOLD:
            # First check if we can merge with previous block
            if pos > 0:
                cur.execute(
                    f"""
                    SELECT node_position, range_start, range_end, count(*)
                    FROM ace_mtree_{schema}_{table} mt
                    LEFT JOIN {schema}.{table} t
                    ON t.{key} >= mt.range_start
                    AND (t.{key} < mt.range_end OR mt.range_end IS NULL)
                    WHERE mt.node_level = 0
                    AND mt.node_position = %s
                    GROUP BY mt.node_position, mt.range_start, mt.range_end
                    """,
                    (pos - 1,),
                )
                prev_block = cur.fetchone()
                if prev_block:
                    prev_pos, prev_start, prev_end, prev_count = prev_block
                    if (count + prev_count) <= target_size * 2:
                        # Move blocks to temp positions
                        cur.execute(
                            f"""
                            UPDATE ace_mtree_{schema}_{table}
                            SET node_position = node_position + %s
                            WHERE node_level = 0
                            AND node_position > %s
                            """,
                            (TEMP_OFFSET, prev_pos),
                        )

                        # Merge with previous block - keep full range
                        cur.execute(
                            f"""
                            UPDATE ace_mtree_{schema}_{table}
                            SET range_end = %s,
                                dirty = true,
                                last_modified = current_timestamp
                            WHERE node_level = 0
                            AND node_position = %s
                            """,
                            (end, prev_pos),
                        )

                        # Delete current block at its temporary position
                        cur.execute(
                            f"""
                            DELETE FROM ace_mtree_{schema}_{table}
                            WHERE node_level = 0
                            AND node_position = %s
                            """,
                            (pos + TEMP_OFFSET,),
                        )

                        # Move remaining blocks back in sequential order
                        cur.execute(
                            f"""
                            UPDATE ace_mtree_{schema}_{table}
                            SET node_position = pos_seq
                            FROM (
                                SELECT node_position,
                                       row_number() OVER (
                                           ORDER BY node_position
                                       ) + %s as pos_seq
                                FROM ace_mtree_{schema}_{table}
                                WHERE node_level = 0
                                AND node_position > %s
                            ) as seq
                            WHERE
                            ace_mtree_{schema}_{table}.node_position = seq.node_position
                            AND node_level = 0
                            """,
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
                        i -= 1
                        continue

            # If we couldn't merge with the previous block, try the next block
            cur.execute(
                f"""
                SELECT node_position, range_start, range_end, count(*)
                FROM ace_mtree_{schema}_{table} mt
                LEFT JOIN {schema}.{table} t
                ON t.{key} >= mt.range_start
                AND (t.{key} < mt.range_end OR mt.range_end IS NULL)
                WHERE mt.node_level = 0
                AND mt.node_position = %s
                GROUP BY mt.node_position, mt.range_start, mt.range_end
                """,
                (pos + 1,),
            )
            next_block = cur.fetchone()
            if next_block:
                next_pos, next_start, next_end, next_count = next_block
                if (count + next_count) <= target_size * 2:
                    # Move blocks to temp positions
                    cur.execute(
                        f"""
                        UPDATE ace_mtree_{schema}_{table}
                        SET node_position = node_position + %s
                        WHERE node_level = 0
                        AND node_position > %s
                        """,
                        (TEMP_OFFSET, pos),
                    )

                    # Merge with next block - keep full range
                    cur.execute(
                        f"""
                        UPDATE ace_mtree_{schema}_{table}
                        SET range_end = %s,
                            dirty = true,
                            last_modified = current_timestamp
                        WHERE node_level = 0
                        AND node_position = %s
                        """,
                        (next_end, pos),
                    )

                    # Delete next block at its temporary position
                    cur.execute(
                        f"""
                        DELETE FROM ace_mtree_{schema}_{table}
                        WHERE node_level = 0
                        AND node_position = %s
                        """,
                        (next_pos + TEMP_OFFSET,),
                    )

                    # Move remaining blocks back in sequential order
                    cur.execute(
                        f"""
                        UPDATE ace_mtree_{schema}_{table}
                        SET node_position = pos_seq
                        FROM (
                            SELECT node_position,
                                   row_number() OVER (
                                       ORDER BY node_position
                                   ) + %s as pos_seq
                            FROM ace_mtree_{schema}_{table}
                            WHERE node_level = 0
                            AND node_position > %s
                        ) as seq
                        WHERE
                        ace_mtree_{schema}_{table}.node_position = seq.node_position
                        AND node_level = 0
                        """,
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

                    # We've already processed the next block since we couldn't
                    # find a previous block to merge with
                    i += 1
                    continue

    conn.commit()
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

    for node in mtree_task.fields.cluster_nodes:
        print(f"\nUpdating Merkle tree on node: {node['name']}")
        _, conn = mtree_task.connection_pool.get_cluster_node_connection(node)

        try:
            # Start transaction with repeatable read isolation
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")

                # Get all dirty and new blocks that need updating
                cur.execute(
                    GET_DIRTY_AND_NEW_BLOCKS.format(
                        schema=schema,
                        table=table,
                    )
                )
                blocks_to_update = cur.fetchall()

                if not blocks_to_update:
                    print(f"No updates needed for {node['name']}")
                    conn.commit()
                    continue

                print(f"Found {len(blocks_to_update)} blocks to update")

                split_blocks(
                    conn,
                    schema,
                    table,
                    key,
                    blocks_to_update,
                )

                if mtree_task.rebalance:
                    merge_blocks(
                        conn,
                        schema,
                        table,
                        key,
                        blocks_to_update,
                    )

                # Get final list of blocks to update (including newly modified ones)
                cur.execute(
                    GET_DIRTY_AND_NEW_BLOCKS.format(
                        schema=schema,
                        table=table,
                    )
                )
                blocks_to_update = cur.fetchall()

                if not blocks_to_update:
                    print(f"No updates needed for {node['name']}")
                    conn.commit()
                    continue

                print(f"Found {len(blocks_to_update)} blocks to update")

                column_list = []
                for col in mtree_task.fields.cols.split(","):
                    column_list.append(
                        f"CASE WHEN {col} IS NULL THEN 'NULL' "
                        f"WHEN {col}::text = '' THEN 'EMPTY' "
                        f"ELSE {col}::text END"
                    )
                column_expr = ",\n        ".join(column_list)

                affected_positions = []
                for block in blocks_to_update:
                    params = {
                        "node_position": block[0],
                        "range_start": block[1],
                        "range_end": block[2],
                    }

                    cur.execute(
                        COMPUTE_LEAF_HASHES.format(
                            schema=schema,
                            table=table,
                            key=key,
                            columns=column_expr,
                        ),
                        params,
                    )
                    result = cur.fetchone()
                    if result:
                        affected_positions.append(result[0])

                if affected_positions:
                    cur.execute(
                        """
                        DELETE FROM ace_mtree_{schema}_{table}
                        WHERE node_level > 0
                        """.format(
                            schema=schema,
                            table=table,
                        )
                    )

                    level = 0

                    while True:
                        cur.execute(
                            BUILD_PARENT_NODES.format(
                                schema=schema,
                                table=table,
                            ),
                            {"node_level": level},
                        )

                        count = cur.fetchone()[0]
                        if count <= 1:
                            break
                        level += 1

                    cur.execute(
                        CLEAR_DIRTY_FLAGS.format(
                            schema=schema,
                            table=table,
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


def find_mismatched_leaves(conn1, conn2, schema, table, parent_level, parent_position):
    """
    Recursively traverse the merkle tree to find mismatched leaf nodes.
    Returns a list of leaf node positions that have different hashes.
    """
    mismatched_leaves = []

    print(f"Current level: {parent_level}, position: {parent_position}")

    # Get children of this parent node from both nodes
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()

    params = {"parent_level": parent_level, "parent_position": parent_position}

    cur1.execute(GET_NODE_CHILDREN.format(schema=schema, table=table), params)
    node1_children = cur1.fetchall()

    cur2.execute(GET_NODE_CHILDREN.format(schema=schema, table=table), params)
    node2_children = cur2.fetchall()

    # This shouldn't happen at all. Failsafe anyway.
    if not node1_children or not node2_children:
        return mismatched_leaves

    # Compare each child
    for child1, child2 in zip(node1_children, node2_children):
        level1, pos1, hash1 = child1
        level2, pos2, hash2 = child2
        print(f"child 1: {level1}, {pos1}, {hash1}")
        print(f"child 2: {level2}, {pos2}, {hash2}")

        if hash1 != hash2:
            if level1 == 0:
                mismatched_leaves.append(pos1)
            else:
                # Recurse down this branch to find mismatched leaves
                child_mismatches = find_mismatched_leaves(
                    conn1, conn2, schema, table, level1, pos1
                )
                mismatched_leaves.extend(child_mismatches)

    return mismatched_leaves


def get_pkey_batches(conn, schema, table, key, mismatched_positions):
    """
    Get range_start and range_end values for mismatched leaf nodes
    and format them into batches for parallel processing.
    """
    cur = conn.cursor()

    cur.execute(
        GET_LEAF_RANGES.format(schema=schema, table=table),
        {"node_positions": mismatched_positions},
    )
    leaf_ranges = cur.fetchall()

    batches = []
    for _, range_start, range_end in leaf_ranges:
        batch = (range_start, range_end)
        batches.append(batch)

    return batches


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
    errors = False
    mismatch = False
    total_diffs = 0
    diffs_exceeded = False
    error_list = []

    start_time = datetime.now()

    node_pairs = list(combinations(mtree_task.fields.cluster_nodes, 2))

    for node1, node2 in node_pairs:
        print(f"\nComparing merkle trees between {node1['name']} and {node2['name']}")

        _, conn1 = mtree_task.connection_pool.get_cluster_node_connection(node1)
        _, conn2 = mtree_task.connection_pool.get_cluster_node_connection(node2)

        try:
            cur1 = conn1.cursor()
            cur2 = conn2.cursor()

            cur1.execute(GET_ROOT_NODE.format(schema=schema, table=table))
            root1 = cur1.fetchone()

            cur2.execute(GET_ROOT_NODE.format(schema=schema, table=table))
            root2 = cur2.fetchone()

            if not root1 or not root2:
                print(f"No merkle tree found for {schema}.{table}")
                continue

            root1_pos, root1_hash = root1
            root2_pos, root2_hash = root2

            # Get the root level
            cur1.execute(
                """
                SELECT MAX(node_level)
                FROM ace_mtree_{schema}_{table}
                """.format(
                    schema=schema, table=table
                )
            )
            root_level = cur1.fetchone()[0]

            # If root hashes match, trees are identical
            if root1_hash == root2_hash:
                print("Merkle trees are identical")
                continue

            # If not, we need to traverse down the tree
            mismatched_leaves = find_mismatched_leaves(
                conn1,
                conn2,
                schema,
                table,
                parent_level=root_level,
                parent_position=root1_pos,
            )

            if not mismatched_leaves:
                print("No mismatched leaf nodes found")
                continue

            batches = get_pkey_batches(conn1, schema, table, key, mismatched_leaves)
            print(f"Found {len(batches)} mismatched blocks")

            max_workers = int(os.cpu_count() * mtree_task.max_cpu_ratio)
            n_jobs = min(len(batches), max_workers)
            stop_event = Manager().Event()

            shared_objects = {
                "p_key": key,
                "schema_name": schema,
                "table_name": table,
                "node_list": mtree_task.fields.cluster_nodes,
                "cols_list": mtree_task.fields.cols,
                "simple_primary_key": simple_primary_key,
                # We need to use the rerun mode here since we're passing in
                # sets of pkeys to compare instead of ranges.
                "mode": "rerun",
                "stop_event": stop_event,
                "task": mtree_task,
            }

            with WorkerPool(
                n_jobs=n_jobs,
                shared_objects=shared_objects,
                use_worker_state=True,
            ) as pool:
                for result in pool.imap_unordered(
                    ace_core.compare_checksums,
                    make_single_arguments(batches),
                    iterable_len=len(batches),
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
                            for node, diffs in node_diffs.items():
                                if node not in diff_dict[node_pair]:
                                    diff_dict[node_pair][node] = []
                                diff_dict[node_pair][node].extend(diffs)

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

        except Exception as e:
            conn1.rollback()
            conn2.rollback()
            raise AceException(f"Error comparing merkle trees: {str(e)}")

        finally:
            conn1.close()
            conn2.close()

    run_time = util.round_timedelta(datetime.now() - start_time).total_seconds()
    run_time_str = f"{run_time:.2f}"

    mtree_task.scheduler.task_status = "COMPLETED"
    mtree_task.scheduler.finished_at = datetime.now()
    mtree_task.scheduler.time_taken = run_time
    mtree_task.scheduler.task_context = {
        "total_rows": "TBD",
        "mismatch": mismatch,
        "diffs_summary": mtree_task.diff_summary if mismatch else {},
        "errors": [],
    }

    if errors:
        context = {"total_rows": "TBD", "mismatch": mismatch, "errors": error_list}
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
                "total_rows": "TBD",
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
        f"TOTAL ROWS CHECKED = TBD\nRUN TIME = {run_time_str} seconds",
        p_state="info",
        quiet_mode=mtree_task.quiet_mode,
    )

    mtree_task.scheduler.task_status = "COMPLETED"
    mtree_task.scheduler.finished_at = datetime.now()
    mtree_task.scheduler.time_taken = run_time
    mtree_task.scheduler.task_context = {
        "total_rows": "TBD",
        "mismatch": mismatch,
        "diffs_summary": mtree_task.diff_summary if mismatch else {},
        "errors": [],
    }

    if not mtree_task.skip_db_update:
        ace_db.update_ace_task(mtree_task)

    mtree_task.connection_pool.close_all()
