
## SYNOPSIS
    ./pgedge ace table-rerun CLUSTER_NAME DIFF_FILE TABLE_NAME <flags>

## DESCRIPTION
    Reruns a table diff operation based on a previous diff file.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster where the operation should be performed.
    DIFF_FILE
        Path to the diff file from a previous table diff operation.
    TABLE_NAME
        Schema-qualified name of the table that you are comparing across cluster nodes.

## FLAGS
    -d, --dbname=DBNAME
        Name of the database. Defaults to the name of the first database in the cluster configuration.
    
    -q, --quiet=QUIET
        Whether to suppress output in stdout. Defaults to False.
    
    -b, --behavior=BEHAVIOR
        The rerun behavior, either "multiprocessing" or "hostdb". "multiprocessing" uses parallel processing for faster execution. "hostdb" uses the host database to create temporary tables for faster comparisons. Defaults to "multiprocessing".
    
