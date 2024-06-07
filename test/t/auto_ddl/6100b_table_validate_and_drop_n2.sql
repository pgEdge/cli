
-- AutoDDL validation on n2 to ensure all the DDL/DML performed in the 6100a files on n1 
-- was auto replicated to n2.
-- In the end, the same objects are dropped.

-- Prepared statement for spock.tables so that we can execute it frequently in the script below
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname = $1 ORDER BY relid;

-- Final validation of all tables along with querying the spock.tables
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

-- Validating data in all tables
SELECT * FROM employees ORDER BY emp_id;
SELECT * FROM departments ORDER BY dept_id;
SELECT * FROM projects ORDER BY project_id;
SELECT * FROM employee_projects ORDER BY emp_id, project_id;
SELECT * FROM products ORDER BY product_id;
SELECT * FROM "CaseSensitiveTable" ORDER BY "ID";
SELECT * FROM test_tab1 ORDER BY id;
SELECT * FROM test_tab2 ORDER BY id;
SELECT * FROM test_tab3 ORDER BY id;
SELECT * FROM test_tab4 ORDER BY id;
SELECT * FROM test_tab5 ORDER BY 1;

-- Execute drop statements on n2 to exercise DROP TABLE, ensuring it gets replicated.
-- This also helps with the cleanup
drop table employees cascade;
drop table departments cascade;
drop table projects cascade;
drop table employee_projects cascade;
drop table products cascade;
drop table "CaseSensitiveTable";
drop table test_tab1;
drop table test_tab2;
drop table test_tab3;
drop table test_tab4;
drop table test_tab5;
