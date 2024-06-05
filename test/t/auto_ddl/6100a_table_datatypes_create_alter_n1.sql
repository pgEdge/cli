-- 6100a_create_alter_table_n1.sql
-- This script creates and alters tables on node n1 to test the autoDDL functionality.
-- It includes a wide variety of data types and exercises several CREATE TABLE/ ALTER TABLE DDL constructs.
-- Also regularly verifying spock.tables 

-- Prepared statement for spock.tables so that we can execute it frequently in the script below
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname = $1 ORDER BY relid;

-- Create a table for employee details with various data types
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hire_date DATE,
    birth_time TIME WITHOUT TIME ZONE,
    salary NUMERIC(10, 2),
    full_time BOOLEAN DEFAULT TRUE,
    street_address TEXT,
    metadata JSON,
    start_timestamp TIMESTAMP WITHOUT TIME ZONE,
    emp_coordinates POINT,
    CONSTRAINT chk_salary CHECK (salary > 0)
);

-- Insert initial data into employees table
INSERT INTO employees (emp_id, first_name, last_name, email, hire_date, birth_time, salary, full_time, street_address, metadata, start_timestamp, emp_coordinates) VALUES
(1, 'John', 'Doe', 'john.doe@example.com', '2023-01-15', '08:30:00', 60000, TRUE, '123 Main St', '{"department": "HR"}', '2023-01-15 08:30:00', '(10, 20)'),
(2, 'Jane', 'Smith', 'jane.smith@example.com', '2023-03-22', '09:00:00', 65000, FALSE, '456 Elm St', '{"department": "Engineering"}', '2023-03-22 09:00:00', '(30, 40)');

-- Validate the structure, spock.tables catalog table and data
\d employees
EXECUTE spocktab('employees');

-- Create a table for department details
CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    established DATE,
    budget MONEY,
    active BOOLEAN
);

-- Insert initial data into departments table
INSERT INTO departments (dept_id, dept_name, location, established, budget, active) VALUES
(1, 'Human Resources', 'New York', '2010-01-01', '$1000000', TRUE),
(2, 'Engineering', 'San Francisco', '2015-06-15', '$2000000', TRUE);

-- Validate the structure, spock.tables catalog table and data
\d departments
EXECUTE spocktab('departments');

-- Alter table employees to add new columns, modify existing columns, and add constraints
ALTER TABLE employees ADD COLUMN middle_name VARCHAR(100);
ALTER TABLE employees ADD COLUMN dept_id INT;
ALTER TABLE employees ADD CONSTRAINT fk_dept FOREIGN KEY (dept_id) REFERENCES departments (dept_id);
ALTER TABLE employees ALTER COLUMN salary SET NOT NULL;
ALTER TABLE employees RENAME COLUMN street_address TO address;

-- Validate the structure, spock.tables catalog table and data
\d employees
EXECUTE spocktab('employees');

-- Insert additional data with new columns
INSERT INTO employees (emp_id, first_name, middle_name, last_name, email, hire_date, birth_time, salary, full_time, address, metadata, start_timestamp, emp_coordinates, dept_id) VALUES
(3, 'Alice', 'M', 'Brown', 'alice.brown@example.com', '2023-05-10', '07:45:00', 70000, TRUE, '789 Maple St', '{"department": "Engineering"}', '2023-05-10 07:45:00', '(50, 60)', 2),
(4, 'Bob', 'J', 'Johnson', 'bob.johnson@example.com', '2023-02-20', '10:00:00', 62000, FALSE, '101 Pine St', '{"department": "HR"}', '2023-02-20 10:00:00', '(70, 80)', 1);

-- Create more tables to cover various types and constraints
CREATE TABLE projects (
    project_id INT PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    budget NUMERIC(12, 2) CHECK (budget > 0),
    active BOOLEAN,
    metadata JSON
);

