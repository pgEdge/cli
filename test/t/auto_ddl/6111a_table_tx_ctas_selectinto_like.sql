-- This script covers the following CREATE TABLE constructs for AutoDDL:
-- CREATE TABLE in transactions
-- CREATE TABLE AS
-- SELECT .. INTO .. FROM EXISTING
-- CREATE TABLE LIKE


-- Prepared statement for spock.tables so that we can execute it frequently in the script below
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname = $1 ORDER BY relid;

----------------------------
-- Table DDL in transactions
----------------------------

-- Create Table within transaction, commit
--table should be created successfully (and auto replicated)
BEGIN;
CREATE TABLE sub_tx_table0 (c int primary key);
COMMIT;

\d sub_tx_table0
EXECUTE spocktab('sub_tx_table0'); --default repset

-- DDL within tx, Rollback
-- table will not get created on n1 and therefore nothing should replicate to n2
-- (although the ddl replication INFO message would appear but it should rollback)
BEGIN;
CREATE TABLE sub_tx_table0a (c int);
ROLLBACK;

\d sub_tx_table0a
EXECUTE spocktab('sub_tx_table0a');

--DDL within transaction and savepoints and rollback/commit
--table sub_tx_table1 will not be created so it should not get replicated
BEGIN;
SAVEPOINT a;
CREATE TABLE sub_tx_table1 (c int);
 ALTER TABLE sub_tx_table1 ALTER c TYPE bigint; 
 ROLLBACK TO a;
COMMIT;

\d sub_tx_table1
EXECUTE spocktab('sub_tx_table1');

--ALTERING TABLE within transaction, savepoints, rollback
-- After commit, the table should have c column datatype to bigint
CREATE TABLE sub_tx_table2 (c int);
BEGIN;
  ALTER TABLE sub_tx_table2 ALTER c TYPE bigint;
  SAVEPOINT q; 
  DROP TABLE sub_tx_table2; 
  ROLLBACK TO q;
COMMIT;

\d sub_tx_table2
EXECUTE spocktab('sub_tx_table2');

BEGIN;
CREATE TABLE sub_tx_table3 (a smallint primary key, b real);
INSERT INTO sub_tx_table3 VALUES
  (56, 7.8), (100, 99.097), (0, 0.09561), (42, 324.78), (777, 777.777);
END;

\d sub_tx_table3
SELECT * FROM sub_tx_table3 order by a;
EXECUTE spocktab('sub_tx_table3');

BEGIN;
CREATE TABLE sub_tx_table4 (a int4 primary key);
DELETE FROM sub_tx_table3;
-- should be empty
SELECT count(*) from sub_tx_table3;--0 rows
ABORT;--rollback
--table sub_tx_table4 should not exist
\d sub_tx_table4
EXECUTE spocktab('sub_tx_table4');
SELECT count(*) from sub_tx_table3;--5 rows, which should also exist on n2 (validated in the 6111b file)

-- Nested transactions with multiple savepoints and a mix of rollbacks and commits
BEGIN;
  CREATE TABLE sub_tx_table5 (c int);
  SAVEPOINT sp3;
  CREATE TABLE sub_tx_table5a (c int primary key);
  SAVEPOINT sp4;
  CREATE TABLE sub_tx_table5b (c int);
  ROLLBACK TO sp4; -- Rolls back the creation of sub_tx_table5b
  SAVEPOINT sp5;
  CREATE TABLE sub_tx_table5c (c int);
  COMMIT; -- Commits all changes since the last rollback, sub_tx_table5a and sub_tx_table5c should exist
COMMIT;

-- Validate sub_tx_table5, sub_tx_table5a, and sub_tx_table5c should exist, sub_tx_table5b should not
\d sub_tx_table5
EXECUTE spocktab('sub_tx_table5'); -- should be in default_insert_only set
\d sub_tx_table5a
EXECUTE spocktab('sub_tx_table5a'); -- should be in default
\d sub_tx_table5b
EXECUTE spocktab('sub_tx_table5b'); -- should not exist
\d sub_tx_table5c
EXECUTE spocktab('sub_tx_table5c'); -- should be in default_insert_only set



-----------------------
-- CREATE TABLE AS
-----------------------

-- Create a base table for reference
CREATE TABLE table_base1 (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT
);

-- Insert initial data into table_base1
INSERT INTO table_base1 (id, name, age) VALUES
(1, 'Alice', 30),
(2, 'Bob', 25),
(3, 'Carol', 35);

