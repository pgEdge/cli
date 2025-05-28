
## SYNOPSIS
    ./pgedge cluster replication-check CLUSTER_NAME <flags>

## DESCRIPTION
    Retrieves the replication status for all nodes in the specified cluster.
    Optionally, it can also display the tables associated with Spock replication sets.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster to check replication status for.

## FLAGS
    -s, --show_spock_tables=SHOW_SPOCK_TABLES
        If True, displays the tables in Spock replication sets. Defaults to False.
    
    -d, --database_name=DATABASE_NAME
        The name of the specific database to check. If not provided, the first database in the cluster configuration will be used.
    
