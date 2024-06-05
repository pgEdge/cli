-- 6111c - Validate tables on n1

-- Prepared statement for spock.tables so that we can execute it frequently in the script below
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname = $1 ORDER BY relid;

-- Validate sub_tx_table0
-- Expected: table does not exist
\d sub_tx_table0
EXECUTE spocktab('sub_tx_table0');

-- Validate sub_tx_table2
-- Expected: table does not exist
\d sub_tx_table2
EXECUTE spocktab('sub_tx_table2');

-- Validate sub_tx_table3
-- Expected: table does not exist
\d sub_tx_table3
EXECUTE spocktab('sub_tx_table3');

-- Validate sub_tx_table5, sub_tx_table5a, sub_tx_table5c, sub_tx_table5b should not exist
-- Expected: tables do not exist
\d sub_tx_table5
EXECUTE spocktab('sub_tx_table5');
\d sub_tx_table5a
EXECUTE spocktab('sub_tx_table5a');
\d sub_tx_table5b
EXECUTE spocktab('sub_tx_table5b'); -- should not exist
\d sub_tx_table5c
EXECUTE spocktab('sub_tx_table5c');

-- Validate table_ctas1
-- Expected: table does not exist
\d table_ctas1
EXECUTE spocktab('table_ctas1');

-- Validate table_ctas2
-- Expected: table does not exist
\d table_ctas2
EXECUTE spocktab('table_ctas2');

-- Validate table_ctas3
-- Expected: table does not exist
\d table_ctas3
EXECUTE spocktab('table_ctas3');

-- Validate table_ctas4
-- Expected: table does not exist
\d table_ctas4
EXECUTE spocktab('table_ctas4');

-- Validate table_ctas5
-- Expected: table does not exist
\d table_ctas5
EXECUTE spocktab('table_ctas5');

-- Validate table_ctas6
-- Expected: table does not exist
\d table_ctas6
EXECUTE spocktab('table_ctas6');

-- Validate table_si1
-- Expected: table does not exist
\d table_si1
EXECUTE spocktab('table_si1');

-- Validate table_si2
-- Expected: table does not exist
\d table_si2
EXECUTE spocktab('table_si2');

-- Validate table_si3
-- Expected: table does not exist
\d table_si3
EXECUTE spocktab('table_si3');

-- Validate table_si4
-- Expected: table does not exist
\d table_si4
EXECUTE spocktab('table_si4');

-- Validate table_si5
-- Expected: table does not exist
\d table_si5
EXECUTE spocktab('table_si5');

-- Validate table_l1
-- Expected: table does not exist
\d table_l1
EXECUTE spocktab('table_l1');

-- Validate table_l2
-- Expected: table does not exist
\d table_l2
EXECUTE spocktab('table_l2');

-- Validate table_l3
-- Expected: table does not exist
\d table_l3
EXECUTE spocktab('table_l3');

-- Validate table_l4
-- Expected: table does not exist
\d table_l4
EXECUTE spocktab('table_l4');

-- Validate table_l5
-- Expected: table does not exist
\d table_l5
EXECUTE spocktab('table_l5');
