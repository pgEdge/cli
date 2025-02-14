## SYNOPSIS
    ./pgedge spock COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     node-create         # Define a node for spock.
     node-drop           # Remove a spock node.
     node-alter-location # Set location details for spock node.
     node-list           # Display node table.
     node-add-interface  # Add a new node interface.
     node-drop-interface # Delete a node interface.
     repset-create       # Define a replication set.
     repset-alter        # Modify a replication set.
     repset-drop         # Remove a replication set.
     repset-add-table    # Add table(s) to a replication set.
     repset-remove-table # Remove table from replication set.
     repset-add-seq      # Add a sequence to a replication set.
     repset-remove-seq   # Remove a sequence from a replication set.
     repset-add-partition# Add a partition to a replication set.
     repset-remove-partition# Remove a partition from a replication set.
     repset-list-tables  # List tables in replication sets.
     sub-create          # Create a subscription.
     sub-drop            # Delete a subscription.
     sub-alter-interface # Modify an interface to a subscription.
     sub-enable          # Make a subscription live.
     sub-disable         # Put a subscription on hold and disconnect from provider.
     sub-add-repset      # Add a replication set to a subscription.
     sub-remove-repset   # Drop a replication set from a subscription.
     sub-show-status     # Display the status of the subscription.
     sub-show-table      # Show subscription tables.
     sub-resync-table    # Resynchronize a table.
     sub-wait-for-sync   # Pause until the subscription is synchronized.
     table-wait-for-sync # Pause until a table finishes synchronizing.
     replicate-ddl       # Replicate DDL through replication set(s).
     sequence-convert    # Convert sequence to snowflake sequence.
     health-check        # Check if PG instance is accepting connections.
     metrics-check       # Retrieve advanced DB & OS metrics.
     set-readonly        # Turn PG read-only mode on or off.
