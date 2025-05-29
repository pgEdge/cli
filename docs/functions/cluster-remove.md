
## SYNOPSIS
    ./pgedge cluster remove CLUSTER_NAME <flags>

## DESCRIPTION
    This command removes spock subscriptions and nodes, and stops PostgreSQL on each node.
    If the `force` flag is set to `True`, it will also remove the `pgedge` directory on 
    each node, including the PostgreSQL data directory.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster to remove.

## FLAGS
    -f, --force=FORCE
        If `True`, removes the `pgedge` directory on each node. Defaults to `False`.
    
