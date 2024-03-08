## SYNOPSIS
    ./pgedge cluster COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     define-remote       # Create a template for a json config file for a remote cluster.
     init                # Initialize a cluster from json definition file of existing nodes.
     add-db              # Add a database to an existing cluster and cross wire it together.
     remove              # Remove a test cluster from json definition file of existing nodes.
     command             # Run ./pgedge commands on one or all nodes.
     app-install         # Install test application [ pgbench | northwind ].
     app-remove          # Remove test application from cluster.
