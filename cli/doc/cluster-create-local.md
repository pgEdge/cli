## SYNOPSIS
    ./nodectl cluster create-local CLUSTER_NAME NUM_NODES <flags>
 
## DESCRIPTION
    Create local cluster of N pgEdge nodes on different ports.
 
## POSITIONAL ARGUMENTS
    CLUSTER_NAME
    NUM_NODES
 
## FLAGS
    -U, --User=USER
        Default: lcusr
    -P, --Passwd=PASSWD
        Default: lcpasswd
    -d, --db=DB
        Default: lcdb
    --port1=PORT1
        Default: 6432
    --pg=PG
        Default: 15
    -a, --app=APP
        Type: Optional[]
        Default: None
