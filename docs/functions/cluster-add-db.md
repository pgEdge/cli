
SYNOPSIS
    ./pgedge cluster add-db CLUSTER_NAME DATABASE_NAME USERNAME PASSWORD

DESCRIPTION
    This command creates a new database in the cluster, installs spock, and sets up all spock nodes and subscriptions.

POSITIONAL ARGUMENTS
    CLUSTER_NAME
        The name of the cluster where the database should be added.
    DATABASE_NAME
        The name of the new database.
    USERNAME
        The name of the user that will be created and own the database.
    PASSWORD
        The password for the new user.
