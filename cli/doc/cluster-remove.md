## SYNOPSIS
    ./pgedge cluster remove CLUSTER_NAME
 
## DESCRIPTION
    Remove a cluster. This will stop postgres on each node, and then remove the pgedge directory on each node.
This command requires a JSON file with the same name as the cluster to be in the cluster/<cluster_name>. 

Example: cluster remove demo 
 
## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster.
