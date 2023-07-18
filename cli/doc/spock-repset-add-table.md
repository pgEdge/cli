## SYNOPSIS
    ./nodectl spock repset-add-table REPLICATION_SET TABLE DB <flags>
 
## DESCRIPTION
    Add table(s) to replication set.
 
## POSITIONAL ARGUMENTS
    REPLICATION_SET
    TABLE
    DB
 
## FLAGS
    -s, --synchronize_data=SYNCHRONIZE_DATA
        Default: False
    -c, --columns=COLUMNS
        Type: Optional[]
        Default: None
    -r, --row_filter=ROW_FILTER
        Type: Optional[]
        Default: None
    -i, --include_partitions=INCLUDE_PARTITIONS
        Default: True
    -p, --pg=PG
        Type: Optional[]
        Default: None
