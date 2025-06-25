
## SYNOPSIS
    ./pgedge setup <flags>

## DESCRIPTION
    Install a pgEdge node (including PostgreSQL, spock, and snowflake-sequences).

Example: ./pgedge setup -U admin -P passwd -d defaultdb --pg_ver 16

## FLAGS
    -U, --User=USER
        The database user that will own the db (required)
    
    -P, --Passwd=PASSWD
        The password for the newly created db user (required)
    
    -d, --dbName=DBNAME
        The database name (required)
    
    --port=PORT
        Defaults to 5432 if not specified
    
    --pg_data=PG_DATA
        The data directory to use for PostgreSQL. Must be an absolute path. Defaults to data/pgV, relative to where the CLI is installed
    
    --pg_ver=PG_VER
        Defaults to latest prod version of pg, such as 16.  May be pinned to a specific pg version such as 16.4
    
    -s, --spock_ver=SPOCK_VER
        Defaults to latest prod version of spock, such as 4.0.  May be pinned to a specific spock version such as 4.0.1
    
    -a, --autostart=AUTOSTART
        Defaults to False
    
    -i, --interactive=INTERACTIVE
        Defaults to False
    
    -y, --yes=YES
        Accept input parms without prompting to confirm (always set to True when interactive is false)
    
