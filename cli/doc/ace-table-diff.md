## SYNOPSIS
    ./ctl ace table-diff CLUSTER_NAME TABLE_NAME <flags>
 
## DESCRIPTION
    Efficiently compare tables across cluster using checksums and blocks of rows.
 
## POSITIONAL ARGUMENTS
    CLUSTER_NAME
    TABLE_NAME
 
## FLAGS
    -b, --block_rows=BLOCK_ROWS
        Default: 10000
    -m, --max_cpu_ratio=MAX_CPU_RATIO
        Default: 0.6
    -o, --output=OUTPUT
        Default: json
    -n, --nodes=NODES
        Default: all
    -d, --diff_file=DIFF_FILE
        Type: Optional[]
        Default: None
