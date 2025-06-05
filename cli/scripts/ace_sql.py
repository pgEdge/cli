# Various SQL statements for Merkle Tree operations

CREATE_METADATA_TABLE = """
    CREATE TABLE ace_mtree_metadata (
        schema_name text,
        table_name text,
        total_rows bigint,
        block_size int,
        num_blocks int,
        is_composite boolean NOT NULL DEFAULT false,
        last_updated timestamptz,
        PRIMARY KEY (schema_name, table_name)
    )
"""

# Instead of having one create table and trying to handle cases, I'm just using
# two variations here for simplicity.
CREATE_SIMPLE_MTREE_TABLE = """
    CREATE TABLE {mtree_table} (
        node_level integer NOT NULL,
        node_position bigint NOT NULL,
        range_start {pkey_type},
        range_end {pkey_type},
        leaf_hash bytea,
        node_hash bytea,
        dirty boolean DEFAULT false,
        inserts_since_tree_update bigint DEFAULT 0,
        deletes_since_tree_update bigint DEFAULT 0,
        last_modified timestamptz DEFAULT current_timestamp,
        PRIMARY KEY (node_level, node_position)
    );

    CREATE INDEX IF NOT EXISTS {range_idx}
    ON {mtree_table} (range_start, range_end)
    WHERE node_level = 0;
"""

CREATE_COMPOSITE_MTREE_TABLE = """
    DROP TYPE IF EXISTS {schema}_{table}_key_type CASCADE;

    CREATE TYPE {schema}_{table}_key_type AS (
        {key_type_columns}
    );

    CREATE TABLE {mtree_table} (
        node_level integer NOT NULL,
        node_position bigint NOT NULL,
        range_start {schema}_{table}_key_type,
        range_end {schema}_{table}_key_type,
        leaf_hash bytea,
        node_hash bytea,
        dirty boolean DEFAULT false,
        inserts_since_tree_update bigint DEFAULT 0,
        deletes_since_tree_update bigint DEFAULT 0,
        last_modified timestamptz DEFAULT current_timestamp,
        PRIMARY KEY (node_level, node_position)
    );

    CREATE INDEX IF NOT EXISTS {range_idx}_tuple
    ON {mtree_table} (range_start, range_end)
    WHERE node_level = 0;
"""

CREATE_GENERIC_TRIGGER = """
    DROP TRIGGER IF EXISTS {trigger}_insert_stmt ON {schema}.{table};
    DROP TRIGGER IF EXISTS {trigger}_update_stmt ON {schema}.{table};
    DROP TRIGGER IF EXISTS {trigger}_delete_stmt ON {schema}.{table};

    CREATE TRIGGER {trigger}_insert_stmt
    AFTER INSERT ON {schema}.{table}
    REFERENCING NEW TABLE AS new_table
    FOR EACH STATEMENT EXECUTE FUNCTION bulk_block_tracking_dispatcher({key});

    CREATE TRIGGER {trigger}_update_stmt
    AFTER UPDATE ON {schema}.{table}
    REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table
    FOR EACH STATEMENT EXECUTE FUNCTION bulk_block_tracking_dispatcher({key});

    CREATE TRIGGER {trigger}_delete_stmt
    AFTER DELETE ON {schema}.{table}
    REFERENCING OLD TABLE AS old_table
    FOR EACH STATEMENT EXECUTE FUNCTION bulk_block_tracking_dispatcher({key});
"""

# SQL for inserting block ranges for composite keys
INSERT_COMPOSITE_BLOCK_RANGES = """
    INSERT INTO {mtree_table}
        (node_level, node_position, range_start, range_end)
    VALUES
        (0, %s, ROW({start_tuple_values}), ROW({end_tuple_values}));
"""

ENABLE_ALWAYS = """
    ALTER TABLE {schema}.{table}
    ENABLE ALWAYS TRIGGER {insert_trigger};
    ALTER TABLE {schema}.{table}
    ENABLE ALWAYS TRIGGER {update_trigger};
    ALTER TABLE {schema}.{table}
    ENABLE ALWAYS TRIGGER {delete_trigger};
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
    WHERE n.nspname = {schema}
    AND c.relname = {table}
"""

