
## SYNOPSIS
    ./pgedge cluster app-concurrent-index CLUSTER_NAME DB_NAME INDEX_NAME TABLE_NAME COL

## DESCRIPTION
    Creates a concurrent index on a specified column of a table in a database 
when auto_ddl is enabled. It ensures the index is created across all
nodes in the cluster.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster where the database resides.
    DB_NAME
        The name of the database where the index will be created.
    INDEX_NAME
        The name of the index to be created.
    TABLE_NAME
        The name of the table on which the index will be created.
    COL
        The column of the table to be indexed.
