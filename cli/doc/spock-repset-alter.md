## SYNOPSIS
    ./pgedge spock repset-alter SET_NAME DB <flags>
 
## DESCRIPTION
    Alter a replication set. 

Example: spock repset-alter demo_repset demo --replicate_truncate=False
 
## POSITIONAL ARGUMENTS
    SET_NAME
        The name of the replication set. Example: demo_repset
    DB
        The name of the database. Example: demo
 
## FLAGS
    --replicate_insert=REPLICATE_INSERT
        Default: True
        For tables in this replication set, replicate inserts.
    --replicate_update=REPLICATE_UPDATE
        Default: True
        For tables in this replication set, replicate updates.
    --replicate_delete=REPLICATE_DELETE
        Default: True
        For tables in this replication set, replicate deletes.
    --replicate_truncate=REPLICATE_TRUNCATE
        Default: True
        For tables in this replication set, replicate truncate.
    -p, --pg=PG
        Type: Optional[]
        Default: None
