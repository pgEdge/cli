## SYNOPSIS
    ./nodectl spock db-create <flags>
 
## DESCRIPTION
    Edit Checks:
    if -I specified:
       -P is required
       -U = u-<ID>
       -d = d-<ID>

    if -U specified:
      -I must be None
      -d must be specified
      if -P == None
         user must already exist

 Usage:
     spock db-createdb -d <db> [-U <usr> -P <passwd>]
     spock db-createdb -I <id>  -P <passwd>
 
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
