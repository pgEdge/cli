## SYNOPSIS
    ./nodectl spock COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     install             # Install pgEdge components.
     validate            # Check pre-reqs for advanced commands.
     tune                # Tune pgEdge components
     node-create         # Define a spock node.
     repset-create       # Define a replication set.
     repset-add-table    # Add a table to a replication set.
     sub-create          # Create a subscription.
     sub-add-repset      # Add a replication set to a subscription.
     sub-show-status     # Display the status of the subcription.
     sub-show-table      # Show the the subscriptions.
     sub-wait-for-sync   # Pause until the subscription is synchronized.
     health-check        # Check if PG instance is accepting connections.
     metrics-check       # Retrieve advanced DB & OS metrics.
