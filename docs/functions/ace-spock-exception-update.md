
## SYNOPSIS
    ./pgedge ace spock-exception-update CLUSTER_NAME NODE_NAME ENTRY <flags>

## DESCRIPTION
    Update the Spock exception status for a specified cluster and node.

## POSITIONAL ARGUMENTS
    CLUSTER_NAME
        Name of the cluster where the operation should be performed.
    NODE_NAME
        The name of the node within the cluster where the update should be performed.
    ENTRY
        A JSON string representing the exception entry. Should contain the following keys.
    
        - "remote_origin" (str) transaction that caused the exception. (Required)
    
        - "remote_commit_ts" (str) transaction on the remote origin. (Required)
    
        - "remote_xid" (str) (Required)
    
        - "status" (str) "RESOLVED", "IGNORED"). (Required)
    
        - "resolution_details" (dict, optional) dictionary containing details about the resolution.
    
        - "command_counter" (int, optional) exception detail (matching this command_counter along with remote_origin, remote_commit_ts, remote_xid) in the `spock.exception_status_detail` table is updated. If omitted, the main entry in `spock.exception_status` and all related detail entries for the (remote_origin, remote_commit_ts, remote_xid) trio in `spock.exception_status_detail` are updated.

## FLAGS
    -d, --dbname=DBNAME
        Name of the database. Defaults to the name of the first database in the cluster configuration.
    
