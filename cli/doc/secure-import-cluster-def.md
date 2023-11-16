## SYNOPSIS
    ./nodectl secure import-cluster-def CLUSTER_ID <flags>
 
## DESCRIPTION
    Import information on a pgEdge Cloud Cluster into a json file for ./nodectl cluster
[ Requires ./nocdectl secure config ]
  CLUSTER_ID - the pgEdge Cloud Cluster ID
  PROFILE - profile name of pgEdge Cloud Account for NodeCTL to use
[ Requires ssh connection to then use ./nodectl cluster commands ]
 
## POSITIONAL ARGUMENTS
    CLUSTER_ID
 
## FLAGS
    -p, --profile=PROFILE
        Default: Default
