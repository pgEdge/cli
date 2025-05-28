
SYNOPSIS
    ./pgedge cluster json-template CLUSTER_NAME DB NUM_NODES USR PASSWD PG PORT

DESCRIPTION
    Create a template for a cluster configuration JSON file.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster. A directory with this name will be created in the cluster directory, and the JSON file will have the same name.
    DB
        The database name.
    NUM_NODES
        The number of nodes in the cluster.
    USR
        The username of the superuser created for this database.
    PASSWD
        The password for the above user.
    PG
        The PostgreSQL version of the database.
    PORT
        The port number for the database.
