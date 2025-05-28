sh: -c: line 1: unexpected EOF while looking for matching `''
sh: -c: line 2: syntax error: unexpected end of file

SYNOPSIS
    ./pgedge cluster add-node CLUSTER_NAME SOURCE_NODE TARGET_NODE <flags>

DESCRIPTION
    Add a new node to a cluster by performing the following steps:

    1. Validate the cluster and target node JSON configurations.
    2. Configure pgBackRest on the source node, if not already configured.
    3. Install pgEdge on the target node, if required.
    4. Restore the target node from a backup of the source node using pgBackRest.
    5. Configure the target node as a standby replica of the source node.
    6. Promote the target node to a primary once it catches up to the source node.
    7. Configure replication and subscriptions for the new node across the cluster.
    8. Reconfigure pgBackrest on the source and target nodes, if required.
    9. Update the cluster JSON configuration with the new node.

    A target node JSON configuration file must be provided in the same directory from which
    this command is invoked, named '<node_name>.json'.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster to which the node is being added.
    SOURCE_NODE
        The name of the source node from which configurations and data are copied.
    TARGET_NODE
        The name of the new node being added.

FLAGS
    -r, --repo1_path=REPO1_PATH
        The repository path for pgBackRest. If not provided, the source node's configuration is used.
    
    -b, --backup_id=BACKUP_ID
        The ID of the backup to restore from. If not provided, the latest backup is used.
    
    -s, --script=SCRIPT
        A bash script to execute after the target node is added.
    
    -i, --install=INSTALL
        Whether to install pgEdge on the target node. Defaults to True.
    
