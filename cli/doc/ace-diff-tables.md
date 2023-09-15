## SYNOPSIS
    ./nodectl ace diff-tables CLUSTER_NAME <flags>
 
## DESCRIPTION
    Efficiently compare tables across cluster using optional checksums and blocks of rows.
 
## POSITIONAL ARGUMENTS
    CLUSTER_NAME
 
## FLAGS
    -t, --table_name=TABLE_NAME
        Type: Optional[]
        Default: None
    -r, --rep_set=REP_SET
        Type: Optional[]
        Default: None
    -c, --checksum_use=CHECKSUM_USE
        Default: False
    -b, --block_rows=BLOCK_ROWS
        Default: 1
    -m, --max_cpu_ratio=MAX_CPU_RATIO
        Default: 0.6
