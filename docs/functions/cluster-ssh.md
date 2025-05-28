
SYNOPSIS
    ./pgedge cluster ssh CLUSTER_NAME NODE_NAME

DESCRIPTION
    This command connects to a node within a cluster using SSH. It validates 
the cluster configuration, retrieves the node's IP address, and executes 
the SSH command with the appropriate credentials.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster containing the node.
    NODE_NAME
        The name of the node to connect to.