GET_PKEY_TYPE = """
    SELECT a.atttypid::regtype::text
    FROM pg_attribute a
    JOIN pg_class c ON c.oid = a.attrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = {schema}
    AND c.relname = {table}
    AND a.attname = {key}
"""

UPDATE_METADATA = """
    INSERT INTO ace_mtree_metadata
    (
        schema_name,
        table_name,
        total_rows,
        block_size,
        num_blocks,
        is_composite,
        last_updated
    )
    VALUES (%s, %s, %s, %s, %s, %s, current_timestamp)
    ON CONFLICT (schema_name, table_name) DO UPDATE
    SET total_rows = EXCLUDED.total_rows,
        block_size = EXCLUDED.block_size,
        num_blocks = EXCLUDED.num_blocks,
        is_composite = EXCLUDED.is_composite,
        last_updated = EXCLUDED.last_updated;
"""

GET_PKEY_OFFSETS = """
    WITH sampled_data AS (
        SELECT
            {key_columns_select}
        FROM {schema}.{table}
        TABLESAMPLE {table_sample_method}({sample_percent})
        ORDER BY {key_columns_order}
    ),
    first_row AS (
        SELECT
            {key_columns_select}
        FROM {schema}.{table}
        ORDER BY {key_columns_order}
        LIMIT 1
    ),
    last_row AS (
        SELECT
            {key_columns_select}
        FROM {schema}.{table}
        ORDER BY {key_columns_order_desc}
        LIMIT 1
    ),
    sample_boundaries AS (
        SELECT
            {key_columns_select},
            ntile({ntile_count}) OVER (ORDER BY {key_columns_order}) as bucket
        FROM sampled_data
    ),
    block_starts AS (
        SELECT DISTINCT ON (bucket)
            {key_columns_select}
        FROM sample_boundaries
        ORDER BY bucket, {key_columns_order}
    ),
    all_bounds AS (
        SELECT
            {first_row_selects},
            0 as seq
        UNION ALL
        SELECT
            {key_columns_select},
            1 as seq
        FROM block_starts
        WHERE ({key_columns_select}) > (
            {first_row_tuple_selects}
        )
        UNION ALL
        SELECT
            {last_row_selects},
            2 as seq
    ),
    ranges AS (
        SELECT
            {key_columns_select},
            {range_start_columns},
            {range_end_columns},
            seq
        FROM all_bounds
    )
    SELECT {range_output_columns}
    FROM ranges
    ORDER BY seq;
"""

INSERT_BLOCK_RANGES = """
    INSERT INTO {mtree_table}
        (node_level, node_position, range_start, range_end, last_modified)
    VALUES
        (0, %s, %s, %s, current_timestamp);
"""

COMPUTE_LEAF_HASHES = """
    WITH block_rows AS (
        SELECT *
        FROM {schema}.{table}
        WHERE {where_clause}
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
    SELECT leaf_hash
    FROM block_hash;
"""

UPDATE_LEAF_HASHES = """
    UPDATE {mtree_table} mt
    SET
        leaf_hash = %(leaf_hash)s,
        node_hash = %(leaf_hash)s,
        last_modified = current_timestamp
    WHERE node_position = %(node_position)s
    AND mt.node_level = 0
    RETURNING mt.node_position;
"""

# COMPUTE_LEAF_HASHES = """
#     WITH block_rows AS (
#             SELECT *
#             FROM {schema}.{table}
#             WHERE {key} >= %(range_start)s
#             AND ({key} < %(range_end)s OR %(range_end)s IS NULL)
#         ),
#     row_hashes AS (
#         SELECT
#             CAST(
#                 CAST(
#                     'x' || MD5(
#                         {concat_columns}
#                     ) AS BIT(64)
#                 ) AS BIGINT
#             ) AS row_hash
#         FROM block_rows
#         )
#     SELECT
#         COALESCE(
#             CAST(
#                 BIT_XOR(row_hash) AS VARCHAR
#             ),
#             'EMPTY_BLOCK'
#         ) AS leaf_hash
#     FROM row_hashes;
# """
# NUMERIC_TO_BYTEA = """
# CREATE OR REPLACE FUNCTION numeric_to_bytea(n numeric, byte_length int)
# RETURNS bytea AS $$
# DECLARE
#   result bytea := '';
#   i int;
#   r int;
# BEGIN
#   -- Loop for each byte we want in the result.
#   FOR i IN 1..byte_length LOOP
#     r := mod(n, 256)::int;
#     -- Convert the remainder (one byte) to a 2-digit hex string,
#     -- decode it to a bytea, and prepend it.
#     result := decode(lpad(to_hex(r), 2, '0'), 'hex') || result;
#     n := trunc(n / 256);
#   END LOOP;
#   RETURN result;
# END;
# $$ LANGUAGE plpgsql IMMUTABLE;
# """

