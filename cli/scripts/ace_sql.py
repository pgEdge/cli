# Various SQL statements for Merkle Tree operations

CREATE_METADATA_TABLE = """
    CREATE TABLE IF NOT EXISTS ace_mtree_metadata (
        schema_name text,
        table_name text,
        total_rows bigint,
        num_blocks int,
        last_updated timestamptz,
        PRIMARY KEY (schema_name, table_name)
    );
"""

CREATE_MTREE_TABLE = """
    CREATE TABLE ace_mtree_{schema}_{table} (
        node_level integer NOT NULL,
        node_position bigint NOT NULL,
        range_start {pkey_type},
        range_end {pkey_type},
        leaf_hash bytea,
        node_hash bytea,
        dirty boolean DEFAULT false,
        last_modified timestamptz DEFAULT current_timestamp,
        PRIMARY KEY (node_level, node_position)
    );
    CREATE INDEX IF NOT EXISTS ace_mtree_{schema}_{table}_range_idx
    ON ace_mtree_{schema}_{table} (range_start, range_end)
    WHERE node_level = 0;
"""

CREATE_BLOCK_ID_FUNCTION = """
    CREATE OR REPLACE FUNCTION get_block_id_{schema}_{table}({pkey_name} {pkey_type})
    RETURNS bigint AS $$
    DECLARE
        pos bigint;
        last_pos bigint;
        last_block_end {pkey_type};
    BEGIN
        -- First try to find the exact block this key belongs to
        SELECT node_position INTO pos
        FROM ace_mtree_{schema}_{table}
        WHERE node_level = 0
        AND range_start <= {pkey_name}
        AND (range_end > {pkey_name} OR range_end IS NULL)
        ORDER BY node_position
        LIMIT 1;

        -- If no block found, this key might be beyond the last block
        -- In this case, we should return the last block
        IF pos IS NULL THEN
            SELECT node_position, range_end
            INTO last_pos, last_block_end
            FROM ace_mtree_{schema}_{table}
            WHERE node_level = 0
            ORDER BY node_position DESC
            LIMIT 1;

            IF {pkey_name} >= last_block_end OR last_block_end IS NULL THEN
                RETURN last_pos;
            ELSE
                -- Otherwise return the first block
                SELECT node_position INTO pos
                FROM ace_mtree_{schema}_{table}
                WHERE node_level = 0
                ORDER BY node_position
                LIMIT 1;
                RETURN pos;
            END IF;
        END IF;

        RETURN pos;
    END;
    $$ LANGUAGE plpgsql STABLE;
"""

