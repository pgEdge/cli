## SYNOPSIS
    ./ctl db create <flags>
 
## DESCRIPTION
    Usage:
    To create a superuser than has access to the whole cluster of db's
       db create -d <db> -U <usr> -P <passwd>

    to create an admin user that owns a specifc tennant database
       db create -I <id>  [-P <passwd>]
 
## FLAGS
    -d, --db=DB
        Type: Optional[]
        Default: None
    -U, --User=USER
        Type: Optional[]
        Default: None
    -P, --Passwd=PASSWD
        Type: Optional[]
        Default: None
    -I, --Id=ID
        Type: Optional[]
        Default: None
    -p, --pg=PG
        Type: Optional[]
        Default: None
