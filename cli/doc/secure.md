## SYNOPSIS
    ./nodectl secure COMMAND
 
## COMMANDS
    COMMAND is one of the following:
     config              # Login nodeCtl with a pgEdge Cloud Account
     list-cloud-acct     # List all cloud account ids in a pgEdge Cloud Account
     list-clusters       # List all clusters in a pgEdge Cloud Account
     cluster-status      # Return info on a cluster in a pgEdge Cloud Account
     list-nodes          # List all nodes in a pgEdge Cloud Account cluster
     import-cluster-def  # Enable nodeCtl cluster commands on a pgEdge Cloud Cluster
     get-cluster-id      # Return the cluster id based on a cluster display name
     get-node-id         # Return the node id based on cluster and node display name
     push-metrics        # Coming Soon: push pgEdge Metrics to a specified target
     create-cluster      # Create a new Cloud Cluster based on json file
     destroy-cluster     # Delete a pgEdge Cloud Cluster
