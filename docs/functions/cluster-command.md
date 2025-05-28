
SYNOPSIS
    ./pgedge cluster command CLUSTER_NAME NODE CMD

DESCRIPTION
    This command executes './pgedge' commands on a specified node or all nodes in the cluster.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster.
    NODE
        The node to run the command on. Can be the node name or 'all'.
    CMD
        The command to run on every node, excluding the beginning './pgedge'.