CREATE_SPLIT_BLOCK_FUNCTION = """
    CREATE OR REPLACE FUNCTION split_block_if_needed_{schema}_{table}(block_pos bigint)
    RETURNS void AS $$
    DECLARE
        block_size bigint;
        target_size bigint;
        split_key {pkey_type};
        old_end {pkey_type};
        new_pos bigint;
        max_pos bigint;
    BEGIN
        target_size := {block_size};

        SELECT count(*) INTO block_size
        FROM {schema}.{table} t
        JOIN ace_mtree_{schema}_{table} mt
            ON mt.node_level = 0
            AND mt.node_position = block_pos
            AND t.{pkey} >= mt.range_start
            AND (t.{pkey} < mt.range_end OR mt.range_end IS NULL);

        -- If block is more than 2x target size, split it
        IF block_size > 2 * target_size THEN
            -- Up for debate, but median should work for most cases
            WITH ordered_keys AS (
                SELECT t.{pkey},
                       row_number() OVER (ORDER BY t.{pkey}) as rn
                FROM {schema}.{table} t
                JOIN ace_mtree_{schema}_{table} mt
                    ON mt.node_level = 0
                    AND mt.node_position = block_pos
                    AND t.{pkey} >= mt.range_start
                    AND (t.{pkey} < mt.range_end OR mt.range_end IS NULL)
            )
            SELECT {pkey} INTO split_key
            FROM ordered_keys
            WHERE rn = block_size/2;

            SELECT range_end, COALESCE(
                (
                    SELECT
                        max(node_position)
                    FROM
                        ace_mtree_{schema}_{table}
                    WHERE
                        node_level = 0
                ),
                0
            ) INTO old_end, max_pos
            FROM ace_mtree_{schema}_{table}
            WHERE node_level = 0 AND node_position = block_pos;

            -- Always use the next available position
            -- TODO: Will this work for non-integer pkeys?
            new_pos := max_pos + 1;

            -- Update the existing block's end
            UPDATE ace_mtree_{schema}_{table}
            SET range_end = split_key,
                dirty = true,
                last_modified = current_timestamp
            WHERE node_level = 0 AND node_position = block_pos;

            -- Insert the new block
            INSERT INTO ace_mtree_{schema}_{table}
                (
                    node_level,
                    node_position,
                    range_start,
                    range_end,
                    dirty,
                    last_modified
                )
            VALUES
                (0, new_pos, split_key, old_end, true, current_timestamp);

            -- Ensure parent nodes exist up to the root
            -- This is needed for both the original and new block positions
            -- Until update_mtree is called, this will be a disconnected graph
            -- instead of a full tree. The full merkle tree structure will be
            -- restored only when update_mtree is called.
            -- This is okay since running the new table-diff will call
            -- update_mtree anyway.
            WITH RECURSIVE ensure_parents(level, pos) AS (
                -- Base case: start with both block positions
                SELECT 0, block_pos
                UNION
                SELECT 0, new_pos
                UNION ALL
                -- Recursive case: add parent positions
                SELECT p.level + 1, p.pos / 2
                FROM ensure_parents p
                WHERE p.pos > 0
            )
            INSERT INTO ace_mtree_{schema}_{table}
                (node_level, node_position, last_modified)
            SELECT level, pos, current_timestamp
            FROM ensure_parents
            WHERE level > 0
            ON CONFLICT (node_level, node_position) DO NOTHING;
        END IF;
    END;
    $$ LANGUAGE plpgsql;
"""

"""
The merge_block_if_needed function handles merging blocks if large sets of
records are deleted in table, thus affecting the block sizes.

1. Block Size Check:
   - Given a block position (after a delete), it first checks if the block
     is too small
   - A block is considered "too small" if it contains < target_size / 2 rows.
     target_size is basically config.MTREE_BLOCK_SIZE.
   - Example: If target_size = 1000, blocks with < 500 rows trigger merging

2. Merge Strategy:
   Consider these blocks with their ranges and positions:
   Block 0: range 1-500     (500 rows)
   Block 1: range 501-1000   (100 rows)
   Block 2: range 1001-1500  (500 rows)

   If records from 601-1000 are deleted, the block with range 501-1000 will
   end up being too small. At first glance, it might not seem like a problem
   that needs to be addressed. However, it is possible that entire ranges may
   become obsolete, thus threatening the integrity of the Merkle tree.

   The function will:
   a) First try to merge with the previous block (Block 0):
      Result: Block 0: range 1-1000, Block 1: range 1001-1500

   b) If no previous block exists, merge with the next block:
      Example with different scenario:
      Block 0: range 1-500    (100 rows after delete) <- Too small
      Block 1: range 501-1000 (500 rows)
      Result: Block 0: range 1-1000 (contains 600 rows, but it's okay)

3. Position Recomputation:
   After merging, node positions must be recomputed to maintain contiguous ordering.
   Example:
   Before merge:
   Level 0: [0, 1, 2, 3, 4]
   Level 1: [0, 1, 2]
   Level 2: [0]

   After merging blocks 3 and 4:
   Level 0: [0, 1, 2, 3]
   Level 1: [0, 1]
   Level 2: [0]

4. Things to note:
   - The function marks affected blocks as dirty to trigger rehashing
   - Parent nodes are not modified here - they are rebuilt from scratch in
     update_mtree
   - The temp_offset (1000) assumes the tree won't have more than 1000 nodes
     per level. This is temporary since it won't work for very large trees.
     I will fix it soon.
   - Position recomputation maintains the relative ordering of all nodes
"""

