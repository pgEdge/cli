## SYNOPSIS
    ./ctl spock replicate-ddl REPLICATION_SETS SQL_COMMAND DB <flags>
 
## DESCRIPTION
    Replicate DDL statement through replication set(s)
REPLICATION_SETS - name of one or more replication sets, eg. default or [default,ddl_sql]
SQL_COMMAND - DDL or other SQL command, NOTE: must specify schema
DB - database name
 
## POSITIONAL ARGUMENTS
    REPLICATION_SETS
    SQL_COMMAND
    DB
 
## FLAGS
    -p, --pg=PG
        Type: Optional[]
        Default: None
