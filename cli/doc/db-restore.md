## SYNOPSIS
    ./ctl db restore OBJECT TARGET_DSN <flags>
 
## DESCRIPTION
    object: database.schema.object where schema and object can contain wildcard '*'
target_dsn: host=x, port=x, username=x, database=x (in any order)
file: location and file name for dump
 
## POSITIONAL ARGUMENTS
    OBJECT
    TARGET_DSN
 
## FLAGS
    -f, --file=FILE
        Default: /tmp/db_0.sql
    -p, --pg=PG
        Type: Optional[]
        Default: None