-- Basic CREATE TABLE AS with data
CREATE TABLE table_ctas1 AS
SELECT * FROM table_base1;

-- CREATE TABLE AS with IF NOT EXISTS
CREATE TABLE IF NOT EXISTS table_ctas1 AS
SELECT id, name FROM table_base1;

-- Validate table_ctas1
\d table_ctas1
EXECUTE spocktab('table_ctas1'); -- should be in default_insert_only set

-- CREATE TABLE AS with specific columns and data
CREATE TABLE IF NOT EXISTS table_ctas2 AS
SELECT id, age FROM table_base1
WHERE age > 30;

-- Add primary key through ALTER TABLE
ALTER TABLE table_ctas2 ADD PRIMARY KEY (id);

-- Validate table_ctas2
\d table_ctas2
EXECUTE spocktab('table_ctas2'); -- should be in default set

-- CREATE TABLE AS with VALUES clause and primary key
CREATE TABLE table_ctas3 (id, value) AS
VALUES (1, 10), (2, 20), (3, 30);
ALTER TABLE table_ctas3 ADD PRIMARY KEY (id);

-- Validate table_ctas3
\d table_ctas3
EXECUTE spocktab('table_ctas3'); -- should be in default set

-- CREATE TABLE AS with query and using WITH NO DATA
CREATE TABLE table_ctas4 AS
SELECT id, name, age * 2 AS double_age FROM table_base1
WHERE age <= 30 WITH NO DATA;

-- Validate table_ctas4
\d table_ctas4
EXECUTE spocktab('table_ctas4'); -- should be in default_insert_only set

-- CREATE TABLE AS with expression 
CREATE TABLE table_ctas5 AS
SELECT generate_series(1, 10) AS num;

-- Validate table_ctas5
\d table_ctas5
EXECUTE spocktab('table_ctas5'); -- should be in default_insert_only set

-- CREATE TABLE AS with explain analyze, redirecting the output to /dev/null so that the varying query plan is not 
-- captured in the expected output, to keep our output consistent across runs.
\o /dev/null
EXPLAIN ANALYZE CREATE TABLE table_ctas6 AS
SELECT 1 AS a;
\o

-- Validate table_ctas6
\d table_ctas6
EXECUTE spocktab('table_ctas6'); -- should be in default_insert_only set

-----------------------------------
-- Create table using SELECT .. INTO .. 
-----------------------------------

-- Create an existing table for reference
CREATE TABLE table_existing1 (
    id INT PRIMARY KEY,
    column1 TEXT,
    column2 INT,
    column3 DATE,
    column4 BOOLEAN
);

-- Insert initial data into table_existing1
INSERT INTO table_existing1 (id, column1, column2, column3, column4) VALUES
(1, 'value1', 10, '2023-01-01', TRUE),
(2, 'value2', 20, '2023-01-02', FALSE),
(3, 'value3', 30, '2023-01-03', TRUE),
(4, 'value4', 40, '2023-01-04', FALSE);

-- Basic SELECT INTO
SELECT * INTO table_si1 FROM table_existing1;

-- Validate table_si1
\d table_si1
EXECUTE spocktab('table_si1'); -- should be in default_insert_only set

-- SELECT INTO with specific columns and conditions
SELECT id, column1, column2 INTO table_si2 FROM table_existing1 WHERE column2 > 20;

-- Validate table_si2
\d table_si2
EXECUTE spocktab('table_si2'); -- should be in default_insert_only set
-- Expected data: (3, 'value3', 30), (4, 'value4', 40)

-- SELECT INTO with GROUP BY and HAVING
SELECT column4, COUNT(*) AS count INTO table_si3 FROM table_existing1 GROUP BY column4 HAVING COUNT(*) > 1;

-- Validate table_si3
\d table_si3
EXECUTE spocktab('table_si3'); -- should be in default_insert_only set
-- Expected data: (TRUE, 2), (FALSE, 2)

-- SELECT INTO with ORDER BY and LIMIT
SELECT id, column1 INTO table_si4 FROM table_existing1 ORDER BY column2 DESC LIMIT 2;

-- Validate table_si4
\d table_si4
EXECUTE spocktab('table_si4'); -- should be in default_insert_only set
-- Expected data: (4, 'value4'), (3, 'value3')

-- Complex SELECT INTO with JOIN, GROUP BY, ORDER BY, and LIMIT
CREATE TABLE table_existing2 (
    ref_id INT,
    extra_data VARCHAR(50)
);

