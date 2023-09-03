## SYNOPSIS
    ./nodectl cluster local-create CLUSTER_NAME NUM_NODES <flags>
 
## DESCRIPTION
    Create a localhost test cluster of N pgEdge nodes on different ports.
 
## POSITIONAL ARGUMENTS
    CLUSTER_NAME
    NUM_NODES
 
## FLAGS
    --pg=PG
        Default: 16
    -a, --app=APP
        Type: Optional[]
        Default: None
    --port1=PORT1
        Default: 6432
    -U, --User=USER
        Default: lcusr
    -P, --Passwd=PASSWD
        Default: lcpasswd
    -d, --db=DB
        Default: lcdb
