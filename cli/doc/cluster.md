## SYNOPSIS
    ./nodectl cluster COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     create-local        # Create a localhost test cluster of N pgEdge nodes on different ports.
     create-remote       # Comiing Soon! Create a remote SSH cluster from a cluster json definition file.
     create-cloud        # Coming Soon!  Provision a secure global cluster in the Cloud using your own account.
     destroy             # Stop and then nuke a cluster.
     validate            # Validate a cluster configuration
     init                # Initialize cluster for Spock.
     command             # Run ./nodectl commands on one or all nodes.
     app-install         # Install test application [ pgbench | spockbench | bmsql ].
     app-remove          # Remove test application from cluster.
