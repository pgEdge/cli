
## SYNOPSIS
    ./pgedge ace repset-diff CLUSTER_NAME REPSET_NAME <flags>

## DESCRIPTION
    Compare a repset across a cluster and produce a report showing any differences.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster where the operation should be performed.
    REPSET_NAME
        Name of the repset to compare across cluster nodes.

## FLAGS
    -d, --dbname=DBNAME
        Name of the database to use. If omitted, defaults to the first database in the cluster configuration.
    
    --block_size=BLOCK_SIZE
        Number of rows to process per block. Defaults to config.DIFF_BLOCK_SIZE.
    
    -m, --max_cpu_ratio=MAX_CPU_RATIO
        Maximum CPU utilisation. The accepted range is 0.0-1.0. Defaults to config.MAX_CPU_RATIO_DEFAULT.
    
    -o, --output=OUTPUT
        Output format. Acceptable values are "json", "csv", and "html". Defaults to "json".
    
    -n, --nodes=NODES
        Comma-separated subset of nodes on which the command will be executed. Defaults to "all".
    
    --batch_size=BATCH_SIZE
        Size of each batch, i.e., number of blocks each worker should process. Defaults to config.DIFF_BATCH_SIZE.
    
    -q, --quiet=QUIET
        Whether to suppress output in stdout. Defaults to False.
    
    --skip_tables=SKIP_TABLES
        Comma-separated list of tables to skip. If omitted, no tables are skipped.
    
    --skip_file=SKIP_FILE
        Path to a file containing a list of tables to skip. If omitted, no tables are skipped.
    
