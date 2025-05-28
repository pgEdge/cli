
## SYNOPSIS
    ./pgedge cluster app-install CLUSTER_NAME APP_NAME <flags>

## DESCRIPTION
    Install a test application on all nodes in the cluster. Supported applications include 'pgbench' and 'northwind'. 

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster.
    APP_NAME
        The name of the application to install ('pgbench' or 'northwind').

## FLAGS
    -d, --database_name=DATABASE_NAME
        The name of the database to install the application on. Defaults to the first database in the cluster configuration.
    
    -f, --factor=FACTOR
        The scale factor for 'pgbench'. Defaults to 1.
    
