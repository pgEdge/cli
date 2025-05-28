
SYNOPSIS
    ./pgedge cluster init CLUSTER_NAME <flags>

DESCRIPTION
    Initialize a cluster via cluster configuration JSON file by performing the following steps:

    1. Loads the cluster configuration.
    2. Checks SSH connectivity for all nodes.
    3. Installs pgEdge on all nodes.
    4. Configures Spock for replication for all configured databases across all nodes.
    5. Integrates pgBackRest on nodes, if configured.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster to initialize.

FLAGS
    -i, --install=INSTALL
        Whether to install pgEdge on nodes. Defaults to True.
    