# COMPUTE_LEAF_HASHES = """
#     with block_hash as (
#         SELECT numeric_to_bytea(sum(hash_record_extended(t, 0)), 32) as hash
#         FROM {schema}.{table} t
#         WHERE t.{key} >= %(range_start)s
#         AND (t.{key} < %(range_end)s OR %(range_end)s IS NULL)
#     )
#     UPDATE ace_mtree_{schema}_{table}
#     SET leaf_hash = block_hash.hash,
#         node_hash = block_hash.hash,
#         last_modified = current_timestamp
#     FROM block_hash
#     WHERE node_position = %(node_position)s AND node_level = 0
#     RETURNING node_position;
# """

GET_BLOCK_RANGES = """
    SELECT node_position, range_start, range_end
    FROM {mtree_table}
    WHERE node_level = 0
    ORDER BY node_position;
"""

GET_DIRTY_AND_NEW_BLOCKS = """
    SELECT node_position, range_start, range_end
    FROM {mtree_table}
    WHERE node_level = 0
    AND (dirty = true OR leaf_hash IS NULL)
    ORDER BY node_position;
"""

CLEAR_DIRTY_FLAGS = """
    UPDATE {mtree_table}
    SET dirty = false,
        inserts_since_tree_update = 0,
        deletes_since_tree_update = 0,
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
        FROM {mtree_table}
        WHERE node_level = %(node_level)s
        GROUP BY node_level, node_position / 2
    ),
    inserted AS (
        INSERT INTO {mtree_table}
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


GET_ROOT_NODE = """
    SELECT node_position, node_hash
    FROM {mtree_table}
    WHERE node_level = (
        SELECT MAX(node_level)
        FROM {mtree_table}
    )
"""

GET_NODE_CHILDREN = """
    SELECT node_level, node_position, node_hash
    FROM {mtree_table}
    WHERE node_level = %(parent_level)s - 1
    AND node_position / 2 = %(parent_position)s
    ORDER BY node_position
"""

GET_LEAF_RANGES = """
    SELECT range_start, range_end
    FROM {mtree_table}
    WHERE node_level = 0
    AND node_position = ANY(%(node_positions)s)
    ORDER BY node_position
"""

GET_ROW_COUNT_ESTIMATE = """
    SELECT total_rows
    FROM ace_mtree_metadata
    WHERE schema_name = {schema}
    AND table_name = {table}
"""

GET_MAX_VAL_COMPOSITE = """
    SELECT {pkey_cols}
    FROM {schema}.{table}
    WHERE ({pkey_cols}) >= ({pkey_values})
    ORDER BY ({pkey_cols}) DESC
    LIMIT 1
"""

UPDATE_MAX_VAL = """
    UPDATE {mtree_table}
    SET range_end = %s
    WHERE node_level = 0
    AND node_position = %s
"""

GET_MAX_VAL_SIMPLE = """
    SELECT max({key})
    FROM {schema}.{table}
    WHERE {key} >= %s
"""

GET_COUNT_COMPOSITE = """
    SELECT count(*)
    FROM {schema}.{table}
    WHERE {where_clause}
"""

GET_COUNT_SIMPLE = """
    SELECT count(*)
    FROM {schema}.{table}
    WHERE {key} >= %s
    AND ({key} < %s OR %s::{pkey_type} IS NULL)
"""

GET_SPLIT_POINT_COMPOSITE = """
    SELECT ROW({pkey_cols})
    FROM {schema}.{table}
    WHERE {where_clause}
    ORDER BY {order_cols}
    OFFSET %s
    LIMIT 1