CREATE_MERGE_BLOCK_FUNCTION = """
CREATE OR REPLACE FUNCTION merge_block_if_needed_{schema}_{table}(block_pos bigint)
RETURNS void AS $$
DECLARE
    block_size bigint;
    target_size bigint := {block_size};
    current_start {pkey_type};
    current_end   {pkey_type};
    merge_target  bigint;
    max_pos       bigint;
    temp_offset   bigint;
BEGIN
    -- Count rows in the block from the base table.
    -- This is the real size of the block after the delete.
    SELECT count(*) INTO block_size
    FROM {schema}.{table} t
    JOIN ace_mtree_{schema}_{table} mt
      ON mt.node_level = 0
      AND mt.node_position = block_pos
      AND t.{pkey} >= mt.range_start
      AND (t.{pkey} < mt.range_end OR mt.range_end IS NULL);

    IF block_size < target_size / 2 THEN
        SELECT range_start, range_end
          INTO current_start, current_end
          FROM ace_mtree_{schema}_{table}
         WHERE node_level = 0 AND node_position = block_pos;

        -- Let's merge with the previous block if possible.
        IF EXISTS (
            SELECT 1 FROM ace_mtree_{schema}_{table}
            WHERE node_level = 0 AND node_position < block_pos
            ORDER BY node_position DESC
            LIMIT 1
        ) THEN
            SELECT node_position
              INTO merge_target
              FROM ace_mtree_{schema}_{table}
             WHERE node_level = 0 AND node_position < block_pos
             ORDER BY node_position DESC
             LIMIT 1;

            -- Extend the previous block's range to absorb the current block
            UPDATE ace_mtree_{schema}_{table}
            SET range_end = current_end,
                dirty = true,
                last_modified = current_timestamp
            WHERE node_level = 0 AND node_position = merge_target;

            -- Remove the merged block
            DELETE FROM ace_mtree_{schema}_{table}
             WHERE node_level = 0 AND node_position = block_pos;

        -- Otherwise, merge with the next block
        ELSIF EXISTS (
            SELECT 1 FROM ace_mtree_{schema}_{table}
            WHERE node_level = 0 AND node_position > block_pos
            ORDER BY node_position
            LIMIT 1
        ) THEN
            SELECT node_position
              INTO merge_target
              FROM ace_mtree_{schema}_{table}
             WHERE node_level = 0 AND node_position > block_pos
             ORDER BY node_position
             LIMIT 1;

            UPDATE ace_mtree_{schema}_{table}
            SET range_start = current_start,
                dirty = true,
                last_modified = current_timestamp
            WHERE node_level = 0 AND node_position = merge_target;

            DELETE FROM ace_mtree_{schema}_{table}
             WHERE node_level = 0 AND node_position = block_pos;
        END IF;

        -- Recalculate positions for all nodes to maintain a contiguous ordering.
        -- Phase 1: Add a large temporary offset to all positions so that no
        -- duplicates occur.
        SELECT COALESCE(max(node_position), 0)
        INTO max_pos
        FROM ace_mtree_{schema}_{table};
        -- TODO: What is the tree is extremely large and this temp_offset just
        -- doesn't cut it?
        temp_offset := max_pos + 1000;

        UPDATE ace_mtree_{schema}_{table}
        SET node_position = node_position + temp_offset,
            last_modified = current_timestamp;

        -- Phase 2: Recompute final positions using a window function.
        WITH new_positions AS (
            SELECT ctid,
                   node_level,
                   row_number()
                   OVER
                   (PARTITION BY node_level ORDER BY node_position) - 1
                   AS final_position
              FROM ace_mtree_{schema}_{table}
        )
        UPDATE ace_mtree_{schema}_{table} mt
        SET node_position = np.final_position,
            last_modified = current_timestamp
        FROM new_positions np
        WHERE mt.ctid = np.ctid;
    END IF;
END;
$$ LANGUAGE plpgsql;
"""

