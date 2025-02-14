## SYNOPSIS
    ./pgedge setup <flags>
 
## DESCRIPTION
    Install pgEdge node (including postgres, spock, and snowflake-sequences)

Example: ./pgedge setup -U user -P passwd -d test --pg_ver 16
 
## FLAGS
    -U, --User=USER
        The database user that will own the db (required)
    
    -P, --Passwd=PASSWD
        The password for the newly created db user (required)
    
    -d, --dbName=DBNAME
        The database name (required)
    
    --port=PORT
        Defaults to 5432 if not specified
    
    --pg_ver=PG_VER
        Defaults to latest prod version of pg, such as 16.  May be pinned to a specific pg version such as 16.1
    
    -s, --spock_ver=SPOCK_VER
        Defaults to latest prod version of spock, such as 3.2.  May be pinned to a specific spock version such as 3.2.4
    
    -a, --autostart=AUTOSTART
        Defaults to False
    
