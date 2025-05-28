
SYNOPSIS
    ./pgedge ace spock-diff CLUSTER_NAME <flags>

DESCRIPTION
    Compare the spock metadata across a cluster and produce a report showing any differences.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster where the operation should be performed.

FLAGS
    -d, --dbname=DBNAME
        Name of the database. Defaults to the name of the first database in the cluster configuration.
    
    -n, --nodes=NODES
        Comma-delimited subset of nodes on which the command will be executed. Defaults to "all".
    
    -q, --quiet=QUIET
        Whether to suppress output in stdout. Defaults to False.
    
