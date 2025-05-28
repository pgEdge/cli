
SYNOPSIS
    ./pgedge ace repset-diff CLUSTER_NAME REPSET_NAME <flags>

DESCRIPTION
    Compare a repset across a cluster and produce a report showing any differences.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster where the operation should be performed.
    REPSET_NAME
        Name of the repset to compare across cluster nodes.

FLAGS
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
    
    -q, --quiet=QUIET
        Whether to suppress output in stdout. Defaults to False.
    
    --skip_tables=SKIP_TABLES
        Comma-deliminated list of tables to skip.
    
    --skip_file=SKIP_FILE
        Path to a file containing a list of tables to skip.
    
