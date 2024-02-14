## SYNOPSIS
    ./pgedge cluster local-create CLUSTER_NAME NUM_NODES <flags>
 
## DESCRIPTION
    Create a local cluster. Each node will be located in the cluster/<cluster_name>/<node_name> directory. Each database will have a different port. 

Example: cluster local-create demo 3 lcusr lcpasswd 16 6432 lcdb
 
## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster.
    NUM_NODES
        The number of nodes in the cluster.
 
## FLAGS
    --pg=PG
        The postgreSQL version of the database.
    
    --port1=PORT1
        The starting port for this cluster. For local clusters, each node will have a port increasing by 1 from this port number.
    
    -U, --User=USER
    
    
    -P, --Passwd=PASSWD
    
    
    -d, --db=DB
        The database name.
    
