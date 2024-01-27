## SYNOPSIS
    ./pgedge cluster COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     define-localhost    # Create a json config file for a local cluster.
     define-remote       # Create a template for a json config file for a remote cluster.
     local-create        # Create a localhost test cluster of N pgEdge nodes on different ports.
     local-destroy       # Stop and then nuke a localhost cluster.
     init                # Initialize a cluster from json definition file of existing nodes.
     remove              # Remove a test cluster from json definition file of existing nodes.
     command             # Run ./pgedge commands on one or all nodes.
     app-install         # Install test application [ pgbench | northwind ].
     app-remove          # Remove test application from cluster.