-- Insert initial data into projects table
INSERT INTO projects (project_id, project_name, start_date, end_date, budget, active, metadata) VALUES
(1, 'Project Alpha', '2023-01-01', '2023-06-30', 500000.00, TRUE, '{"client": "Client A"}'),
(2, 'Project Beta', '2023-02-15', '2023-12-31', 750000.00, TRUE, '{"client": "Client B"}');

-- Validate the structure, spock.tables catalog table and data
\d projects
EXECUTE spocktab('projects');

-- Create a table for employee projects (many-to-many relationship)
CREATE TABLE employee_projects (
    emp_id INT,
    project_id INT,
    hours_worked NUMERIC(5, 2),
    role VARCHAR(50),
    PRIMARY KEY (emp_id, project_id),
    FOREIGN KEY (emp_id) REFERENCES employees (emp_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id)
);

-- Insert initial data into employee_projects table
INSERT INTO employee_projects (emp_id, project_id, hours_worked, role) VALUES
(1, 1, 120.5, 'Manager'),
(2, 1, 80.0, 'Developer'),
(3, 2, 150.75, 'Lead Developer');

-- Validate the structure, spock.tables catalog table and data
\d employee_projects
EXECUTE spocktab('employee_projects');

-- Create additional tables to cover more data types and constraints
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    price NUMERIC(10, 2),
    stock_quantity INT,
    discontinued BOOLEAN,
    product_description TEXT,
    added TIMESTAMP WITHOUT TIME ZONE,
    updated TIMESTAMPTZ
);

-- Insert initial data into products table
INSERT INTO products (product_id, product_name, price, stock_quantity, discontinued, product_description, added, updated) VALUES
(1, 'Product A', 19.99, 100, FALSE, 'Description of Product A', '2023-01-01 12:00:00', '2023-01-01 12:00:00+00'),
(2, 'Product B', 29.99, 200, TRUE, 'Description of Product B', '2023-02-01 15:00:00', '2023-02-01 15:00:00+00');

-- Validate the structure, spock.tables catalog table and data
\d products
EXECUTE spocktab('products');

-- Alter table products to add and modify columns
ALTER TABLE products ADD COLUMN category VARCHAR(50);
ALTER TABLE products ALTER COLUMN price SET NOT NULL;
ALTER TABLE products ADD CONSTRAINT price_check CHECK (price > 0);

-- Validate the structure, spock.tables catalog table and data
\d products
EXECUTE spocktab('products');

-- Update product data
UPDATE products SET stock_quantity = 150 WHERE product_id = 1;

-- Create additional tables with case-sensitive names and special characters
CREATE TABLE "CaseSensitiveTable" (
    "ID" INT PRIMARY KEY,
    "Name" VARCHAR(50),
    "Value" NUMERIC(10, 2)
);

-- Insert initial data into CaseSensitiveTable
INSERT INTO "CaseSensitiveTable" ("ID", "Name", "Value") VALUES
(1, 'Item One', 123.45),
(2, 'Item Two', 678.90);

-- Validate the structure, spock.tables catalog table and data
\d "CaseSensitiveTable"
EXECUTE spocktab('CaseSensitiveTable');

-- Create table to test various ALTER TABLE operations
CREATE TABLE test_tab1 (
    id UUID PRIMARY KEY,
    data VARCHAR(100)
);

-- Insert initial data into test_tab1
INSERT INTO test_tab1 (id, data) VALUES ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Initial data');

-- Alter table test_tab1 to add, drop, and rename columns
ALTER TABLE test_tab1 ADD COLUMN new_data TEXT;
ALTER TABLE test_tab1 DROP COLUMN new_data;
ALTER TABLE test_tab1 RENAME COLUMN data TO old_data;

-- Validate the structure, spock.tables catalog table and data
\d test_tab1
EXECUTE spocktab('test_tab1');

