
# AutoDDL Testing Framework 

The AutoDDL testing framework laid out in the `runner.py` program (the regression test runner for the pgEdge CLI), facilitates the automated validation of DDL replication between 2 nodes. This framework encompasses SQL test cases that run on designated nodes and perform validation (of the auto-replicated DDL) on a secondary node. 

Key elements include:

## SQL Tests
Test cases are written in .sql files to cover various DDL constructs. These files are executed via psql on the node specified in its filename (n1 or n2 specified prior to file extension). If no node is specified, n1 is the assumed default. Each test case is comprised of a three-set file structure:
- **a file** (e.g. `6555a_create_alter_table_n1.sql`): Contains the main CREATE and ALTER operations on node n1. With the cluster being in autoDDL mode, all these DDLs will be auto-replicated to n2.
- **b file** (e.g. `6555b_table_validate_n2.sql`): Validates DDL on node n2 as a result of executing the a file on n1, and performs cleanup of replicated tables on n2, exercising the DROP construct, which auto-replicates and cleans up on n1.
- **c file** (e.g. `6555c_table_validate_n1.sql`): Performs final validation on n1 to ensure all tables are dropped.

### General Guidelines for writing SQL tests
When writing SQL tests for the AutoDDL framework, it is important to ensure that the tests produce consistent and reliable outputs. Follow these guidelines to achieve consistency and clarity:

- **Ordering Results**: Include `ORDER BY` clauses in `SELECT` statements to ensure that the result order is consistent across runs.
- **Avoid Serial Types**: Do not use serial or auto-incrementing types, as they can produce different values on each run.
- **Avoid Varying Outputs**: Avoid Functions or operations that generate variable results, such as `CURRENT_TIMESTAMP` or `EXPLAIN` plans.
- **Specific Meta Commands**: Use meta commands (`\d`, `\d+`) specific to the object being described to ensure clear and relevant output. For example, use `\d tablename` instead of just `\d`.
- **Commenting**: Include comments in the SQL files to describe the purpose of each section and the expected outcome. This helps in understanding the test case and the validation process.

## Expected Output Files
Each of these .sql files will have a corresponding expected output file generated manually by executing the SQL files against psql on the intended node.

## Actual Output Files
When these .sql files are executed during the regression run (via runner.py), an actual output file is generated.

## Output Comparison
Expected output files are compared against the actual output generated during test execution. Any differences between the actual and expected outputs result in the test being marked as a failure, and the discrepancies are logged for review.

## Directory Structure
- SQL test files and their expected output files reside in the `t/auto_ddl/` directory. SQL and expected output files share the same name, differing only in their extensions.
- The actual output files are generated in the `/tmp/auto_ddl/` directory, which is cleaned up before each execution.

## auto_ddl_schedule
Comprises setup files (to set up a 2-node cluster with autoDDL enabled), autoDDL tests, and teardown files. Each test assumes there is autoDDL configured between the two node cluster with autoDDL GUCs enabled.

## Enhancements to `runner.py`

To support the above-mentioned test framework, the following enhancements have been made to runner.py:

### .sql File Execution
runner.py can now execute .sql files (specified in a schedule) against a specific node. The SQL files exercise DDL constructs/validation.

### Generating Expected Output Files
To generate the expected output file for a test case, use the following command:
```sql
./psql -X -a -d <db> -p <port> < input.sql > expected_output.out 2>&1
```
Please adjust the port in the command above depending on the node you wish this file to run on.

### Runtime Execution
When you run it, runner.py reads the .sql file from the schedule, executes the sql via psql (constructing its path and switches based on the values defined in config.env), and generates an actual output file. It then compares the expected and actual outputs:
- If they match, the test passes.
- If they do not match, the test fails, and a diff is logged.

# Example: Adding a Set of Tests for CREATE TABLE

To add a set of three tests for `CREATE TABLE` as an example, use the following steps to create the a, b, and c files:

1. **Create SQL Test Files**:
 - `6112a_create_table_n1.sql`:
   ```sql
   -- Prepared statement for spock.tables
   PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname = $1 ORDER BY relid;

   -- Create table with primary key
   CREATE TABLE table_with_pk (
       id INT PRIMARY KEY,
       data TEXT
   );

   -- Insert data into table_with_pk
   INSERT INTO table_with_pk (id, data) VALUES (1, 'data1'), (2, 'data2');

   -- Validate table_with_pk
   \d table_with_pk
   EXECUTE spocktab('table_with_pk'); -- Replication set: default

   -- Create table without primary key
   CREATE TABLE table_without_pk (
       id INT,
       data TEXT
   );

   -- Insert data into table_without_pk
   INSERT INTO table_without_pk (id, data) VALUES (1, 'data1'), (2, 'data2');

   -- Validate table_without_pk
   \d table_without_pk
   EXECUTE spocktab('table_without_pk'); -- Replication set: default_insert_only
   ```
 - `6112b_validate_and_drop_n2.sql` (do the necessary validation on n2 to ensure everything expected auto replicated):
   ```sql
   -- Validate the replicated tables on n2 and drop them
   -- Prepared statement for spock.tables
    PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname = $1 ORDER BY relid;

   -- Validate table_with_pk
   \d table_with_pk
   EXECUTE spocktab('table_with_pk'); -- Replication set: default
   SELECT * FROM table_with_pk ORDER BY id; -- Expected data: (1, 'data1'), (2, 'data2')

   -- Validate table_without_pk
   \d table_without_pk
   EXECUTE spocktab('table_without_pk'); -- Replication set: default_insert_only
   SELECT * FROM table_without_pk ORDER BY id; -- Expected data: (1, 'data1'), (2, 'data2')

   -- Drop tables
   DROP TABLE table_with_pk;
   DROP TABLE table_without_pk;
   ```
 - `6112c_validate_drop_n1.sql` (perform necessary validation on n1 to ensure all of the DROP statements exercised in the b file have been replicated to n1 and all objects are dropped):
   ```sql
   -- Ensure tables are dropped on n1
   -- Prepared statement for spock.tables
    PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname = $1 ORDER BY relid;

   -- Validate table_with_pk does not exist
   \d table_with_pk
   EXECUTE spocktab('table_with_pk'); -- should not exist

   -- Validate table_without_pk does not exist
   \d table_without_pk
   EXECUTE spocktab('table_without_pk'); -- should not exist
   ```

2. **Generate Expected Output Files**:
 Once your sql files are finalised, use the `psql` command to generate the expected output files against a node where the file is intended to run:
```bash 
./psql -X -a -d lcdb -p 6432 < 6112a_create_table_n1.sql > 6112a_create_table_n1.out 2>&1 
./psql -X -a -d lcdb -p 6433 < 6112b_validate_and_drop_n2.sql > 6112b_validate_and_drop_n2.out 2>&1 
./psql -X -a -d lcdb -p 6432 < 6112c_validate_drop_n1.sql > 6112c_validate_drop_n1.out 2>&1
```
Thoroughly review the expected output file to ensure all tests and queries produce consistent outputs. 

3. **Examine the Expected Output**:
   Carefully check the expected output files to ensure they contain the intended results.
   
4. **Add the Test Files to the `t/auto_ddl/` Directory**:
   Place both the SQL files and their expected output files in the `t/auto_ddl/` directory.

5. **Update the Schedule**:
   Add the entries of the .sql files in the `auto_ddl_schedule`, keeping their relative path from the `test` directory.

6. **Execute a Run**:
   Execute the schedule file with runner.py to ensure your tests pass.
   
7. **Commit the Changes**:
   Proceed with committing the relevant .sql and .out files and the updated schedule with a detailed commit message.

By following this structure and example, you can add new AutoDDL test cases to the regression suite, ensuring thorough testing of various database operations and their replication across nodes.