"""

GET_SPLIT_POINT_SIMPLE = """
    SELECT {key}
    FROM {schema}.{table}
    WHERE {key} >= %s
    AND ({key} < %s OR %s::{pkey_type} IS NULL)
    ORDER BY {key}
    OFFSET %s
    LIMIT 1
"""

DELETE_PARENT_NODES = """
    DELETE FROM {mtree_table}
    WHERE node_level > 0
"""

GET_MAX_NODE_POSITION = """
    SELECT MAX(node_position) + 1
    FROM {mtree_table}
    WHERE node_level = 0
"""

UPDATE_BLOCK_RANGE_END = """
    UPDATE {mtree_table}
    SET range_end = %s,
        dirty = true,
        last_modified = current_timestamp
    WHERE node_level = 0
    AND node_position = %s
"""

UPDATE_NODE_POSITIONS_TEMP = """
    UPDATE {mtree_table}
    SET node_position = node_position + %s
    WHERE node_level = 0
    AND node_position > %s
"""

DELETE_BLOCK = """
    DELETE FROM {mtree_table}
    WHERE node_level = 0
    AND node_position = %s
"""

UPDATE_NODE_POSITIONS_SEQUENTIAL = """
    UPDATE {mtree_table}
    SET node_position = pos_seq
    FROM (
        SELECT node_position,
               row_number() OVER (
               ORDER BY node_position
           ) + %s as pos_seq
        FROM {mtree_table}
        WHERE node_level = 0
        AND node_position > %s
    ) as seq
    WHERE
    {mtree_table}.node_position = seq.node_position
    AND node_level = 0
"""

FIND_BLOCKS_TO_SPLIT = """
    SELECT node_position, range_start, range_end
    FROM {mtree_table}
    WHERE node_level = 0
    AND inserts_since_tree_update >= %s
    AND node_position = ANY(%s)
"""

FIND_BLOCKS_TO_MERGE_COMPOSITE = """
    WITH range_sizes AS (
        SELECT
            mt.node_position,
            mt.range_start,
            mt.range_end,
            mt.deletes_since_tree_update,
            COUNT(*) AS current_size
        FROM {mtree_table} mt
        LEFT JOIN {schema}.{table} t
        ON ROW({key_columns}) >= mt.range_start
        AND (ROW({key_columns}) < mt.range_end
            OR mt.range_end IS NULL)
        WHERE mt.node_level = 0
        AND mt.node_position = ANY(%s)
        GROUP BY
            mt.node_position,
            mt.range_start,
            mt.range_end,
            mt.deletes_since_tree_update
    )
    SELECT
        node_position,
        range_start,
        range_end
    FROM range_sizes
    WHERE
        deletes_since_tree_update >=
        current_size * {merge_threshold}
"""

FIND_BLOCKS_TO_MERGE_SIMPLE = """
    WITH range_sizes AS (
        SELECT
            mt.node_position,
            mt.range_start,
            mt.range_end,
            mt.deletes_since_tree_update,
            COUNT(*) AS current_size
        FROM {mtree_table} mt
        LEFT JOIN {schema}.{table} t
        ON t.{key} >= mt.range_start
        AND (t.{key} < mt.range_end
            OR mt.range_end IS NULL)
        WHERE mt.node_level = 0
        AND mt.node_position = ANY(%s)
        GROUP BY
            mt.node_position,
            mt.range_start,
            mt.range_end,
            mt.deletes_since_tree_update
    )
    SELECT
        node_position,
        range_start,
        range_end
    FROM range_sizes
    WHERE
        deletes_since_tree_update >=
        current_size * {merge_threshold}
"""

GET_BLOCK_COUNT_COMPOSITE = """
    WITH block_data AS
    (
        SELECT node_position, range_start, range_end
        FROM {mtree_table}
        WHERE node_level = 0
        AND node_position = %s
    )
    SELECT
        b.node_position,
        b.range_start,
        b.range_end,
        COUNT(t.*) AS cnt
    FROM block_data b
    LEFT JOIN {schema}.{table} t
    ON ROW({pkey_cols}) >= b.range_start
    AND (ROW({pkey_cols}) <= b.range_end OR b.range_end IS NULL)
    GROUP BY
        b.node_position,
        b.range_start,
        b.range_end
    ORDER BY b.node_position;
