
## SYNOPSIS
    ./pgedge ace mtree teardown CLUSTER_NAME <flags>

## DESCRIPTION
    Removes Merkle tree objects.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster.

## FLAGS
    -t, --table_name=TABLE_NAME
        Schema-qualified table name. If omitted, removes objects for the entire database.
    
    -d, --dbname=DBNAME
        Name of the database.
    
    -n, --nodes=NODES
        Comma-separated subset of nodes.
    
    -q, --quiet_mode=QUIET_MODE
        Suppress output.
    
