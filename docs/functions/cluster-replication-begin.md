
## SYNOPSIS
    ./pgedge cluster replication-begin CLUSTER_NAME <flags>

## DESCRIPTION
    Adds all tables in the given database to the default replication set on every node
    in the specified cluster. If no database name is provided, the first database in the cluster
    configuration is used. The function ensures that replication is not configured if auto DDL
    is enabled for the database.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster where the database is located.

## FLAGS
    -d, --database_name=DATABASE_NAME
        The name of the database to replicate. Defaults to None.
    