"""

GET_BLOCK_COUNT_SIMPLE = """
    SELECT node_position, range_start, range_end, count(t.{key})
    FROM {mtree_table} mt
    LEFT JOIN {schema}.{table} t
    ON t.{key} >= mt.range_start
    AND (t.{key} <= mt.range_end OR mt.range_end IS NULL)
    WHERE mt.node_level = 0
    AND mt.node_position = %s
    GROUP BY mt.node_position, mt.range_start, mt.range_end
"""

GET_BLOCK_SIZE_FROM_METADATA = """
    SELECT block_size
    FROM ace_mtree_metadata
    WHERE schema_name = {schema}
    AND table_name = {table}
"""

GET_MAX_NODE_LEVEL = """
    SELECT MAX(node_level)
    FROM {mtree_table}
"""

COMPARE_BLOCKS_SQL = """
    SELECT * FROM {table_name} WHERE {where_clause}
"""

DROP_XOR_FUNCTION = """
    DROP FUNCTION IF EXISTS bytea_xor(bytea, bytea) CASCADE;
"""

DROP_METADATA_TABLE = """
    DROP TABLE IF EXISTS ace_mtree_metadata CASCADE;
"""

DROP_BULK_TRIGGER_FUNCTION = """
    DROP FUNCTION IF EXISTS bulk_block_tracking_dispatcher() CASCADE;
"""

DROP_MTREE_TABLE = """
    DROP TABLE IF EXISTS {mtree_table} CASCADE;
"""

DROP_MTREE_TRIGGERS = """
    DROP TRIGGER IF EXISTS {trigger}_insert_stmt ON {schema}.{table};
    DROP TRIGGER IF EXISTS {trigger}_update_stmt ON {schema}.{table};
    DROP TRIGGER IF EXISTS {trigger}_delete_stmt ON {schema}.{table};
"""

CREATE_BULK_TRIGGER_FUNCTION = """
CREATE OR REPLACE FUNCTION bulk_block_tracking_dispatcher()
RETURNS trigger AS $$
DECLARE
    pkey_info      text := TG_ARGV[0];
    is_composite   boolean;
    t_schema       text := TG_TABLE_SCHEMA;
    t_table        text := TG_TABLE_NAME;
    mtree_table    text := 'ace_mtree_' || t_schema || '_' || t_table;
    key_columns    text[];
    composite_type text;
    rec record;
