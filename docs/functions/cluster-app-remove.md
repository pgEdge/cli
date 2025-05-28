
SYNOPSIS
    ./pgedge cluster app-remove CLUSTER_NAME APP_NAME <flags>

DESCRIPTION
    Remove a test application from all nodes in the cluster.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster.
    APP_NAME
        The name of the application to remove ('pgbench' or 'northwind').

FLAGS
    -d, --database_name=DATABASE_NAME
        The name of the database to remove the application from. Defaults to the first database in the cluster configuration.
    