-- Create table to test more data types and constraints
CREATE TABLE test_tab2 (
    id INT PRIMARY KEY,
    timestamp_col TIMESTAMPTZ,
    interval_col INTERVAL,
    inet_col INET,
    cidr_col CIDR,
    macaddr_col MACADDR,
    bit_col BIT(8),
    varbit_col VARBIT(8),
    box_col BOX,
    circle_col CIRCLE,
    line_col LINE,
    lseg_col LSEG,
    path_col PATH,
    polygon_col POLYGON
);

-- Insert initial data into test_tab2
INSERT INTO test_tab2 (id, timestamp_col, interval_col, inet_col, cidr_col, macaddr_col, bit_col, varbit_col, box_col, circle_col, line_col, lseg_col, path_col, polygon_col) VALUES
(1, '2023-01-01 12:00:00+00', '1 year 2 months', '192.168.1.1', '192.168.0.0/24', '08:00:2b:01:02:03', B'10101010', B'10101010', '((0,0),(1,1))', '<(1,1),1>', '{1,2,3}', '((0,0),(1,1))', '((0,0),(1,1))', '((0,0),(1,1))');

-- Validate the structure, spock.tables catalog table and data
\d test_tab2
EXECUTE spocktab('test_tab2');

-- Create table to test composite and array types
CREATE TABLE test_tab3 (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    int_array INT[],
    text_array TEXT[]
);

-- Insert initial data into test_tab3 
INSERT INTO test_tab3 (id, name, int_array, text_array) VALUES
(1, 'Henry', '{1,2,3}', '{"one","two","three"}'),
(2, 'Isabel', '{4,5,6}', '{"four","five","six"}');

-- Validate the structure, spock.tables catalog table and data
\d test_tab3
EXECUTE spocktab('test_tab3');

-- creating table without primary key to ensure the default repset is default_insert_only
-- and then play around with adding primary key and dropping them to see the repset
-- are set accordingly. 

-- Create the initial table
CREATE TABLE test_tab4 (
    id TEXT,
    data VARCHAR(100)
);

-- Insert initial data into test_tab4
INSERT INTO test_tab4 (id, data) VALUES ('m2eebc99', 'Initial data');
-- Execute prepared statement for the table, repset default_insert_only
EXECUTE spocktab('test_tab4');
-- Alter table to add a primary key on the id column
ALTER TABLE test_tab4 ADD PRIMARY KEY (id);

-- Display the table structure
\d test_tab4
-- Execute prepared statement for the table, repset default
EXECUTE spocktab('test_tab4');

-- Alter table to remove primary key
ALTER TABLE test_tab4 DROP CONSTRAINT test_tab4_pkey;

-- Alter table to add, drop, and rename columns
ALTER TABLE test_tab4 ADD COLUMN new_data TEXT;
ALTER TABLE test_tab4 DROP COLUMN new_data;
ALTER TABLE test_tab4 RENAME COLUMN data TO old_data;

-- Display the table structure
\d test_tab4
-- Execute prepared statement again for the table
EXECUTE spocktab('test_tab4');

-- Alter table to add a primary key on multiple columns
ALTER TABLE test_tab4 ADD PRIMARY KEY (id, old_data);

-- Display the table structure
\d test_tab4
-- Execute prepared statement again for the table
EXECUTE spocktab('test_tab4');

-- Alter table to drop the primary key
ALTER TABLE test_tab4 DROP CONSTRAINT test_tab4_pkey;

-- Display the table structure
\d test_tab4
-- Execute prepared statement again for the table
EXECUTE spocktab('test_tab4');

-- Negative test cases to validate constraints and error handling
-- Attempt to insert a record with a duplicate primary key (should fail)
INSERT INTO employees (emp_id, first_name, last_name, email) VALUES (1, 'Duplicate', 'Entry', 'duplicate@example.com'); -- This should produce a primary key violation error

-- Attempt to insert a record with a negative salary (should fail due to CHECK constraint)
INSERT INTO employees (emp_id, first_name, last_name, email, salary) VALUES (3, 'Negative', 'Salary', 'negative@example.com', -5000); -- This should produce a check constraint violation error

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
