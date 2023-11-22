## SYNOPSIS
    ./ctl spock repset-create SET_NAME DB <flags>
 
## DESCRIPTION
    Define a replication set.
 
## POSITIONAL ARGUMENTS
    SET_NAME
    DB
 
## FLAGS
    --replicate_insert=REPLICATE_INSERT
        Default: True
    --replicate_update=REPLICATE_UPDATE
        Default: True
    --replicate_delete=REPLICATE_DELETE
        Default: True
    --replicate_truncate=REPLICATE_TRUNCATE
        Default: True
    -p, --pg=PG
        Type: Optional[]
        Default: None
