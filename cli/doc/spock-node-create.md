## SYNOPSIS
    ./nodectl spock node-create NODE_NAME DSN DB <flags>
 
## DESCRIPTION
    Create a spock node
    NODE_NAME - name of the new node, only one node is allowed per database
    DSN - connection string to the node, for nodes that are supposed to be providers, this should be reachable from outside
    DB - database
 
## POSITIONAL ARGUMENTS
    NODE_NAME
    DSN
    DB
 
## FLAGS
    -p, --pg=PG
        Type: Optional[]
        Default: None
