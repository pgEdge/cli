
## SYNOPSIS
    ./pgedge cluster COMMAND

## COMMANDS
    COMMAND is one of the following:
     json-validate       # Validate and update a cluster configuration JSON file.
     json-create         # Create a cluster configuration JSON file based on user input.
     json-template       # Create a template for a cluster configuration JSON file.
     init                # Initialize a cluster via cluster configuration JSON file.
     list-nodes          # List all nodes in the cluster.
     add-node            # Add a new node to a cluster
     remove-node         # Remove a node from a cluster
     replication-begin   # Add all tables to the default replication set on every node.
     replication-check   # Check and display the replication status for a given cluster.
     add-db              # Add a database to an existing pgEdge cluster.
     remove              # Remove a cluster.
     command             # Run './pgedge' commands on one or all nodes in a cluster.
     ssh                 # Establish an SSH session into the specified node of a cluster.
     app-install         # Install a test application on all nodes in the cluster.
     app-remove          # Remove a test application from all nodes in the cluster.
     app-concurrent-index# Create a concurrent index on a table column in a database.
