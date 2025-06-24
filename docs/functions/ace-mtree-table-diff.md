
## SYNOPSIS
    ./pgedge ace mtree table-diff CLUSTER_NAME TABLE_NAME <flags>

## DESCRIPTION
    Compares Merkle trees of a table across cluster nodes.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster.
    TABLE_NAME
        Schema-qualified table name.

## FLAGS
    -d, --dbname=DBNAME
        Name of the database.
    
    -r, --rebalance=REBALANCE
        Trigger rebalancing of the tree.
    
    -m, --max_cpu_ratio=MAX_CPU_RATIO
        Max CPU for parallel operations.
    
    -b, --batch_size=BATCH_SIZE
        Number of blocks per worker batch.
    
    -n, --nodes=NODES
        Comma-separated subset of nodes.
    
    -o, --output=OUTPUT
        Output format (json, csv, html).
    
    -q, --quiet_mode=QUIET_MODE
        Suppress output.
    