BEGIN
    SELECT m.is_composite
      INTO is_composite
      FROM ace_mtree_metadata m
     WHERE m.schema_name = t_schema
       AND m.table_name = t_table;

    IF TG_OP = 'INSERT' THEN
        IF is_composite THEN
            key_columns := string_to_array(pkey_info, ',');
            composite_type := t_schema || '_' || t_table || '_key_type';
            EXECUTE format($f$
               WITH affected AS (
                 SELECT count(*) AS cnt,
                   (SELECT key_val FROM (
                     SELECT ROW(%s)::%I AS key_val FROM new_table
                   ) x ORDER BY key_val ASC LIMIT 1) AS min_key,
                   (SELECT key_val FROM (
                     SELECT ROW(%s)::%I AS key_val FROM new_table
                   ) x ORDER BY key_val DESC LIMIT 1) AS max_key
                 FROM new_table
               )
               UPDATE %I
               SET dirty = true,
                   inserts_since_tree_update = inserts_since_tree_update + affected.cnt,
                   last_modified = current_timestamp
               FROM affected
               WHERE node_level = 0
               AND
               (
                    (
                        range_start <= affected.min_key AND
                        (range_end > affected.min_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start <= affected.max_key AND
                        (range_end > affected.max_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start >= affected.min_key AND
                        range_start < affected.max_key
                    )
                )
            $f$, array_to_string(key_columns, ', '), composite_type,
                 array_to_string(key_columns, ', '), composite_type,
                 mtree_table);

            -- Is this even needed anymore?
            EXECUTE format($f$
               WITH affected AS (
                 SELECT (SELECT key_val FROM (
                   SELECT ROW(%s)::%I AS key_val FROM new_table
                 ) x ORDER BY key_val DESC LIMIT 1) AS max_key
               )
               UPDATE %I
               SET range_end = NULL,
                   dirty = true,
                   last_modified = current_timestamp
               FROM affected
               WHERE node_level = 0
                 AND range_end IS NOT NULL
                 AND affected.max_key > range_end
                 AND node_position =
                    (
                        SELECT max(node_position)
                        FROM %I
                        WHERE node_level = 0
                    )
            $f$, array_to_string(key_columns, ', '), composite_type,
                 mtree_table, mtree_table);

        ELSE
            EXECUTE format($f$
               WITH affected AS (
                 SELECT count(*) AS cnt, MIN(%I) AS min_key, MAX(%I) AS max_key
                 FROM new_table
               )
               UPDATE %I
               SET dirty = true,
                   inserts_since_tree_update = inserts_since_tree_update + affected.cnt,
                   last_modified = current_timestamp
               FROM affected
               WHERE node_level = 0
               AND
               (
                    (
                        range_start <= affected.min_key AND
                        (range_end > affected.min_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start <= affected.max_key AND
                        (range_end > affected.max_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start >= affected.min_key AND
                        range_start < affected.max_key
                    )
                )
            $f$, pkey_info, pkey_info, mtree_table);

            EXECUTE format($f$
               WITH affected AS (
                 SELECT MAX(%I) AS max_key FROM new_table
               )
               UPDATE %I
               SET range_end = NULL,
                   dirty = true,
                   last_modified = current_timestamp
               FROM affected
               WHERE node_level = 0
               AND range_end IS NOT NULL
               AND affected.max_key > range_end
               AND node_position =
               (
                    SELECT
                    max(node_position)
                    FROM %I
                    WHERE
                    node_level = 0
                )
            $f$, pkey_info, mtree_table, mtree_table);
        END IF;

    ELSIF TG_OP = 'DELETE' THEN
        IF is_composite THEN
            key_columns := string_to_array(pkey_info, ',');
            composite_type := t_schema || '_' || t_table || '_key_type';
            EXECUTE format($f$
               WITH affected AS (
                 SELECT count(*) AS cnt,
                   (SELECT key_val FROM (
                     SELECT ROW(%s)::%I AS key_val FROM old_table
                   ) x ORDER BY key_val ASC LIMIT 1) AS min_key,
                   (SELECT key_val FROM (
                     SELECT ROW(%s)::%I AS key_val FROM old_table
                   ) x ORDER BY key_val DESC LIMIT 1) AS max_key
                 FROM old_table
               )
               UPDATE %I
               SET dirty = true,
                   deletes_since_tree_update = deletes_since_tree_update + affected.cnt,
                   last_modified = current_timestamp
               FROM affected
               WHERE node_level = 0
               AND
               (
                    (
                        range_start <= affected.min_key AND
                        (range_end >= affected.max_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start >= affected.min_key AND
                        range_start <= affected.max_key AND
                        (range_end <= affected.max_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start <= affected.min_key AND
                        (range_end >= affected.min_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start <= affected.max_key AND
                        (range_end >= affected.max_key OR range_end IS NULL)
                    )
                )
            $f$, array_to_string(key_columns, ', '), composite_type,
                 array_to_string(key_columns, ', '), composite_type,
                 mtree_table);
        ELSE
            EXECUTE format($f$
               WITH affected AS (
                 SELECT count(*) AS cnt, MIN(%I) AS min_key, MAX(%I) AS max_key
                 FROM old_table
               )
               UPDATE %I
               SET dirty = true,
                   deletes_since_tree_update = deletes_since_tree_update + affected.cnt,
                   last_modified = current_timestamp
               FROM affected
               WHERE node_level = 0
               AND
               (
                    (
                        range_start <= affected.min_key AND
                        (range_end >= affected.max_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start >= affected.min_key AND
                        range_start <= affected.max_key AND
                        (range_end <= affected.max_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start <= affected.min_key AND
                        (range_end >= affected.min_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start <= affected.max_key AND
                        (range_end >= affected.max_key OR range_end IS NULL)
                    )
                 )
            $f$, pkey_info, pkey_info, mtree_table);
        END IF;

    ELSIF TG_OP = 'UPDATE' THEN
        IF is_composite THEN
            key_columns := string_to_array(pkey_info, ',');
            composite_type := t_schema || '_' || t_table || '_key_type';
            EXECUTE format($f$
               WITH affected AS (
                 SELECT count(*) AS cnt,
                   (SELECT key_val FROM (
                     SELECT ROW(%s)::%I AS key_val FROM new_table
                     UNION
                     SELECT ROW(%s)::%I AS key_val FROM old_table
                   ) x ORDER BY key_val ASC LIMIT 1) AS min_key,
                   (SELECT key_val FROM (
                     SELECT ROW(%s)::%I AS key_val FROM new_table
                     UNION
                     SELECT ROW(%s)::%I AS key_val FROM old_table
                   ) x ORDER BY key_val DESC LIMIT 1) AS max_key
                 FROM new_table
               )
               UPDATE %I
               SET dirty = true,
                   inserts_since_tree_update = inserts_since_tree_update + affected.cnt,
                   last_modified = current_timestamp
               FROM affected
               WHERE node_level = 0
               AND
               (
                    (
                        range_start <= affected.min_key AND
                        (range_end > affected.min_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start <= affected.max_key AND
                        (range_end > affected.max_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start >= affected.min_key AND
                        range_start <= affected.max_key
                    )
                    OR
                    (
                        (
                            range_end >= affected.min_key AND
                            range_end <= affected.max_key
                        )
                        OR
                        range_end IS NULL
                    )
                 )
            $f$, array_to_string(key_columns, ', '), composite_type,
                 array_to_string(key_columns, ', '), composite_type,
                 array_to_string(key_columns, ', '), composite_type,
                 array_to_string(key_columns, ', '), composite_type,
                 mtree_table);

            EXECUTE format($f$
               WITH affected AS (
                 SELECT (SELECT key_val FROM (
                   SELECT ROW(%s)::%I AS key_val FROM new_table
                   UNION
                   SELECT ROW(%s)::%I AS key_val FROM old_table
                 ) x ORDER BY key_val DESC LIMIT 1) AS max_key
               )
               UPDATE %I
               SET range_end = NULL,
                   dirty = true,
                   last_modified = current_timestamp
               FROM affected
               WHERE node_level = 0
               AND range_end IS NOT NULL
               AND affected.max_key > range_end
               AND node_position =
                (
                    SELECT
                    max(node_position)
                    FROM %I
                    WHERE
                    node_level = 0
                )
            $f$, array_to_string(key_columns, ', '), composite_type,
                 array_to_string(key_columns, ', '), composite_type,
                 mtree_table, mtree_table);
        ELSE
            EXECUTE format($f$
               WITH affected AS (
                 SELECT count(*) AS cnt, MIN(%I) AS min_key, MAX(%I) AS max_key
                 FROM new_table
               )
               UPDATE %I
               SET dirty = true,
                   inserts_since_tree_update = inserts_since_tree_update + affected.cnt,
                   last_modified = current_timestamp
               FROM affected
               WHERE node_level = 0
               AND
               (
                    (
                        range_start <= affected.min_key AND
                        (range_end > affected.min_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start <= affected.max_key AND
                        (range_end > affected.max_key OR range_end IS NULL)
                    )
                    OR
                    (
                        range_start >= affected.min_key AND
                        range_start <= affected.max_key
                    )
                    OR
                    (
                        (
                            range_end >= affected.min_key AND
                            range_end <= affected.max_key
                        )
                        OR
                        range_end IS NULL
                    )
                )
            $f$, pkey_info, pkey_info, mtree_table);

            EXECUTE format($f$
               WITH affected AS (
                 SELECT MAX(%I) AS max_key FROM new_table
               )
               UPDATE %I
               SET range_end = NULL,
                   dirty = true,
                   last_modified = current_timestamp
               FROM affected
               WHERE node_level = 0
               AND range_end IS NOT NULL
               AND affected.max_key > range_end
               AND node_position =
                (
                    SELECT
                    max(node_position)
                    FROM %I
                    WHERE
                    node_level = 0
                )
            $f$, pkey_info, mtree_table, mtree_table);
        END IF;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
"""