-- Insert initial data into table_existing2
INSERT INTO table_existing2 (ref_id, extra_data) VALUES
(1, 'extra1'),
(2, 'extra2'),
(3, 'extra3'),
(4, 'extra4');

SELECT e1.id, e1.column1, e2.extra_data INTO table_si5
FROM table_existing1 e1
JOIN table_existing2 e2 ON e1.id = e2.ref_id
WHERE e1.column4 = TRUE
GROUP BY e1.id, e1.column1, e2.extra_data
ORDER BY e1.id
LIMIT 3;

-- Validate table_si5
\d table_si5
EXECUTE spocktab('table_si5'); -- should be in default_insert_only set
-- Expected data: (1, 'value1', 'extra1'), (3, 'value3', 'extra3')

---------------------
-- Create table using CREATE TABLE LIKE
--------------------

-- Create base tables with various constraints

-- Base table with primary key and default value
CREATE TABLE table_base1a (
    col1 INT PRIMARY KEY,
    col2 TEXT DEFAULT 'default_text'
);

-- Base table without primary key, but with check constraint and unique constraint
CREATE TABLE table_base2 (
    col1 INT,
    col2 TEXT,
    col3 DATE,
    CONSTRAINT chk_col1 CHECK (col1 > 0),
    UNIQUE (col2)
);

-- Insert initial data into table_base1a
INSERT INTO table_base1a (col1, col2) VALUES (1, 'text1'), (2, 'text2');
-- Insert initial data into table_base2
INSERT INTO table_base2 (col1, col2, col3) VALUES (1, 'unique_text1', '2023-01-01'), (2, 'unique_text2', '2023-01-02');

-- Create table using LIKE including defaults and constraints
CREATE TABLE table_l1 (LIKE table_base1a INCLUDING DEFAULTS INCLUDING CONSTRAINTS);

-- Validate table_l1
-- Expected columns: col1 (without primary key), col2 (with default 'default_text')
\d table_l1
EXECUTE spocktab('table_l1'); -- should be in default_insert_only set


-- Create table using LIKE excluding defaults
CREATE TABLE table_l2 (LIKE table_base1a EXCLUDING DEFAULTS);

-- Validate table_l2
-- Expected columns: col1 (without primary key), col2 (without default)
\d table_l2
EXECUTE spocktab('table_l2'); -- should be in default_insert_only set


-- Create table using LIKE including all properties
CREATE TABLE table_l3 (LIKE table_base2 INCLUDING ALL);

-- Validate table_l3
-- Expected columns: col1, col2, col3 (with check constraint and unique constraint)
\d table_l3
EXECUTE spocktab('table_l3'); -- should be in default_insert_only set

-- Create table using LIKE excluding constraints
CREATE TABLE table_l4 (LIKE table_base2 EXCLUDING CONSTRAINTS);

-- Validate table_l4
-- Expected columns: col1, col2, col3 (without constraints)
\d table_l4
EXECUTE spocktab('table_l4'); -- should be in default_insert_only set

-- Create table using LIKE including indexes
CREATE TABLE table_l5 (LIKE table_base1a INCLUDING INDEXES);

-- Validate table_l5
-- Expected columns: col1 (primary key), col2 (without default), indexes copied
\d table_l5
EXECUTE spocktab('table_l5'); -- should be in default set


-- Insert data into the LIKE created tables to validate defaults and constraints
INSERT INTO table_l1 (col1) VALUES (3);
INSERT INTO table_l2 (col1, col2) VALUES (4, 'text4');
INSERT INTO table_l3 (col1, col2, col3) VALUES (3, 'unique_text3', '2023-01-03');
INSERT INTO table_l4 (col1, col2, col3) VALUES (4, 'text4', '2023-01-04');
INSERT INTO table_l5 (col1) VALUES (5);

-- Validate data in table_l1 , Expected data: (3, 'default_text')
SELECT * FROM table_l1;

-- Validate data in table_l2 , Expected data: (4, 'text4')
SELECT * FROM table_l2;

-- Validate data in table_l3 , Expected data: (3, 'unique_text3', '2023-01-03')
SELECT * FROM table_l3;

-- Validate data in table_l4 ,  Expected data: (4, 'text4', '2023-01-04')
SELECT * FROM table_l4;

-- Validate data in table_l5, Expected data: (5, )
SELECT * FROM table_l5;

