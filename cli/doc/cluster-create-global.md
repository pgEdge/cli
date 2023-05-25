## SYNOPSIS
    ./nodectl cluster create-global CLUSTER_NAME LOCATIONS USER PASSWD DB <flags>
 
## DESCRIPTION
    Provision a secure cluster in the Cloud using your own account.
 
## POSITIONAL ARGUMENTS
    CLUSTER_NAME
    LOCATIONS
    USER
    PASSWD
    DB
 
## FLAGS
    -c, --cloud=CLOUD
        Default: aws
    -s, --size=SIZE
        Default: Medium
    --pg=PG
        Default: 16
    -a, --app=APP
        Type: Optional[]
        Default: None
    --port=PORT
        Default: 5432
