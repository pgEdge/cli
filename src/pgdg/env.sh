DEFAULT_PG=13

unset PKMG
unset VER_OS
source getPKMG.sh

unset VER_PG
unset SVC_PG

echo ""
list_pg="96 10 11 12 13"
if [ "$1" == "" ]; then
  num_pg=`sudo ls /var/lib/pgsql | wc -l`
  if [ "$num_pg" == "1" ]; then
    ver_pg=`sudo ls /var/lib/pgsql`
    if [ "$ver_pg" == "9.6" ]; then
      export VER_PG="96"
    else
      export VER_PG=$ver_pg
    fi
  else
    echo "ERROR: You must specifiy the Postgres version when more than one installed"
    return 1
  fi
else
  export VER_PG="$1"
  v=`echo $list_pg | grep -w $VER_PG`
  rc=$?
  if [ ! "$rc" == "0" ]; then
    echo "ERROR: Valid PostgreSQL versions are ($list_pg)."
    return 1
  fi
fi

if [ "$PKMG" == "yum" ]; then
  if [ "$VER_PG" == "96" ]; then
    export SVC_PG=postgresql-9.6
  else
    export SVC_PG=postgresql-$VER_PG
  fi
else
  export SVC_PG=postgresql@$VER_PG-main
fi
