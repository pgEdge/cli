
SYNOPSIS
    ./pgedge cluster remove-node CLUSTER_NAME NODE_NAME

DESCRIPTION
    Remove a node from a cluster by performing the following steps:

    1. Load and validate the cluster JSON configuration.
    2. Verify SSH connectivity for all nodes in the cluster.
    3. On other nodes (not being removed), drop any subscriptions that point to the node being removed.
    4. On the node being removed, drop all subscriptions to other nodes and remove spock configuration. 
    5. Stop the node being removed and list the Spock nodes for each database on other nodes.
    6. Remove the node from the cluster configuration JSON file.
    7. Save the updated cluster configuration back to the cluster configuration JSON file.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster from which the node should be removed.
    NODE_NAME
        The name of the node to remove.
