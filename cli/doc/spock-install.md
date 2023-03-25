## SYNOPSIS
    ./nodectl spock install <flags>
 
## DESCRIPTION
    Install pgEdge components.
 
## FLAGS
    -U, --User=USER
        Type: Optional[]
        Default: None
    -P, --Password=PASSWORD
        Type: Optional[]
        Default: None
    -d, --database=DATABASE
        Type: Optional[]
        Default: None
    -l, --location=LOCATION
        Type: Optional[]
        Default: None
    --port=PORT
        Default: 5432
    --pgV=PGV
        Default: pg15
    -a, --autostart=AUTOSTART
        Default: True
    --with_patroni=WITH_PATRONI
        Default: False
    --with_cat=WITH_CAT
        Default: False
    --with_bouncer=WITH_BOUNCER
        Default: False
    --with_backrest=WITH_BACKREST
        Default: False
    --with_postgrest=WITH_POSTGREST
        Default: False
