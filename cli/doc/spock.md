## SYNOPSIS
    ./nodectl spock COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     install             # Install pgEdge components.
     validate            # Check pre-reqs for advanced commands.
     tune                # Tune pgEdge components
     create-node         # Define a spock node.
     create-repset       # Define a replication set.
     create-sub          # Create a subscription.
     repset-add-table    # Add a table to a replication set.
     sub-add-repset      # Add a replication set to a subscription.
     show-sub-status     # Display the status of the subcription.
     show-sub-table      # Show the the subscriptions.
     wait-for-sub-sync   # Pause until the subscription is synchronized.
     health-check        # Check if PG instance is accepting connections.
     metrics-check       # Retrieve advanced DB & OS metrics.
