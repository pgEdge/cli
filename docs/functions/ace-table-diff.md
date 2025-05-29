
## SYNOPSIS
    ./pgedge ace table-diff CLUSTER_NAME TABLE_NAME <flags>

## DESCRIPTION
    Compare a table across a cluster and produce a report showing any differences.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster where the operation should be performed.
    TABLE_NAME
        Schema-qualified name of the table that you are comparing across cluster nodes.

## FLAGS
    -d, --dbname=DBNAME
        Name of the database. Defaults to the name of the first database in the cluster configuration.
    
    --block_rows=BLOCK_ROWS
        Number of rows to process per block. Defaults to config.BLOCK_ROWS_DEFAULT.
    
    -m, --max_cpu_ratio=MAX_CPU_RATIO
        Maximum CPU utilisation. The accepted range is 0.0-1.0. Defaults to config.MAX_CPU_RATIO_DEFAULT.
    
    -o, --output=OUTPUT
        Output format. Acceptable values are "json", "csv", and "html". Defaults to "json".
    
    -n, --nodes=NODES
        Comma-delimited subset of nodes on which the command will be executed. Defaults to "all".
    
    --batch_size=BATCH_SIZE
        Size of each batch. Defaults to config.BATCH_SIZE_DEFAULT.
    
    -t, --table_filter=TABLE_FILTER
        A SQL WHERE clause that allows you to filter rows for comparison.
    
    -q, --quiet=QUIET
        Whether to suppress output in stdout. Defaults to False.
    
