
SYNOPSIS
    ./pgedge ace schema-diff CLUSTER_NAME SCHEMA_NAME <flags>

DESCRIPTION
    Compare a schema across a cluster and produce a report showing any differences.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster where the operation should be performed.
    SCHEMA_NAME
        Name of the schema that you are comparing across cluster nodes.

FLAGS
    -n, --nodes=NODES
        Comma-delimited subset of nodes on which the command will be executed. Defaults to "all".
    
    --dbname=DBNAME
        Name of the database. Defaults to the name of the first database in the cluster configuration.
    
    --ddl_only=DDL_ONLY
        If True, only compares DDL differences across nodes.
    
    --skip_tables=SKIP_TABLES
        Comma-delimited list of tables to skip.
    
    --skip_file=SKIP_FILE
        Path to a file containing a list of tables to skip.
    
    -q, --quiet=QUIET
        Whether to suppress output in stdout. Defaults to False.
    
