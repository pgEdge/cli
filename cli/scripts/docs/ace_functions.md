## ACE Functions

ACE provides functions that compare the data from one object to the data on other object, and optionally repairs the differences it finds.  ACE functions include:

| Command | Description |
|---------|-------------|
| [ACE table-diff](#ace-table-diff) | Compare two tables to identify differences |
| [ACE repset-diff](#ace-repset-diff) | Compare two replication sets to identify differences | 
| [ACE schema-diff](#ace-schema-diff) | Compare two schemas to identify differences |
| [ACE spock-diff](#ace-spock-diff) | Compare two sets of spock meta-data to identify differences |
| [ACE table-repair](#ace-table-repair) | Repair data inconsistencies identified by the table-diff module. |
| [ACE table-rerun](#ace-table-rerun) | Rerun a diff to confirm that a fix has been correctly applied |


### ACE table-diff

Use the `table-diff` command to compare the tables in a cluster and produce a csv or json report showing any differences.  

The syntax is:

`$ ./pgedge ace table-diff cluster_name schema.table_name`

* `cluster_name` is the name of the cluster in which the table resides.
* `schema.table_name` is the schema-qualified name of the table that you are comparing across cluster nodes.

**Optional Arguments**

Include the following optional arguments to customize ACE table-diff behavior:

* `--dbname` is a string value that specifies the database name (defaults to first database in cluster config).
* `--block-rows` is an integer value that specifies the number of rows to process per block.
    - Min: 1000
    - Max: 100000
    - Default: 10000
    - Higher values improve performance but increase memory usage
    - This is a configurable parameter in ace_config.py
* `--max-cpu-ratio` is a float value that specifies the maximum CPU utilisation; the accepted range is 0.0-1.0.  The default is 0.6.
    - Configurable in ace_config.py
* `--batch-size` is an integer value that specifies the number of blocks to process per multiprocessing worker (default: 1)
    - The higher the number, the lower the parallelism
    - Configurable in ace_config.py
* `--output` specifies the output type;choose from `json` or `csv` when including the `--output` parameter to select the output type for a difference report. By default, the report written to `diffs/<YYYY-MM-DD>/diffs_<HHMMSSmmmm>.json`. If the output mode is CSV, then ACE will generate coloured diff files to highlight differences.
* `--nodes` specifies a comma-delimited subset of nodes on which the command will be executed. ACE allows up to a three-way node comparison. Simultaneously comparing more than three nodes at once is not recommended.
* `--quiet` suppresses messages about sanity checks and the progress bar in `stdout`. If ACE encounters no differences, ACE will exit without messages. Otherwise, it will print the differences to JSON in `stdout` (without writing to a file).
* `--table-filter` is a SQL WHERE clause that allows you to filter rows for comparison.

**ACE table-diff Command Examples**

The following command compares a table across all nodes:
```bash
./pgedge ace table-diff my_cluster public.customers
```

The following command compares specific nodes with a custom block size:
```bash
./pgedge ace table-diff my_cluster public.orders --nodes="node1,node2" --block-rows=50000
```

The following command generates an HTML report with filtered data:
```bash
./pgedge ace table-diff my_cluster public.transactions \
  --output=html \
  --table-filter="created_at > '2024-01-01'"
```

### ACE repset-diff

Use the `repset-diff` command to loop through the tables in a replication set and produce a csv or json report showing any differences.  The syntax is:

`$ ./pgedge ace repset-diff cluster_name repset_name`

* `cluster_name` is the name of the cluster in which the replication set is a member.
* `repset_name` is the name of the replication set in which the tables being compared reside.
* `--max_cpu_ratio` specifies the percentage of CPU power you are allotting for use by ACE. A value of `1` instructs the server to use all available CPUs, while `.5` means use half of the available CPUs. The default is `.6` (or 60% of the CPUs).
* `--block_rows` specifies the number of tuples to be used at a time during table comparisons. If `block_rows` is set to `1000`, then a thousand tuples are compared per job across tables. 
* `--output` specifies the output type;choose from `json` or `csv` when including the `--output` parameter to select the output type for a difference report. By default, the report written to `diffs/<YYYY-MM-DD>/diffs_<HHMMSSmmmm>.json`.
* `--nodes` specifies a comma-delimited list of nodes on which the command will be executed.

### ACE schema-diff

Use the `schema-diff` command to compare the schemas in a cluster and produce a csv or json report showing any differences.  The syntax is:

`$ ./pgedge ace schema-diff cluster_name node_one node_two schema_name --output=json|csv`

* `cluster_name` is the name of the cluster in which the table resides.
* `node_one` is the name of the node on which the schema you are comparing resides; you will be comparing the schema to the same schema on `node_two`.
* `schema_name` is the name of the schema you will be comparing.
* `output` specifies the output type;choose from `json` or `csv` when including the `--output` parameter to select the output type for a difference report. By default, the report written to `diffs/<YYYY-MM-DD>/diffs_<HHMMSSmmmm>.json`.

### ACE spock-diff

Use the `spock-diff` command to compare the meta-data on two cluster nodes, and produce a csv or json report showing any differences.  The syntax is:

`$ ./pgedge ace spock-diff cluster_name node_one node_two --output=json|csv`

* `cluster_name` is the name of the cluster in which the table resides.
* `node_one` is the name of the node you will be comparing to `node_two`.
* `output` specifies the output type;choose from `json` or `csv` when including the `--output` parameter to select the output type for a difference report. By default, the report written to `diffs/<YYYY-MM-DD>/diffs_<HHMMSSmmmm>.json`.


### ACE table-repair

The `ACE table-repair` function fixes data inconsistencies identified by the table-diff module. ACE table-repair uses a specified node as the source of truth to correct data on other nodes. The function has a number of safety and audit features that you should consider before invoking the command:

* **Dry Run Mode**: Test repairs without making changes
* **Report Generation**: Detailed repair audit trail of all changes made
* **Upsert-Only Option**: Prevent data deletion
* **Transaction Safety**: All changes are atomic. If, for some reason your repair fails midway, the entire transaction will be rolled back, and no changes will be made to the database.

Please note that:

1. Table-repair is meant to be used to repair differences that arise from spock exceptions, network partitions, temporary node outages, etc. If the 'blast radius' of the failure event is too large -- say, millions of records across several tables, even though table-repair can handle this, we recommend that instead you do a dump and restore using PostgreSQL tooling.
2. Table-repair can only repair rows found in the diff file. If your diff exceeds `MAX_ALLOWED_DIFFS`, table-repair will only be able to partially repair the table.  This may even be desirable if you want to repair the table in batches; perform a `diff->repair->diff->repair` cycle until no more differences are reported.
3. Invoke `ACE table-repair` with `--dry-run` first to review proposed changes.
4. Use `--upsert-only` or `--insert-only` for critical tables where data deletion may be risky.
5. Verify your table structure and constraints before repair.

The command syntax is:

```bash
./pgedge ace table-repair <cluster_name> <schema.table_name> --diff-file=<diff_file> --source-of-truth=<source_of_truth> [options]
```

* `cluster_name` is the name of the cluster in which the table resides.
* `diff_file` is the path and name of the file that contains the table differences.
* `schema.table_name` is the schema-qualified name of the table that you are comparing across cluster nodes.

**Optional Arguments**
* `--dry_run` - Include this option to perform a test application of the differences between the source_of_truth and the other nodes in the cluster. The default is `false`.
* `--upsert_only` (or `-u`) - Set this option to `true` to specify that ACE should make only additions to the *non-source of truth nodes*, skipping any `DELETE` statements that may be needed to make the data match. This option does not guarantee that nodes will match when the command completes, but can be usful if you want to merge the contents of different nodes. The default value is `false`. 
* `--generate_report` (or `-g`) - Set this option to true to generate a .json report of the actions performed;  
Reports are written to files identified by a timestamp in the format: `reports/<YYYY-MM-DD>/report_<HHMMSSmmmm>`.json. The default is `false`.
* `--source-of-truth` is a string value specifying the node name to use as the source of truth for repairs. Note: if you are not using the `--bidirectional` option or the `--fix-nulls` option, you must specify the source of truth node for all other kinds of repairs.
* `--dbname` is a string value that specifies the database name (defaults to first database in cluster config).
* `--dry-run` is a boolean value that simulates repair operations without making changes (default: false).
* `--quiet` is a boolean value that suppresses non-essential output.
* `--generate-report` is a boolean value that instructs the server to create a detailed report of repair operations.
* `--upsert-only` is a boolean value that instructs the server to only perform inserts/updates, and skip deletions.
* `--insert-only` is a boolean value that instructs the server to only perform inserts, and skip updates and deletions. Note: This option uses `INSERT INTO ... ON CONFLICT DO NOTHING`. So, if there are identical rows with different values, this option alone is not enough to fully repair the table.
* `--bidirectional` is a boolean value that must be used with `--insert-only`. Similar to `--insert-only`, but inserts missing rows in a bidirectional manner. For example, if you specify `--bidirectional` for a repair in a case where node A has records with IDs 1, 2, 3 and node B has records with IDs 2, 3, 4, the repair will ensure that both node A and node B have records with IDs 1, 2, 3, and 4.
- `--fix-nulls` is a boolean value that instructs the server to fix NULL values by comparing values across nodes.  For example, if you have an issue where a column is not being replicated, you can use this option to fix the NULL values on the target nodes. This does not need a source of truth node as it consults the diff file to determine which rows have NULL values. However, it should be used for this special case only, and should not be used for other types of data inconsistencies.

**ACE table-repair Command Examples**

The following command performs a basic repair using a diff file:
```bash
./pgedge ace table-repair my_cluster /path/to/diff.json primary public.customers
```

The following command performs a dry run and generates a report:
```bash
./pgedge ace table-repair my_cluster /path/to/diff.json primary public.orders \
  --dry-run=True \
  --generate-report=True
```

The following command repairs update statements only:
```bash
./pgedge ace table-repair my_cluster public.transactions \
  --diff-file=/path/to/diff.json \
  --source-of-truth=primary \
  --upsert-only=True
```

The following command performs a unidirectional insert-only repair. If you had a situation where node 2 is missing some records from node 1, you can use the `--insert-only` option to insert the missing records from node 1 to node 2.
```bash
./pgedge ace table-repair my_cluster public.transactions \
  --diff-file=/path/to/diff.json \
  --source-of-truth=primary \
  --insert-only=True
```

The following command performs a bidirectional insert-only repair.  If you have a network partition between node 1 and node 2, and they each separately received new records, you can use the `--bidirectional` option to insert the missing records from node 1 to node 2 and vice versa.
```bash
./pgedge ace table-repair my_cluster public.transactions \
  --diff-file=/path/to/diff.json \
  --source-of-truth=primary \
  --bidirectional=True
```

**ACE table-repair Report Example**

```json
{
  "time_stamp": "08/07/2024, 13:20:19",
  "arguments": {
    "cluster_name": "demo",
    "diff_file": "diffs/2024-08-07/diffs_131919688.json",
    "source_of_truth": "n1",
    "table_name": "public.acctg_diff_data",
    "dbname": null,
    "dry_run": false,
    "quiet": false,
    "upsert_only": false,
    "generate_report": true
  },
  "database": "lcdb",
  "changes": {
    "n2": {
      "upserted_rows": [],
      "deleted_rows": [],
      "missing_rows": [
        {
          "employeeid": 1,
          "employeename": "Carol",
          "employeemail": "carol@example.com"
        },
        {
          "employeeid": 2,
          "employeename": "Bob",
          "employeemail": "bob@example.com"
        }
      ]
    }
  },
  "run_time": 0.1
}
```

Within the report:

* `time_stamp` displays when the function was called. 
* `arguments` lists the syntax used when performing the repair. 
* `database` identifies the database the function connected to. 
* `runtime` tells you how many seconds the function took to complete.

The `changes` property details the differences found by ACE on each node of your cluster. The changes are identified by node name (for example, `n2`) and by type:

* The `upserted_rows` section lists the rows upserted. Note that if you have specified `UPSERT only`, the report will include those rows in the `missing_rows` section.
* The `deleted_rows` section lists the rows deleted on the node.
* The `missing_rows` section lists the rows that were missing from the node. You will need to manually add any missing rows to your node.


### ACE table-rerun

The table-rerun function allows you to rerun a previous table-diff operation to verify fixes or check if inconsistencies persist after repairs.  When using ACE table-rerun, you should:

* Include the `hostdb` processing option for very large tables and diffs to improve performance.
* Compare results using the original diff file to confirm that differences were resolved after a replication lag window.

 The syntax is:

`$ ./pgedge ace table-rerun <cluster_name> schema.table_name --diff_file=/path/to/diff_file.json`

* `cluster_name` is a string value that specifies the name of the cluster as defined in your configuration.
* `schema.table_name` is a string value that specifies the fully qualified table name (e.g., "public.users")'.
* `diff_file` is a string value that specifies the path to the JSON diff file from a previous table-diff operation.

**Optional Arguments**

* `--dbname` is a string value that specifies the database name; this defaults to the first database in the cluster config file.
* `--quiet` is a boolean value that suppresses non-essential output.
* `--behavior`is a string value that specifies the processing behavior [`multiprocessing` or `hostdb`]; the default is `multiprocessing`.  `multiprocessing` uses parallel processing for faster execution while `hostdb` uses the host database to create temporary tables for faster comparisons (useful for very large tables and diffs).

**ACE table-rerun Command Examples**

To perform a basic rerun of a previous diff:
```bash
./pgedge ace table-rerun my_cluster public.customers \
  --diff-file=/path/to/diff.json
```

To rerun larger diff files using temporary tables:
```bash
./pgedge ace table-rerun my_cluster public.orders \
  --diff-file=/path/to/diff.json \
  --behavior=hostdb
```


