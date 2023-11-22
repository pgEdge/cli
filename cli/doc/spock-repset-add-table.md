## SYNOPSIS
    ./ctl spock repset-add-table REPLICATION_SET TABLE DB <flags>
 
## DESCRIPTION
    Add a table or tables to replication set
  REPLICATION_SET - name of the existing replication set
  RELATION - name or name pattern of the table(s) to be added to the set
    e.g. '*' for all tables, 'public.*' for all tables in public schema
  DB - database name
  SYNCHRONIZE_DATA - synchronized table data on all related subscribers
  COLUMNS - list of columns to replicate
  ROW_FILTER - row filtering expression
  INCLUDE_PARTITIONS - include all partitions in replication
 
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
