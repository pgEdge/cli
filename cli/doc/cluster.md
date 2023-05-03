## SYNOPSIS
    ./nodectl cluster COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     create-local        # Create local cluster of N pgEdge nodes on different ports.
     destroy             # Stop and then nuke a cluster
     validate            # Validate a cluster configuration
     init                # Initialize cluster for Spock
     command             # Run ./nodectl commands on one or all nodes.
     app-install         # Install test application [ pgbench | spockbench | bmsql ]
     app-remove          # Remove test application from cluster
