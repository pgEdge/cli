#!/bin/bash
cd "$(dirname "$0")"

source versions.sh


function build {
  pgbin="--with-pgbin /opt/pgcomponent/pg$pgV"
  pgver="--with-pgver $3"
  src="$SOURCE/$1-$2.tar.gz"
  echo ""
  echo "###################################"
  cmd="./build-component.sh --build-$1 $src $pgbin $pgver $copyBin $4"
  echo "cmd=$cmd"
  $cmd
  rc=$?
}


################### MAINLINE #####################

pgV="$2"
copyBin="$3"
if [ "$copyBin" == "" ]; then
  copyBin="--no-copy-bin"
fi
if [[ "$pgV" < "12" ]] || [[ "$pgV" > "17" ]]; then
  echo  "ERROR: second parm must be 12 thru 17"
  exit 1
fi


if [ "$1" == "vector" ]; then
  build vector $vectorFullV $2 vector
fi

if [ "$1" == "plv8" ]; then
  build plv8 $plv8FullV $2 plv8
fi

if [ "$1" == "pldebugger" ]; then
  build pldebugger $debugFullV $2 pldebugger
fi

if [ "$1" == "hintplan" ]; then
  if [ "$pgV" == "17" ]; then
    build hintplan $hintplan17V $2 hintplan
  elif [ "$pgV" == "16" ]; then
    build hintplan $hintplan16V $2 hintplan
  elif [ "$pgV" == "15" ]; then
    build hintplan $hintplan15V $2 hintplan
  fi
fi

if [ "$1" == "decoderbufs" ]; then
  build decoderbufs $decoderbufsFullV $2 decoderbufs
fi

if [ "$1" == "backrest" ]; then
  build backrest $backrestFullV $2 backrest
fi

if [ "$1" == "citus" ]; then
  build citus $citusFullV $2 citus
fi

if [ "$1" == "multicorn" ]; then
  build multicorn $multicornFullV $2 multicorn 
fi

if [ "$1" == "wal2json" ]; then
  build wal2json $wal2jV $2 wal2json
fi

if [ "$1" == "cron" ]; then
  build cron $cronFullV $2 cron
fi

if [ "$1" == "partman" ]; then
  build partman $partmanFullV $2 partman
fi

if [ "$1" == "setuser" ]; then
  build setuser $setuserFullV $2 setuser  
fi

if [ "$1" == "permissions" ]; then
  build permissions $permissionsFullV $2 permissions
fi

if [ "$1" == "postgis" ]; then
  build postgis $postgisFullV $2 postgis  
fi

if [ "$1" == "audit" ]; then
  if [ "$pgV" == "16" ]; then
    build audit $auditFull16V $2 audit    
  elif [ "$pgV" == "15" ]; then
    build audit $auditFull15V $2 audit    
  fi
fi

if [ "$1" == "orafce" ]; then
  build orafce $orafceFullV $2 orafce
fi

if [ "$1" == "curl" ]; then
  build curl $curlFullV $2 curl
fi

if [ "$1" == "hypopg" ]; then
  build hypopg $hypopgFullV $2 hypopg
fi

if [ "$1" == "plprofiler" ]; then
  build plprofiler $plProfilerFullVersion $2 profiler
fi

if [ "$1" == "timescaledb" ]; then
  build timescaledb $timescaledbFullV $2 timescale
fi

if [ "$1" == "snowflake" ]; then
  build snowflake $snwflkV $2  snowflake
fi

if [ "$1" == "spock40" ]; then
  build spock40 $spock40V $2  spock40
fi

if [ "$1" == "lolor" ]; then
  build lolor $lolorV $2  lolor
fi

if [ "$1" == "spock33" ]; then
  build spock33 $spock33V $2  spock33
fi

if [ "$1" == "ddlx" ]; then
  build ddlx $ddlxFullV $2 ddlx
fi

if [ "$1" == "bouncer" ]; then
  build bouncer $bouncerV $2 bouncer
fi

if [ "$1" == "sqlitefdw" ]; then
  build sqlitefdw $sqlitefdwFullV $2 sqlitefdw
fi

exit 0
