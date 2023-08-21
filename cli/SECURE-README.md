# PGEDGE NODECTL SECURE
SEcure pgEdge Cloud Interface

## Synopsis
    ./nodectl secure  <command> [parameters] [options]   

COMMANDS
[**config**](doc/secure-config.md)                         - Login nodeCtl with a pgEdge Cloud Account
[**list-cloud-acct**](doc/secure-list-cloud-acct.md)       - List all cloud account ids in a pgEdge Cloud Account
[**list-clusters**](doc/secure-list-clusters.md)           - List all clusters in a pgEdge Cloud Account
[**cluster-status**](doc/secure-cluster-status.md)         - Return info on a cluster in a pgEdge Cloud Account
[**list-nodes**](doc/secure-list-nodes.md)                 - List all nodes in a pgEdge Cloud Account cluster
[**import-cluster-def**](doc/secure-import-cluster-def.md) - Enable nodeCtl cluster commands on a pgEdge Cloud Cluster
[**get-cluster-id**](doc/secure-get-cluster-id.md)         - Return the cluster id based on a cluster display name
[**get-node-id**](doc/secure-get-node-id.md)               - Return the node id based on cluster and node display name
[**push-metrics**](doc/secure-push-metrics.md)             - Coming Soon: push pgEdge Metrics to a specified target
[**create-cluster**](doc/secure-create-cluster.md)         - Create a new Cloud Cluster based on json file
[**destroy-cluster**](doc/secure-destroy-cluster.md)       - Delete a pgEdge Cloud Cluster

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

