#LOCAL-CLUSTER

##SYNOPSIS
    ./nc local-cluster COMMAND

##COMMANDS
    COMMAND is one of the following  **bold

     **create**
       Create a local cluster that runs N instances of pgEdge each running PG on a different port.

     **destroy**
       Stop each node of a local-cluster and then delete all of it.

     **command**
       Run './nc' commands on one or 'all' nodes.

=====================================================================

#LOCAL-CLUSTER CREATE

##SYNOPSIS
    ./nc local-cluster create CLUSTER_NAME NUM_NODES <flags>

##DESCRIPTION
    Create a local cluster that runs N instances of pgEdge each running PG on a different port.

##POSITIONAL ARGUMENTS
    CLUSTER_NAME
    NUM_NODES

##FLAGS
    -U, --User=USER
        Default: 'lcusr'
    -P, --Passwd=PASSWD
        Default: 'lcpasswd'
    -d, --db=DB
        Default: 'lcdb'
    --port1=PORT1
        Default: 6432
    --pg=PG
        Default: '15'
    -b, --base_dir=BASE_DIR
        Default: 'cluster'
