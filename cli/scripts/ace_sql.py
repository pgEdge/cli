# Various SQL statements for Merkle Tree operations

CREATE_METADATA_TABLE = """
    CREATE TABLE IF NOT EXISTS ace_mtree_metadata (
        schema_name text,
        table_name text,
        total_rows bigint,
        num_blocks int,
        last_updated timestamptz,
        PRIMARY KEY (schema_name, table_name)
    )
"""

CREATE_MTREE_TABLE = """
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

CREATE_GENERIC_BLOCK_ID_FUNCTION = """
    CREATE OR REPLACE FUNCTION get_block_id(
        schema_name text,
        table_name text,
        pkey_value anyelement
    )
    RETURNS bigint AS $$
    DECLARE
        pos bigint;
        last_pos bigint;
        last_block_end text;
        mtree_table text;
        pkey_type text;
        boolean_result boolean;
    BEGIN
        mtree_table := 'ace_mtree_' || schema_name || '_' || table_name;

        pkey_type := pg_typeof(pkey_value)::text;

        -- First try to find the exact block this key belongs to
        EXECUTE format('
            SELECT node_position
            FROM %I
            WHERE node_level = 0
            AND range_start <= $1
            AND (range_end > $1 OR range_end IS NULL)
            ORDER BY node_position
            LIMIT 1', mtree_table)
        USING pkey_value INTO pos;

        -- If no block found, this key might be beyond the last block
        -- In this case, we should return the last block
        IF pos IS NULL THEN
            EXECUTE format('
                SELECT node_position, range_end::text
                FROM %I
                WHERE node_level = 0
                ORDER BY node_position DESC
                LIMIT 1', mtree_table)
            INTO last_pos, last_block_end;

            IF last_block_end IS NULL THEN
                RETURN last_pos;
            ELSE
                EXECUTE format('
                    SELECT $1 >= $2::%s', pkey_type)
                USING pkey_value, last_block_end INTO STRICT boolean_result;

                IF boolean_result THEN
                    RETURN last_pos;
                ELSE
                    -- Otherwise return the first block
                    EXECUTE format('
                        SELECT node_position
                        FROM %I
                        WHERE node_level = 0
                        ORDER BY node_position
                        LIMIT 1', mtree_table)
                    INTO pos;
                    RETURN pos;
                END IF;
            END IF;
        END IF;

        RETURN pos;
    END;
    $$ LANGUAGE plpgsql STABLE;
"""

CREATE_GENERIC_TRIGGER_FUNCTION = """
    CREATE OR REPLACE FUNCTION track_dirty_blocks()
    RETURNS trigger AS $$
    DECLARE
        affected_pos bigint;
        last_block_pos bigint;
        last_block_end text;
        schema_name text;
        table_name text;
        pkey_name text;
        mtree_table text;
        pkey_type text;
        boolean_result boolean;
    BEGIN
        IF TG_LEVEL = 'STATEMENT' THEN
            RETURN NULL;
        END IF;

        schema_name := TG_TABLE_SCHEMA;
        table_name := TG_TABLE_NAME;
        pkey_name := TG_ARGV[0];
        mtree_table := 'ace_mtree_' || schema_name || '_' || table_name;

        IF TG_OP = 'INSERT' THEN
            -- Get the last block's position and end value
            EXECUTE format('
                SELECT node_position, range_end::text
                FROM %I
                WHERE node_level = 0
                ORDER BY node_position DESC
                LIMIT 1', mtree_table)
            INTO last_block_pos, last_block_end;

            -- If this key is beyond the last block's end, set its range_end to NULL
            IF last_block_end IS NOT NULL THEN
                -- TODO: Can we directly compare as text since we're just checking
                -- if greater?
                EXECUTE format('
                    SELECT ($1.%I)::text > $2', pkey_name)
                USING NEW, last_block_end INTO STRICT boolean_result;

                IF boolean_result THEN
                    EXECUTE format('
                        UPDATE %I
                        SET range_end = NULL,
                            dirty = true,
                            inserts_since_tree_update = inserts_since_tree_update + 1,
                            last_modified = current_timestamp
                        WHERE node_level = 0
                        AND node_position = $1', mtree_table)
                    USING last_block_pos;
                END IF;
            END IF;

            EXECUTE format('
                SELECT get_block_id($1, $2, $3.%I)', pkey_name)
            USING schema_name, table_name, NEW INTO affected_pos;

            EXECUTE format('
                UPDATE %I
                SET dirty = true,
                    inserts_since_tree_update = inserts_since_tree_update + 1,
                    last_modified = current_timestamp
                WHERE node_level = 0
                AND node_position = $1', mtree_table)
            USING affected_pos;

        ELSIF TG_OP = 'DELETE' THEN
            EXECUTE format('
                SELECT get_block_id($1, $2, $3.%I)', pkey_name)
            USING schema_name, table_name, OLD INTO affected_pos;

            EXECUTE format('
                UPDATE %I
                SET dirty = true,
                    deletes_since_tree_update = deletes_since_tree_update + 1,
                    last_modified = current_timestamp
                WHERE node_level = 0
                AND node_position = $1', mtree_table)
            USING affected_pos;

        ELSIF TG_OP = 'UPDATE' THEN
            EXECUTE format('
                SELECT $1.%I IS DISTINCT FROM $2.%I', pkey_name, pkey_name)
            USING OLD, NEW INTO STRICT boolean_result;

            IF boolean_result THEN
                -- Mark both blocks as dirty
                EXECUTE format('
                    SELECT get_block_id($1, $2, $3.%I)', pkey_name)
                USING schema_name, table_name, OLD INTO affected_pos;

                EXECUTE format('
                    UPDATE %I
                    SET dirty = true,
                        deletes_since_tree_update = deletes_since_tree_update + 1,
                        last_modified = current_timestamp
                    WHERE node_level = 0
                    AND node_position = $1', mtree_table)
                USING affected_pos;

                EXECUTE format('
                    SELECT get_block_id($1, $2, $3.%I)', pkey_name)
                USING schema_name, table_name, NEW INTO affected_pos;

                EXECUTE format('
                    UPDATE %I
                    SET dirty = true,
                        inserts_since_tree_update = inserts_since_tree_update + 1,
                        last_modified = current_timestamp
                    WHERE node_level = 0
                    AND node_position = $1', mtree_table)
                USING affected_pos;

                RETURN NULL;
            END IF;

            EXECUTE format('
                SELECT get_block_id($1, $2, $3.%I)', pkey_name)
            USING schema_name, table_name, NEW INTO affected_pos;

            EXECUTE format('
                UPDATE %I
                SET dirty = true,
                    last_modified = current_timestamp
                WHERE node_level = 0
                AND node_position = $1', mtree_table)
            USING affected_pos;
        END IF;

        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
"""

CREATE_GENERIC_TRIGGER = """
    DROP TRIGGER IF EXISTS {trigger}
    ON {schema}.{table};
    CREATE TRIGGER {trigger}
    AFTER INSERT OR UPDATE OR DELETE ON {schema}.{table}
    FOR EACH ROW EXECUTE FUNCTION track_dirty_blocks({key});
"""

ENABLE_ALWAYS = """
    ALTER TABLE {schema}.{table}
    ENABLE ALWAYS TRIGGER {trigger};
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
        (schema_name, table_name, total_rows, num_blocks, last_updated)
    VALUES (%s, %s, %s, %s, current_timestamp)
    ON CONFLICT (schema_name, table_name) DO UPDATE
    SET total_rows = EXCLUDED.total_rows,
        num_blocks = EXCLUDED.num_blocks,
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
        WHERE {key} >= %(range_start)s
        AND ({key} <= %(range_end)s OR %(range_end)s IS NULL)
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
