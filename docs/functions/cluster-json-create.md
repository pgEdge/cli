
SYNOPSIS
    ./pgedge cluster json-create CLUSTER_NAME NUM_NODES DB USR PASSWD <flags>

DESCRIPTION
    Create a cluster configuration JSON file based on user input.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster. A directory with this same name will be created in the cluster directory, and the JSON file will have the same name.
    NUM_NODES
        The number of nodes in the cluster.
    DB
        The database name.
    USR
        The username of the superuser created for this database.
    PASSWD
        The password for the superuser.

FLAGS
    --pg_ver=PG_VER
        The PostgreSQL version of the database.
    
    --port=PORT
        The port number for the primary nodes. Must be between 1 and 65535. Defaults to '5432'.
    
    -f, --force=FORCE
        If True, forces the creation of the JSON file without prompting for user input.
    
