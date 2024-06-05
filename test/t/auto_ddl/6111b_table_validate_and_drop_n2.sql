-- 6111b - Validate and drop tables on n2

-- Prepared statement for spock.tables so that we can execute it frequently in the script below
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname = $1 ORDER BY relid;

-- Validate sub_tx_table0
-- Expected: table exists with column c of type int and primary key
\d sub_tx_table0
EXECUTE spocktab('sub_tx_table0'); -- Replication set: default

-- Validate sub_tx_table0a
-- Expected: table does not exist
\d sub_tx_table0a

-- Validate sub_tx_table1
-- Expected: table does not exist
\d sub_tx_table1

-- Validate sub_tx_table2
-- Expected: table exists with column c of type bigint
\d sub_tx_table2
EXECUTE spocktab('sub_tx_table2'); -- Replication set: default_insert_only

-- Validate sub_tx_table3
-- Expected: table exists with columns a (smallint, primary key) and b (real)
\d sub_tx_table3
EXECUTE spocktab('sub_tx_table3'); -- Replication set: default
-- Expected data: (0, 0.09561), (42, 324.78), (56, 7.8), (100, 99.097), (777, 777.777)
SELECT * FROM sub_tx_table3 ORDER BY a;

-- Validate sub_tx_table4
-- Expected: table does not exist
\d sub_tx_table4

-- Validate sub_tx_table5, sub_tx_table5a, and sub_tx_table5c, sub_tx_table5b should not exist
\d sub_tx_table5
EXECUTE spocktab('sub_tx_table5'); -- Replication set: default_insert_only

\d sub_tx_table5a
EXECUTE spocktab('sub_tx_table5a'); -- Replication set: default

\d sub_tx_table5b

\d sub_tx_table5c
EXECUTE spocktab('sub_tx_table5c'); -- Replication set: default_insert_only


-- Validate table_ctas1
-- Expected: table exists with columns id (int), name (varchar), age (int)
\d table_ctas1
EXECUTE spocktab('table_ctas1'); -- Replication set: default_insert_only
-- Expected data: (1, 'Alice', 30), (2, 'Bob', 25), (3, 'Carol', 35)
SELECT * FROM table_ctas1 ORDER BY id;

-- Validate table_ctas2
-- Expected: table exists with columns id (int), age (int), primary key on id
\d table_ctas2
EXECUTE spocktab('table_ctas2'); -- Replication set: default
-- Expected data: (3, 35)
SELECT * FROM table_ctas2 ORDER BY id;

-- Validate table_ctas3
-- Expected: table exists with columns id (int), value (int), primary key on id
\d table_ctas3
EXECUTE spocktab('table_ctas3'); -- Replication set: default
-- Expected data: (1, 10), (2, 20), (3, 30)
SELECT * FROM table_ctas3 ORDER BY id;

-- Validate table_ctas4
-- Expected: table exists with columns id (int), name (varchar), double_age (int), no data
\d table_ctas4
EXECUTE spocktab('table_ctas4'); -- Replication set: default_insert_only
-- Expected data: empty (no data)
SELECT * FROM table_ctas4 ORDER BY id;

-- Validate table_ctas5
-- Expected: table exists with column num (int)
\d table_ctas5
EXECUTE spocktab('table_ctas5'); -- Replication set: default_insert_only
-- Expected data: 1 through 10
SELECT * FROM table_ctas5 ORDER BY num;

-- Validate table_ctas6
-- Expected: table exists with column a (int)
\d table_ctas6
EXECUTE spocktab('table_ctas6'); -- Replication set: default_insert_only
-- Expected data: 1
SELECT * FROM table_ctas6 ORDER BY a;

-- Validate table_si1
-- Expected: table exists with columns id (int), column1 (text), column2 (int), column3 (date), column4 (boolean)
\d table_si1
EXECUTE spocktab('table_si1'); -- Replication set: default_insert_only
-- Expected data: (1, 'value1', 10, '2023-01-01', TRUE), (2, 'value2', 20, '2023-01-02', FALSE), (3, 'value3', 30, '2023-01-03', TRUE), (4, 'value4', 40, '2023-01-04', FALSE)
SELECT * FROM table_si1 ORDER BY id;