CREATE_TRIGGER_FUNCTION = """
    CREATE OR REPLACE FUNCTION track_dirty_blocks_{schema}_{table}()
    RETURNS trigger AS $$
    DECLARE
        affected_pos bigint;
        last_block_pos bigint;
        last_block_end {pkey_type};
    BEGIN
        IF TG_LEVEL = 'STATEMENT' THEN
            RETURN NULL;
        END IF;

        IF TG_OP = 'INSERT' THEN
            -- Get the last block's position and end value
            SELECT node_position, range_end
            INTO last_block_pos, last_block_end
            FROM ace_mtree_{schema}_{table}
            WHERE node_level = 0
            ORDER BY node_position DESC
            LIMIT 1;

            -- If this key is beyond the last block's end, set its range_end to NULL
            -- Still deciding if this should be null or set to the new value
            IF NEW.{pkey} > last_block_end AND last_block_end IS NOT NULL THEN
                UPDATE ace_mtree_{schema}_{table}
                SET range_end = NULL,
                    dirty = true,
                    last_modified = current_timestamp
                WHERE node_level = 0
                AND node_position = last_block_pos;
            END IF;

            affected_pos := get_block_id_{schema}_{table}(NEW.{pkey});
            -- Check if we need to split the block after insert
            PERFORM split_block_if_needed_{schema}_{table}(affected_pos);
        ELSIF TG_OP = 'DELETE' THEN
            affected_pos := get_block_id_{schema}_{table}(OLD.{pkey});
            PERFORM merge_block_if_needed_{schema}_{table}(affected_pos);
        ELSIF TG_OP = 'UPDATE' THEN
            IF OLD.{pkey} IS DISTINCT FROM NEW.{pkey} THEN
                UPDATE ace_mtree_{schema}_{table}
                SET dirty = true,
                    last_modified = current_timestamp
                WHERE node_level = 0
                AND node_position IN (
                    get_block_id_{schema}_{table}(OLD.{pkey}),
                    get_block_id_{schema}_{table}(NEW.{pkey})
                );
                RETURN NULL;
            END IF;
            affected_pos := get_block_id_{schema}_{table}(NEW.{pkey});
        END IF;

        UPDATE ace_mtree_{schema}_{table}
        SET dirty = true,
            last_modified = current_timestamp
        WHERE node_level = 0
        AND node_position = affected_pos;

        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
"""

CREATE_TRIGGER = """
    DROP TRIGGER IF EXISTS
    track_dirty_blocks_{schema}_{table}_trigger ON {schema}.{table};
    CREATE TRIGGER track_dirty_blocks_{schema}_{table}_trigger
    AFTER INSERT OR UPDATE OR DELETE ON {schema}.{table}
    FOR EACH ROW EXECUTE FUNCTION track_dirty_blocks_{schema}_{table}();
"""

CREATE_XOR_FUNCTION = """
    CREATE OR REPLACE FUNCTION bytea_xor(a bytea, b bytea) RETURNS bytea AS $$
    DECLARE
        result bytea;
        len int;
    BEGIN
        IF length(a) != length(b) THEN
            RAISE EXCEPTION 'bytea_xor inputs must be same length';
        END IF;

        len := length(a);
        result := a;
        FOR i IN 0..len-1 LOOP
            result := set_byte(
                result, i, get_byte(a, i) # get_byte(b, i)
            );
        END LOOP;

        RETURN result;
    END;
    $$ LANGUAGE plpgsql IMMUTABLE STRICT;

    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_operator WHERE oprname = '#'
            AND oprleft = 'bytea'::regtype AND oprright = 'bytea'::regtype
        ) THEN
            CREATE OPERATOR # (
                LEFTARG = bytea,
                RIGHTARG = bytea,
                PROCEDURE = bytea_xor
            );
        END IF;
    END $$;
"""

ESTIMATE_ROW_COUNT = """
    SELECT (
        CASE
            WHEN s.n_live_tup > 0 THEN s.n_live_tup
            WHEN c.reltuples > 0 THEN c.reltuples
            ELSE pg_relation_size(c.oid) / (8192*0.7)
        END
    )::bigint as estimate
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    LEFT JOIN pg_stat_user_tables s
        ON s.schemaname = n.nspname
        AND s.relname = c.relname
    WHERE n.nspname = %s
    AND c.relname = %s
"""

