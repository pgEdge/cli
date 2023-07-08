## SYNOPSIS
    ./nodectl cluster COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     create-secure       # Coming Soon! Create a secure pgEdge cluster of N nodes.
     create-local        # Create a localhost test cluster of N pgEdge nodes on different ports.
     destroy-local       # Stop and then nuke a localhost cluster.
     init-remote         # Initialize a test cluster from json definition file of existing nodes.
     reset-remote        # Reset a test cluster from json definition file of existing nodes.
     validate            # Validate a cluster configuration
     command             # Run ./nodectl commands on one or all nodes.
     app-install         # Install test application [ pgbench | spockbench | bmsql ].
     app-remove          # Remove test application from cluster.