-- Validate table_si2
-- Expected: table exists with columns id (int), column1 (text), column2 (int)
\d table_si2
EXECUTE spocktab('table_si2'); -- Replication set: default_insert_only
-- Expected data: (3, 'value3', 30), (4, 'value4', 40)
SELECT * FROM table_si2 ORDER BY id;

-- Validate table_si3
-- Expected: table exists with columns column4 (boolean), count (int)
\d table_si3
EXECUTE spocktab('table_si3'); -- Replication set: default_insert_only
-- Expected data: (TRUE, 2), (FALSE, 2)
SELECT * FROM table_si3 ORDER BY column4;

-- Validate table_si4
-- Expected: table exists with columns id (int), column1 (text)
\d table_si4
EXECUTE spocktab('table_si4'); -- Replication set: default_insert_only
-- Expected data: (4, 'value4'), (3, 'value3')
SELECT * FROM table_si4 ORDER BY id;

-- Validate table_si5
-- Expected: table exists with columns id (int), column1 (text), extra_data (varchar)
\d table_si5
EXECUTE spocktab('table_si5'); -- Replication set: default_insert_only
-- Expected data: (1, 'value1', 'extra1'), (3, 'value3', 'extra3')
SELECT * FROM table_si5 ORDER BY id;

-- Validate table_l1
-- Expected: table exists with columns col1 (int), col2 (text, default 'default_text')
\d table_l1
EXECUTE spocktab('table_l1'); -- Replication set: default_insert_repset
-- Expected data:  (3, 'default_text')
SELECT * FROM table_l1 ORDER BY col1;

-- Validate table_l2
-- Expected: table exists with columns col1 (int, primary key), col2 (text)
\d table_l2
EXECUTE spocktab('table_l2'); -- Replication set: default_insert_only
-- Expected data: (4, 'text4')
SELECT * FROM table_l2 ORDER BY col1;

-- Validate table_l3
-- Expected: table exists with columns col1 (int), col2 (text), col3 (date), check constraint, unique constraint
\d table_l3
EXECUTE spocktab('table_l3'); -- Replication set: default_insert_only
-- Expected data: (3, 'unique_text3', '2023-01-03')
SELECT * FROM table_l3 ORDER BY col1;

-- Validate table_l4
-- Expected: table exists with columns col1 (int), col2 (text), col3 (date), no constraints
\d table_l4
EXECUTE spocktab('table_l4'); -- Replication set: default_insert_only
-- Expected data: (4, 'text4', '2023-01-04')
SELECT * FROM table_l4 ORDER BY col1;

-- Validate table_l5
-- Expected: table exists with columns col1 (int, primary key), col2 (text)
\d table_l5
EXECUTE spocktab('table_l5'); -- Replication set: default
-- Expected data: (5, )
SELECT * FROM table_l5 ORDER BY col1;

----------------------------
-- Cleanup: Drop all created tables
-----------------------------
-- Confirm autoDDL of DROP commands (and also to cleanup for all tables created in 6111a)

--cleanup for tables ddl in transactions
DROP TABLE sub_tx_table0;
DROP TABLE sub_tx_table2, sub_tx_table3;
DROP TABLE sub_tx_table5, sub_tx_table5a, sub_tx_table5c;

--cleanup for tables used in ctas
DROP TABLE table_base1;
DROP TABLE table_ctas1;
DROP TABLE table_ctas2;
DROP TABLE table_ctas3;
DROP TABLE table_ctas4;
DROP TABLE table_ctas5;
DROP TABLE table_ctas6;

--cleanup for select into

-- DROP commands for cleanup in 6111b
DROP TABLE table_existing1;
DROP TABLE table_existing2;
DROP TABLE table_si1;
DROP TABLE table_si2;
DROP TABLE table_si3;
DROP TABLE table_si4;
DROP TABLE table_si5;

-- DROP commands for cleanup in 6111b
DROP TABLE table_base1a;
DROP TABLE table_base2;
DROP TABLE table_l1;
DROP TABLE table_l2;
DROP TABLE table_l3;
DROP TABLE table_l4;
DROP TABLE table_l5;
