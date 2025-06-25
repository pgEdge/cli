
## SYNOPSIS
    ./pgedge ace table-diff CLUSTER_NAME TABLE_NAME <flags>

## DESCRIPTION
    Compare a table across a cluster and produce a report showing differences, if any.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster where the operation should be performed.
    TABLE_NAME
        Schema-qualified name of the table that you are comparing across cluster nodes.

## FLAGS
    -d, --dbname=DBNAME
        Name of the database to use. If omitted, defaults to the first database in the cluster configuration file.
    
    --block_rows=BLOCK_ROWS
        Number of rows to process per block. Defaults to config.DIFF_BLOCK_SIZE.
    
    -m, --max_cpu_ratio=MAX_CPU_RATIO
        Maximum CPU utilisation. The accepted range is 0.0-1.0. Defaults to config.MAX_CPU_RATIO_DEFAULT.
    
    -o, --output=OUTPUT
        Output format. Acceptable values are "json", "csv", and "html". Defaults to "json".
    
    -n, --nodes=NODES
        Comma-separated subset of nodes on which the command will be executed. Defaults to "all".
    
    --batch_size=BATCH_SIZE
        Size of each batch, i.e., number of blocks each worker should process. Defaults to config.DIFF_BATCH_SIZE.
    
    -t, --table_filter=TABLE_FILTER
        Used to compare a subset of rows in the table. Specified as a WHERE clause of a SQL query. E.g., --table-filter="customer_id < 100" will compare only rows with customer_id less than 100.  If omitted, the entire table is compared.
    
    -q, --quiet=QUIET
        Whether to suppress output in stdout. Defaults to False.
    
    -s, --skip_block_size_check=SKIP_BLOCK_SIZE_CHECK
        Skip block size check, and potentially tolerate unsafe block sizes. Defaults to False.
    
    Additional flags are accepted.
