# PGEDGE CTL SECURE
Secure interface to pgEdge Cloud

## Synopsis
    ./ctl secure  <command> [parameters] [options]   

COMMANDS
[**config**](doc/secure-config.md)                         - Login with a pgEdge Cloud Account<br>
[**list-cloud-acct**](doc/secure-list-cloud-acct.md)       - List all cloud account ids in a pgEdge Cloud Account<br>
[**list-clusters**](doc/secure-list-clusters.md)           - List all clusters in a pgEdge Cloud Account<br>
[**cluster-status**](doc/secure-cluster-status.md)         - Return info on a cluster in a pgEdge Cloud Account<br>
[**list-nodes**](doc/secure-list-nodes.md)                 - List all nodes in a pgEdge Cloud Account cluster<br>
[**import-cluster-def**](doc/secure-import-cluster-def.md) - Enable cluster commands on a pgEdge Cloud Cluster<br>
[**get-cluster-id**](doc/secure-get-cluster-id.md)         - Return the cluster id based on a cluster display name<br>
[**get-node-id**](doc/secure-get-node-id.md)               - Return the node id based on cluster and node display name<br>
[**push-metrics**](doc/secure-push-metrics.md)             - Coming Soon: push pgEdge Metrics to a specified target<br>
[**create-cluster**](doc/secure-create-cluster.md)         - Create a new Cloud Cluster based on json file<br>
[**destroy-cluster**](doc/secure-destroy-cluster.md)       - Delete a pgEdge Cloud Cluster<br>

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

