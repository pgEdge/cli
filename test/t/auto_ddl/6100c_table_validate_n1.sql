
-- Final AutoDDL validation for the 6100 series on n1 to ensure all the DROP TABLE performed in the 6100b files on n2 
-- was auto replicated to n1.
-- None of the Tables should exist and spock.tables should not contain any entries for these tables

-- Prepared statement for spock.tables so that we can execute it frequently in the script below
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname = $1 ORDER BY relid;

-- Final validation of all tables along with querying the spock.tables
-- validating all tables dropped on n1
\d+ employees
EXECUTE spocktab('employees');

\d+ departments
execute spocktab('departments');

\d+ projects
execute spocktab('projects');

\d+ employee_projects
execute spocktab('employee_projects');

\d+ products
execute spocktab('products');

\d+ "CaseSensitiveTable"
execute spocktab('CaseSensitiveTable');

\d+ test_tab1
execute spocktab('test_tab1');

\d+ test_tab2
execute spocktab('test_tab2');

\d+ test_tab3
execute spocktab('test_tab3');

\d+ test_tab4
EXECUTE spocktab('test_tab4');

\d+ test_tab5
EXECUTE spocktab('test_tab5');