GET_PKEY_TYPE = """
    SELECT a.atttypid::regtype::text
    FROM pg_attribute a
    JOIN pg_class c ON c.oid = a.attrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = %s
    AND c.relname = %s
    AND a.attname = %s;
"""

UPDATE_METADATA = """
    INSERT INTO ace_mtree_metadata
        (schema_name, table_name, total_rows, num_blocks, last_updated)
    VALUES (%s, %s, %s, %s, current_timestamp)
    ON CONFLICT (schema_name, table_name) DO UPDATE
    SET total_rows = EXCLUDED.total_rows,
        num_blocks = EXCLUDED.num_blocks,
        last_updated = EXCLUDED.last_updated;
"""

# TODO: Use SYSTEM for larger tables and BERNOULLI for smaller tables
CALCULATE_BLOCK_RANGES = """
    WITH sampled_data AS (
        SELECT
            {key}
        FROM {schema}.{table}
        TABLESAMPLE BERNOULLI(1)
        ORDER BY {key}
    ),
    first_row AS (
        SELECT
            {key}
        FROM {schema}.{table}
        ORDER BY {key}
        LIMIT 1
    ),
    last_row AS (
        SELECT
            {key}
        FROM {schema}.{table}
        ORDER BY {key} DESC
        LIMIT 1
    ),
    sample_boundaries AS (
        SELECT
            {key},
            ntile({num_blocks}) OVER (ORDER BY {key}) as bucket
        FROM sampled_data
    ),
    block_starts AS (
        SELECT DISTINCT ON (bucket)
            {key}
        FROM sample_boundaries
        ORDER BY bucket, {key}
    ),
    all_bounds AS (
        SELECT
            (SELECT {key} FROM first_row) as {key},
            0 as seq
        UNION ALL
        SELECT
            {key},
            1 as seq
        FROM block_starts
        WHERE {key} > (SELECT {key} FROM first_row)
        UNION ALL
        SELECT
            (SELECT {key} FROM last_row) as {key},
            2 as seq
    ),
    ranges AS (
        SELECT
            {key},
            {key} as range_start,
            LEAD({key}) OVER (ORDER BY seq, {key}) as range_end,
            seq
        FROM all_bounds
    )
    INSERT INTO ace_mtree_{schema}_{table}
        (node_level, node_position, range_start, range_end, last_modified)
    SELECT
        0,
        row_number() OVER (ORDER BY seq, {key}) - 1 as node_position,
        range_start,
        range_end,
        current_timestamp
    FROM ranges
    WHERE range_end IS NOT NULL;
"""

COMPUTE_LEAF_HASHES = """
    WITH block_rows AS (
        SELECT *
        FROM {schema}.{table}
        WHERE {key} >= %(range_start)s
        AND ({key} < %(range_end)s OR %(range_end)s IS NULL)
    ),
    block_hash AS (
        SELECT
            digest(
                COALESCE(
                    string_agg(
                        concat_ws(
                            '|',
                            {columns}
                        ),
                        '|'
                        ORDER BY {key}
                    ),
                    'EMPTY_BLOCK'
                ),
                'sha256'
            ) as leaf_hash
        FROM block_rows
    )
    UPDATE ace_mtree_{schema}_{table} mt
    SET
        leaf_hash = block_hash.leaf_hash,
        node_hash = block_hash.leaf_hash,
        last_modified = current_timestamp
    FROM block_hash
    WHERE mt.node_position = %(node_position)s
    AND mt.node_level = 0
    RETURNING mt.node_position;
"""

GET_BLOCK_RANGES = """
    SELECT node_position, range_start, range_end
    FROM ace_mtree_{schema}_{table}
    WHERE node_level = 0
    ORDER BY node_position;
"""

GET_DIRTY_AND_NEW_BLOCKS = """
    SELECT node_position, range_start, range_end
    FROM ace_mtree_{schema}_{table}
    WHERE node_level = 0
    AND (dirty = true OR leaf_hash IS NULL)
    ORDER BY node_position;
"""

