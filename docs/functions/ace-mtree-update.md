
## SYNOPSIS
    ./pgedge ace mtree update CLUSTER_NAME TABLE_NAME <flags>

## DESCRIPTION
    Updates an existing Merkle tree.

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
    
    -n, --nodes=NODES
        Comma-separated subset of nodes.
    
    -q, --quiet_mode=QUIET_MODE
        Suppress output.
    
