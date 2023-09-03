## SYNOPSIS
    ./nodectl cluster COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     local-create        # Create a localhost test cluster of N pgEdge nodes on different ports.
     local-destroy       # Stop and then nuke a localhost cluster.
     remote-init         # Initialize a test cluster from json definition file of existing nodes.
     remote-reset        # Reset a test cluster from json definition file of existing nodes.
     remote-import-def   # Import a cluster definition file so we can work with it like a pgEdge cluster.
     command             # Run ./nodectl commands on one or all nodes.
     app-install         # Install test application [ pgbench | northwind ].
     app-remove          # Remove test application from cluster.