CLEAR_DIRTY_FLAGS = """
    UPDATE ace_mtree_{schema}_{table}
    SET dirty = false,
        last_modified = current_timestamp
    WHERE node_level = 0
    AND node_position = ANY(%(node_positions)s);
"""

BUILD_PARENT_NODES = """
    WITH pairs AS (
        SELECT
            node_level,
            node_position / 2 as parent_position,
            array_agg(node_hash ORDER BY node_position) as child_hashes
        FROM ace_mtree_{schema}_{table}
        WHERE node_level = %(node_level)s
        GROUP BY node_level, node_position / 2
    ),
    inserted AS (
        INSERT INTO ace_mtree_{schema}_{table}
            (node_level, node_position, node_hash, last_modified)
        SELECT
            %(node_level)s + 1,
            parent_position,
            CASE
                WHEN array_length(child_hashes, 1) = 1 THEN child_hashes[1]
                ELSE child_hashes[1] # child_hashes[2]
            END,
            current_timestamp
        FROM pairs
        RETURNING 1
    )
    SELECT count(*) FROM inserted;
"""

INSERT_BLOCK_RANGES = """
    INSERT INTO ace_mtree_{schema}_{table}
        (node_level, node_position, range_start, range_end, last_modified)
    VALUES
        (0, %s, %s, %s, current_timestamp);
"""

# This is the optimised version of the former get_pkey_offsets() in table_diff
# The Bernoulli sampling method is slow for larger tables and smaller sample sizes.
# However, we're using it here since regular table-diff should not be used
# for large tables anyway. Nevertheless, this should give us a significant
# performance boost over the former get_pkey_offsets() function.
GET_PKEY_OFFSETS = """
    WITH sampled_data AS (
        SELECT {key}
        FROM {schema}.{table}
        TABLESAMPLE BERNOULLI(1)
        ORDER BY ROW({key})
    ),
    first_row AS (
        SELECT {key}
        FROM {schema}.{table}
        ORDER BY ROW({key})
        LIMIT 1
    ),
    last_row AS (
        SELECT {key}
        FROM {schema}.{table}
        ORDER BY ROW({key}) DESC
        LIMIT 1
    ),
    sample_boundaries AS (
        SELECT {key},
            ntile({num_blocks}) OVER (ORDER BY ROW({key})) as bucket
        FROM sampled_data
    ),
    block_starts AS (
        SELECT DISTINCT ON (bucket)
            {key},
            ROW({key})::text as row_text
        FROM sample_boundaries
        ORDER BY bucket, ROW({key})
    ),
    all_bounds AS (
        SELECT NULL as range_start,
               (SELECT string_to_array(TRIM(BOTH '()' FROM ROW({key})::text), ',')
               FROM first_row) as range_end,
               -1 as seq
        UNION ALL
        SELECT
            (SELECT string_to_array(TRIM(BOTH '()' FROM ROW({key})::text), ',')
            FROM first_row) as range_start,
            (SELECT string_to_array(TRIM(BOTH '()' FROM ROW({key})::text), ',')
            FROM block_starts ORDER BY ROW({key}) LIMIT 1) as range_end,
            0 as seq
        UNION ALL
        SELECT
            string_to_array(TRIM(BOTH '()' FROM row_text), ',') as range_start,
            CASE
                WHEN LEAD(row_text) OVER (ORDER BY ROW({key})) IS NULL THEN
                    (SELECT string_to_array(TRIM(BOTH '()' FROM ROW({key})::text), ',')
                    FROM last_row)
                ELSE
                    string_to_array(TRIM(BOTH '()' FROM LEAD(row_text)
                    OVER (ORDER BY ROW({key}))), ',')
            END as range_end,
            1 as seq
        FROM block_starts
        UNION ALL
        SELECT
            (SELECT string_to_array(TRIM(BOTH '()' FROM ROW({key})::text), ',')
            FROM last_row) as range_start,
            NULL as range_end,
            2 as seq
    )
    SELECT range_start,
           range_end
    FROM all_bounds
    ORDER BY seq;
"""
