## SYNOPSIS
    ./nodectl spock sub-create SUBSCRIPTION_NAME PROVIDER_DSN DB <flags>
 
## DESCRIPTION
    Create a subscription.
 
## POSITIONAL ARGUMENTS
    SUBSCRIPTION_NAME
    PROVIDER_DSN
    DB
 
## FLAGS
    -r, --replication_sets=REPLICATION_SETS
    --synchronize_structure=SYNCHRONIZE_STRUCTURE
        Default: False
    --synchronize_data=SYNCHRONIZE_DATA
        Default: False
    -f, --forward_origins=FORWARD_ORIGINS
        Default: {}
    -a, --apply_delay=APPLY_DELAY
        Default: 0
    -p, --pg=PG
        Type: Optional[]
        Default: None
